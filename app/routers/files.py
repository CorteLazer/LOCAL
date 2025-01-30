from fastapi.responses import FileResponse
from app.services.dxf_processor import generate_dxf_plot
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from app.services.dxf_processor import process_dxf_file, generate_dxf_plot
import os

router = APIRouter(prefix="/files", tags=["files"])
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload/", response_class=HTMLResponse)
async def upload_file(
    file: UploadFile = File(...),
    material: str = Form(...),
    cantidad: int = Form(...)
):
    if not file.filename.endswith(".dxf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un DXF")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Procesar el archivo DXF con cantidad
    result = process_dxf_file(file_path, material, cantidad)

    if result["status"] == "success":
        return f"""
        <html>
            <head>
                <link rel="stylesheet" href="/static/styles.css">
            </head>
            <body>
                <div class="container">
                    <h2>El archivo {file.filename} fue procesado correctamente.</h2>
                    <p><strong>Material:</strong> {material}</p>
                    <p><strong>Cantidad de piezas:</strong> {cantidad}</p>
                    <table style="width:100%; text-align:left; margin-top:20px;">
                        <tr>
                            <th>Descripción</th>
                            <th>Valor</th>
                        </tr>
                        <tr>
                            <td>Total de entidades:</td>
                            <td>{result['total_entities']}</td>
                        </tr>
                        <tr>
                            <td>Perímetro total:</td>
                            <td>{result['total_perimeter']:.2f} metros</td>
                        </tr>
                        <tr>
                            <td>Área más grande:</td>
                            <td>{result['largest_area']:.2f} mm²</td>
                        </tr>
                        <tr>
                            <td>Costo unitario:</td>
                            <td>{result['costo_unitario']:.2f} COP</td>
                        </tr>
                        <tr>
                            <td>Costo total sin descuento:</td>
                            <td>{result['costo_total']:.2f} COP</td>
                        </tr>
                        <tr>
                            <td>Descuento aplicado:</td>
                            <td>{result['descuento_porcentaje']}%</td>
                        </tr>
                        <tr>
                            <td><strong>Costo final:</strong></td>
                            <td><strong>{result['costo_final']:.2f} COP</strong></td>
                        </tr>
                    </table>
                    <h3>Visualización del archivo DXF:</h3>
                    <img src="/static/{file.filename}.png" alt="TRY DXF" style="max-width:100%; margin-top:20px;">
                    <a href="/" style="display:block; margin-top:20px; text-decoration:none; color:#007BFF;">Volver al inicio</a>
                </div>
            </body>
        </html>
        """
    else:
        return f"""
        <html>
            <body>
                <h2>Error al procesar el archivo {file.filename}.</h2>
                <p>{result['error']}</p>
                <a href="/">Volver al inicio</a>
            </body>
        </html>
        """
