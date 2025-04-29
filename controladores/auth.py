from fastapi.responses import HTMLResponse
from base_de_datos.conexion import obtener_conexion
from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from modelos.usuario import autenticar_usuario
from jose import jwt
import bcrypt
import datetime

auth_router = APIRouter()  # <-- ahora todo usa auth_router
templates = Jinja2Templates(directory="vistas")

# Clave secreta para firmar el JWT
SECRET_KEY = "tu_clave_secreta_segura"

def create_access_token(data: dict, expires_delta: int = 30):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# ------------------------
# LOGIN
# ------------------------

@auth_router.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": ""})

@auth_router.post("/login")
def login_post(request: Request, response: Response, nombre: str = Form(...), password: str = Form(...)):
    usuario = autenticar_usuario(nombre, password)
    if usuario:
        token_data = {
            "sub": usuario["nombre"],
            "idusuario": usuario["idusuario"]
        }
        token = create_access_token(token_data)

        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "mensaje": "Usuario o contraseña incorrectos."})

# ------------------------
# LOGOUT
# ------------------------

@auth_router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response

# ------------------------
# REGISTRO
# ------------------------

@auth_router.get("/register", response_class=HTMLResponse)
def mostrar_registro(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@auth_router.post("/register")
def registrar_usuario(nombre: str = Form(...), password: str = Form(...)):
    password_encriptado = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "INSERT INTO usuario (nombre, password) VALUES (%s, %s)"
            cursor.execute(sql, (nombre, password_encriptado))
        conexion.commit()
    finally:
        conexion.close()

    return RedirectResponse(url="/login", status_code=303)

# Función para obtener el usuario actual desde la cookie
async def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no encontrado")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        usuario = {
            "nombre": payload.get("sub"),
            "idusuario": payload.get("idusuario")
        }
        return usuario
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
