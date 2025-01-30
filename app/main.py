from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from app.routers import files

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(files.router)

materials = [
    "CR18", "CR16", "CR14", "HR14", "HR12", "HR1/8", "HR3/16", "HR1/4", "HR5/16", "HR3/8", "HR1/2",
    "INOX20", "INOX18", "INOX16", "INOX14", "INOX12", "INOX1/8", "INOX3/16",
    "ALUM1", "ALUM1,5", "ALUM2,5", "ALUM3", "ALUM4", "ALUM5", "ALUM6"
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "materials": materials
    })

