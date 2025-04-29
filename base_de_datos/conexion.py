# base_de_datos/conexion.py

import pymysql
import pymysql.cursors
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # Para montar los archivos estáticos

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") # Para montar los archivos estáticos

def obtener_conexion():
    conexion = pymysql.connect(
        host="localhost",
        user="root",
        password="271215",  # password aquí si tienes
        db="prestamo_libros",  # nombre de tu base de datos
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    return conexion
