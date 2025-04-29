from fastapi import APIRouter, HTTPException
from modelos.usuario import crear_usuario, obtener_usuarios

router = APIRouter()

@router.post("/usuarios")
def crear_usuario_endpoint(nombre: str, password: str):
    try:
        crear_usuario(nombre, password)
        return {"mensaje": "Usuario creado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usuarios")
def obtener_usuarios_endpoint():
    try:
        usuarios = obtener_usuarios()
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
