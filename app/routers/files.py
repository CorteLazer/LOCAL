# Importar el módulo APIRouter de FastAPI para gestionar rutas.
# Importar UploadFile y File para manejar la carga de archivos en solicitudes HTTP.
# Importar HTTPException para manejar errores de solicitudes HTTP.
# Importar HTMLResponse para devolver respuestas en formato HTML.
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse

# Importar una función personalizada para procesar archivos DXF desde un módulo de servicios.
from app.services.dxf_processor import process_dxf_file

# Importar el módulo os para operaciones relacionadas con el sistema de archivos.
import os

# Crear un enrutador con un prefijo para las rutas relacionadas con archivos y un grupo de etiquetas para organización.
router = APIRouter(prefix="/files", tags=["files"])

# Definir el directorio donde se guardarán los archivos subidos.
UPLOAD_DIR = "uploaded_files"

# Asegurarse de que el directorio definido para las cargas de archivos existe, creándolo si es necesario.
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Definir un endpoint para subir archivos, especificando que devuelve una respuesta en formato HTML.
@router.post("/upload/", response_class=HTMLResponse)
async def upload_file(file: UploadFile = File(...)):  # Recibir un archivo cargado como parámetro.
    # Verificar que el archivo tenga una extensión válida (.dxf).
    if not file.filename.endswith(".dxf"):
        # Si el archivo no es un DXF, lanzar una excepción HTTP con el código 400 (Solicitud incorrecta).
        raise HTTPException(status_code=400, detail="El archivo debe ser un DXF")

    # Construir la ruta completa donde se guardará el archivo subido.
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Abrir el archivo en modo escritura binaria y escribir su contenido en la ubicación definida.
    with open(file_path, "wb") as f:
        f.write(await file.read())  # Leer y escribir el contenido del archivo cargado de forma asíncrona.

    # Llamar a la función personalizada para procesar el archivo DXF y obtener los resultados.
    result = process_dxf_file(file_path)

    # Verificar si el procesamiento del archivo fue exitoso.
    if result["status"] == "success":
        # Extraer los detalles de las entidades procesadas, el número total de entidades y el perímetro total.
        entity_details = result["entity_details"]
        total_entities = result["total_entities"]
        total_perimeter = result["total_perimeter"]
        # Extraer la ruta del archivo de visualización generado durante el procesamiento.
        visualization_path = result["visualization_path"]

        # Crear una lista HTML para mostrar los detalles de cada entidad en el archivo DXF.
        entities_html = "<ul>"
        for entity in entity_details:  # Iterar sobre cada entidad en los resultados.
            # Agregar información de cada entidad (tipo, si está cerrada, perímetro y área) como elementos de lista.
            entities_html += f"""
            <li>
                Tipo: {entity['type']}<br>
                Cerrado: {"Sí" if entity['closed'] else "No"}<br>
                Perímetro: {entity['perimeter'] if entity['perimeter'] else "No disponible"}<br>
                Área: {entity['area'] if entity['area'] else "No disponible"}<br>
            </li>
            <br>
            """
        entities_html += "</ul>"  # Cerrar la lista HTML.

        # Construir una respuesta HTML para mostrar el resumen del procesamiento del archivo DXF.
        return f"""
        <html>
            <body>
                <h2>El archivo {file.filename} fue procesado correctamente.</h2>
                <p>Total de entidades: {total_entities}</p>
                <p>Perímetro total: {total_perimeter}</p>
                <h3>Detalles de las entidades:</h3>
                {entities_html}
                <h3>Visualización:</h3>
                <img src="/static/visualization.png" alt="Visualización del archivo DXF" style="border:1px solid #ccc; max-width: 100%; height: auto;">
                <br>
                <a href="/">Volver al inicio</a>
            </body>
        </html>
        """
    else:
        # Si hubo un error durante el procesamiento, devolver una respuesta HTML con el mensaje de error.
        return f"""
        <html>
            <body>
                <h2>Error al procesar el archivo {file.filename}.</h2>
                <p>{result['error']}</p>
                <a href="/">Volver al inicio</a>
            </body>
        </html>
        """
