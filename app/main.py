from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from app.routers import files

# Crear la aplicación FastAPI
app = FastAPI()

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar plantillas Jinja2
templates = Jinja2Templates(directory="app/templates")

# Incluir las rutas del manejador de archivos
app.include_router(files.router)

# Ruta raíz para renderizar la interfaz HTML
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

