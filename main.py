# main.py

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Importamos los routers de controladores
from controladores import dashboard, auth


# Crear instancia de FastAPI
app = FastAPI()

# Montar carpeta "vistas"
templates = Jinja2Templates(directory="vistas")

# Montar carpeta de archivos estáticos (cuando tengamos CSS, imágenes, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Incluir los routers
app.include_router(auth.auth_router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

