from fastapi import FastAPI, Response, status
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# Función de conexión a la BD en el contenedor Docker
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootpassword",
        database="taller_db",
        port=3306
    )

# Modelo de datos con Pydantic para validación de entrada
class Producto(BaseModel):
    nombre: str
    precio: float
    disponible: bool = True

# 1. LISTAR TODOS LOS REGISTROS (GET /productos)
@app.get("/productos")
def listar():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    data = cursor.fetchall()
    return {"status": True, "message": "Registros consultados", "data": data}

# 2. CONSULTAR UN REGISTRO POR ID (GET /productos/{id})
@app.get("/productos/{id}")
def consultar(id: int, response: Response):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    data = cursor.fetchone()
    if not data:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status": False, "message": "Registro no encontrado"}
    return {"status": True, "message": "Registro consultado", "data": data}

# 3. CREAR UN NUEVO REGISTRO (POST /productos)
@app.post("/productos", status_code=201)
def crear(producto: Producto):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, precio, disponible) VALUES (%s, %s, %s)",
        (producto.nombre, producto.precio, producto.disponible)
    )
    db.commit()
    return {
        "status": True, 
        "message": "Registro creado", 
        "data": {"id": cursor.lastrowid, **producto.model_dump()}
    }

# 4. ACTUALIZAR UN REGISTRO EXISTENTE (PUT /productos/{id})
@app.put("/productos/{id}")
def actualizar(id: int, producto: Producto, response: Response):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE productos SET nombre=%s, precio=%s, disponible=%s WHERE id=%s",
        (producto.nombre, producto.precio, producto.disponible, id)
    )
    db.commit()
    if cursor.rowcount == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status": False, "message": "Registro no encontrado"}
    return {"status": True, "message": "Registro actualizado", "data": {"id": id, **producto.model_dump()}}

# 5. ELIMINAR UN REGISTRO (DELETE /productos/{id})
@app.delete("/productos/{id}")
def eliminar(id: int, response: Response):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    db.commit()
    if cursor.rowcount == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status": False, "message": "Registro no encontrado"}
    return {"status": True, "message": "Registro eliminado"}