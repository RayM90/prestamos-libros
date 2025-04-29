from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from base_de_datos.conexion import obtener_conexion
from controladores.auth import get_current_user_from_cookie
from datetime import date
import uuid
from datetime import timedelta



router = APIRouter()
templates = Jinja2Templates(directory="vistas")

SECRET_KEY = "tu_clave_secreta_segura"

# Endpoint para mostrar el dashboard
@router.get("/dashboard", response_class=HTMLResponse)
async def mostrar_dashboard(request: Request, usuario: dict = Depends(get_current_user_from_cookie)):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Obtener los libros y sus detalles, incluyendo la fecha de devolución
            cursor.execute("""
                SELECT libros.idlibros, libros.titulo, libros.autor, libros.editorial, 
                       libros.disponible, prestamos.id_prestamo, prestamos.fecha_devolucion
                FROM libros
                LEFT JOIN prestamos ON libros.idlibros = prestamos.libros_idlibros AND prestamos.usuario_idusuario = %s
            """, (usuario['idusuario'],))  # Asegúrate de filtrar por el usuario actual
            libros = cursor.fetchall()
    finally:
        conexion.close()

    return templates.TemplateResponse("dashboard.html", {"request": request, "libros": libros, "usuario": usuario})


@router.post("/prestar")
async def prestar_libro(request: Request, idlibro: int = Form(...), usuario: dict = Depends(get_current_user_from_cookie)):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # 1. Verificar que el libro esté disponible
            cursor.execute("SELECT disponible FROM libros WHERE idlibros = %s", (idlibro,))
            resultado = cursor.fetchone()
            if not resultado or resultado['disponible'] == 0:
                return HTMLResponse(content="Libro no disponible", status_code=400)

            # 2. Registrar el préstamo en la tabla 'prestamos'
            id_prestamo = str(uuid.uuid4())
            fecha_prestamo = date.today()

            # Calcular la fecha de devolución: 30 días después del préstamo
            fecha_devolucion = fecha_prestamo + timedelta(days=30)

            cursor.execute("""
                INSERT INTO prestamos (id_prestamo, libros_idlibros, usuario_idusuario, fecha_prestamo, fecha_devolucion)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_prestamo, idlibro, usuario['idusuario'], fecha_prestamo, fecha_devolucion))

            # 3. Actualizar el estado del libro a 'No disponible'
            cursor.execute("UPDATE libros SET disponible = 0 WHERE idlibros = %s", (idlibro,))

            # 4. Confirmar cambios
            conexion.commit()

    finally:
        conexion.close()

    # Redirigir al dashboard y pasar la fecha de devolución
    return RedirectResponse(url=f"/dashboard?fecha_devolucion={fecha_devolucion}", status_code=303)


