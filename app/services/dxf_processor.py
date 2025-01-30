import ezdxf
import math
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Arc, Circle
import os
    
# Diccionarios de precios
Metro_perimetro_corte = {
    "CR18": 2000, "CR16": 2500, "CR14": 3000, "HR14": 2500,
    "HR12": 4000, "HR1/8": 6000, "HR3/16": 7500, "HR1/4": 9000,
    "HR5/16": 12000, "HR3/8": 14000, "HR1/2": 18000, "INOX20": 1800,
    "INOX18": 2100, "INOX16": 2700, "INOX14": 4500, "INOX12": 6000,
    "INOX1/8": 7000, "INOX3/16": 9000, "ALUM1": 2000, "ALUM1,5": 3000,
    "ALUM2,5": 4500, "ALUM3": 6000, "ALUM4": 7500, "ALUM5": 8500,
    "ALUM6": 10000,
}

Valor_lamina_m2 = {
    "CR18": 130000, "CR16": 150000, "CR14": 200000, "HR14": 180000,
    "HR12": 210000, "HR1/8": 230000, "HR3/16": 250000, "HR1/4": 345000,
    "HR5/16": 460000, "HR3/8": 520000, "HR1/2": 730000, "INOX20": 250000,
    "INOX18": 290000, "INOX16": 370000, "INOX14": 440000, "INOX12": 520000,
    "INOX1/8": 700000, "INOX3/16": 850000, "ALUM1": 120000, "ALUM1,5": 190000,
    "ALUM2,5": 300000, "ALUM3": 400000, "ALUM4": 480000, "ALUM5": 550000,
    "ALUM6": 650000,
}

def calcular_descuento(cantidad):
    """
    Retorna el porcentaje de descuento según la cantidad de piezas.
    """
    if cantidad >= 1000:
        return 60  # 60% de descuento
    elif cantidad >= 500:
        return 50  # 50% de descuento
    elif cantidad >= 250:
        return 40  # 40% de descuento
    elif cantidad >= 100:
        return 30  # 30% de descuento
    elif cantidad >= 50:
        return 20  # 20% de descuento
    elif cantidad >= 10:
        return 10  # 10% de descuento
    else:
        return 0  # Sin descuento para menos de 10 piezas


def process_dxf_file(file_path, material, cantidad):
    try:
        if material not in Metro_perimetro_corte or material not in Valor_lamina_m2:
            raise ValueError(f"Material '{material}' no encontrado.")

        # Leer el archivo DXF
        doc = ezdxf.readfile(file_path)
        modelspace = doc.modelspace()

        total_perimeter = 0.0
        largest_area = 0.0
        total_entities = 0

        for entity in modelspace:
            if entity.dxftype() in ["LINE", "CIRCLE", "ARC", "LWPOLYLINE", "POLYLINE"]:
                total_entities += 1
                perimeter = calculate_perimeter(entity)
                area = calculate_area(entity) or 0
                total_perimeter += perimeter or 0

                # Guardar solo el área más grande
                if area > largest_area:
                    largest_area = area

        # Calcular costos
        costo_corte = (total_perimeter / 1000) * Metro_perimetro_corte[material]
        costo_material = (largest_area / 1000000) * Valor_lamina_m2[material]
        costo_unitario = (costo_corte + costo_material)*2
        costo_total = costo_unitario * cantidad
        print(f"costo_corte = {costo_corte}")
        print(f"costo_material = {costo_material}")

        # Aplicar descuento según cantidad
        descuento_porcentaje = calcular_descuento(cantidad)
        descuento_valor = (costo_total * descuento_porcentaje) / 100
        costo_final = costo_total - descuento_valor

        return {
            "status": "success",
            "total_entities": total_entities,
            "total_perimeter": total_perimeter,
            "largest_area": largest_area,
            "costo_unitario": costo_unitario,
            "costo_total": costo_total,
            "descuento_porcentaje": descuento_porcentaje,
            "descuento_valor": descuento_valor,
            "costo_final": costo_final,
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
        }


def calculate_perimeter(entity):
    if entity.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
        points = entity.get_points("xy")
        perimeter = sum(
            math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1])
        )
        return perimeter if entity.is_closed else None
    elif entity.dxftype() == "CIRCLE":
        return 2 * math.pi * entity.dxf.radius
    elif entity.dxftype() == "ARC":
        angle = abs(entity.dxf.end_angle - entity.dxf.start_angle)
        return (angle / 360.0) * (2 * math.pi * entity.dxf.radius)
    elif entity.dxftype() == "LINE":
        start, end = entity.dxf.start, entity.dxf.end
        return math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
    return None

def calculate_area(entity):
    if entity.dxftype() in ["LWPOLYLINE", "POLYLINE"] and entity.is_closed:
        points = entity.get_points("xy")
        return abs(sum(x1 * y2 - y1 * x2 for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]))) / 2.0
    elif entity.dxftype() == "CIRCLE":
        return math.pi * (entity.dxf.radius ** 2)
    return None

def generate_dxf_plot(file_path, output_image_path="app/static/output.png"):
    """
    Genera una visualización del archivo DXF y la guarda como una imagen.
    """
    try:
        # Crear la carpeta 'static' si no existe
        output_dir = os.path.dirname(output_image_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

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
                    2 * radius,
                    2 * radius,
                    angle=0,
                    theta1=start_angle,
                    theta2=end_angle,
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

        print(f"Imagen guardada correctamente en {output_image_path}")
        return output_image_path

    except Exception as e:
        raise RuntimeError(f"Error al generar la visualización: {str(e)}")

