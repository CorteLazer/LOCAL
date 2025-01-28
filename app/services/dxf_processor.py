import ezdxf
import math
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Arc, Circle


def calculate_perimeter(entity):
    """
    Calcula el perímetro de una entidad (LWPOLYLINE, POLYLINE, ARC, CIRCLE, LINE).
    """
    if entity.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
        points = entity.get_points("xy")
        perimeter = 0.0
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            perimeter += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        # Si la entidad está cerrada, añade la distancia entre el último y el primer punto
        if entity.is_closed:
            x1, y1 = points[-1]
            x2, y2 = points[0]
            perimeter += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return perimeter
    elif entity.dxftype() == "CIRCLE":
        return 2 * math.pi * entity.dxf.radius
    elif entity.dxftype() == "ARC":
        angle = abs(entity.dxf.end_angle - entity.dxf.start_angle)
        return (angle / 360.0) * (2 * math.pi * entity.dxf.radius)
    elif entity.dxftype() == "LINE":
        start = entity.dxf.start
        end = entity.dxf.end
        return math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
    return None


def calculate_area(entity):
    """
    Calcula el área de una entidad cerrada (LWPOLYLINE, POLYLINE o CIRCLE).
    """
    if entity.dxftype() in ["LWPOLYLINE", "POLYLINE"] and entity.is_closed:
        points = entity.get_points("xy")
        area = 0.0
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]  # El siguiente punto, circularmente
            area += x1 * y2 - y1 * x2
        return abs(area) / 2.0
    elif entity.dxftype() == "CIRCLE":
        return math.pi * (entity.dxf.radius ** 2)
    return None


def generate_dxf_plot(file_path, output_image_path="output.png"):
    """
    Genera una visualización del archivo DXF y la guarda como una imagen.
    """
    try:
        # Leer el archivo DXF
        doc = ezdxf.readfile(file_path)
        modelspace = doc.modelspace()

        # Crear la figura y el eje
        fig, ax = plt.subplots(figsize=(10, 10))

        # Iterar sobre las entidades y graficarlas
        for entity in modelspace:
            if entity.dxftype() == "LINE":
                start = entity.dxf.start
                end = entity.dxf.end
                ax.plot([start[0], end[0]], [start[1], end[1]], color="blue", linewidth=1)

            elif entity.dxftype() == "CIRCLE":
                center = entity.dxf.center
                radius = entity.dxf.radius
                circle = Circle((center[0], center[1]), radius, color="green", fill=False)
                ax.add_artist(circle)

            elif entity.dxftype() == "ARC":
                center = entity.dxf.center
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle
                end_angle = entity.dxf.end_angle
                arc = Arc(
                    (center[0], center[1]),
                    2 * radius,  # Ancho del arco
                    2 * radius,  # Alto del arco
                    angle=0,  # Rotación del arco
                    theta1=start_angle,  # Ángulo inicial
                    theta2=end_angle,  # Ángulo final
                    color="orange",
                )
                ax.add_artist(arc)

            elif entity.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
                points = entity.get_points("xy")
                x_coords, y_coords = zip(*points)
                ax.plot(x_coords, y_coords, color="red", linewidth=1)
                if entity.is_closed:
                    ax.plot([x_coords[-1], x_coords[0]], [y_coords[-1], y_coords[0]], color="red", linewidth=1)

        # Configurar los límites y las etiquetas del gráfico
        ax.set_aspect("equal", adjustable="datalim")
        ax.autoscale()
        ax.set_title("Visualización del Archivo DXF")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        # Guardar la imagen
        plt.savefig(output_image_path)
        plt.close(fig)
        return output_image_path
    except Exception as e:
        raise RuntimeError(f"Error al generar la visualización: {str(e)}")


def process_dxf_file(file_path):
    """
    Procesa un archivo DXF para obtener detalles de las entidades y generar una visualización.
    """
    try:
        # Procesar entidades
        doc = ezdxf.readfile(file_path)
        modelspace = doc.modelspace()

        entity_summary = []
        total_entities = 0
        total_perimeter = 0.0

        for entity in modelspace:
            entity_data = {"type": entity.dxftype(), "closed": False, "perimeter": None, "area": None}
            total_entities += 1

            if entity.dxftype() in ["LWPOLYLINE", "POLYLINE", "CIRCLE", "ARC", "LINE"]:
                entity_data["perimeter"] = calculate_perimeter(entity)
                entity_data["area"] = calculate_area(entity)
                if entity.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
                    entity_data["closed"] = entity.is_closed
                elif entity.dxftype() == "CIRCLE":
                    entity_data["closed"] = True

            if entity_data["perimeter"] is not None:
                total_perimeter += entity_data["perimeter"]

            entity_summary.append(entity_data)

        # Generar visualización
        output_image_path = "app/static/visualization.png"
        generate_dxf_plot(file_path, output_image_path)

        return {
            "status": "success",
            "total_entities": total_entities,
            "total_perimeter": total_perimeter,
            "entity_details": entity_summary,
            "visualization_path": output_image_path,
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
        }