# modelos/usuario.py

import bcrypt
from base_de_datos.conexion import obtener_conexion

def crear_usuario(nombre, password):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "INSERT INTO usuario (nombre, password) VALUES (%s, %s)"
            cursor.execute(sql, (nombre, password))
        conexion.commit()
    finally:
        conexion.close()

def obtener_usuarios():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "SELECT idusuario, nombre FROM usuario"
            cursor.execute(sql)
            usuarios = cursor.fetchall()
        return usuarios
    finally:
        conexion.close()

def obtener_usuario_por_id(idusuario):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "SELECT idusuario, nombre FROM usuario WHERE idusuario = %s"
            cursor.execute(sql, (idusuario,))
            usuario = cursor.fetchone()
        return usuario
    finally:
        conexion.close()

def actualizar_usuario(idusuario, nombre, password):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "UPDATE usuario SET nombre = %s, password = %s WHERE idusuario = %s"
            cursor.execute(sql, (nombre, password, idusuario))
        conexion.commit()
    finally:
        conexion.close()

def eliminar_usuario(idusuario):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "DELETE FROM usuario WHERE idusuario = %s"
            cursor.execute(sql, (idusuario,))
        conexion.commit()
    finally:
        conexion.close()

def autenticar_usuario(nombre, password):
    print(f"Intentando login: nombre={nombre}, password={password}")  # <-- Agrega esta línea

    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "SELECT idusuario, nombre, password FROM usuario WHERE nombre = %s"
            cursor.execute(sql, (nombre,))
            usuario = cursor.fetchone()

            if usuario is None:
                return None  # No existe ese usuario

            password_encriptado = usuario["password"].encode('utf-8')

            # Comparamos el password dado con el encriptado
            if bcrypt.checkpw(password.encode('utf-8'), password_encriptado):
                return usuario  # Login exitoso
            else:
                return None  # Contraseña incorrecta
    finally:
        conexion.close()
