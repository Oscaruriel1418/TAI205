from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime
import asyncio

app = FastAPI(title="API de Biblioteca", version="1.0")

# --- Modelos Pydantic ---
class Usuario(BaseModel):
    nombre: str = Field(min_length=2)
    correo: EmailStr

class Libro(BaseModel):
    id: int
    nombre: str = Field(min_length=2, max_length=100)
    año: int = Field(gt=1450, le=datetime.now().year)
    paginas: int = Field(gt=1)
    estado: Literal["disponible", "prestado"] = "disponible"

class Prestamo(BaseModel):
    id_prestamo: int
    id_libro: int
    usuario: Usuario
    activo: bool = True


# --- "Bases de datos" en memoria ---
libros_db = [
    Libro(id=1, nombre="Libro de ana frank", año=1950, paginas=300, estado="disponible"),
    Libro(id=2, nombre="Alicia en el pais de las maravillas", año=1940, paginas=200, estado="disponible"),
    Libro(id=3, nombre="Mein Kampf", año=1945, paginas=400, estado="disponible")
]
prestamos_db = []


# --- Endpoints ---

# a. Registrar un libro
@app.post("/v1/libro", status_code=status.HTTP_201_CREATED, tags=['Libros'])
async def registrar_libro(libro: Libro):
    await asyncio.sleep(1)
    
    # Validamos manualmente si el libro ya existe para arrojar un 400 (Bad Request)
    for l in libros_db:
        if l.id == libro.id:
            raise HTTPException(status_code=400, detail="El ID del libro ya está registrado.")
            
    libros_db.append(libro)
    return {"Mensaje": "Libro registrado exitosamente", "Libro": libro}

# b. Listar todos los libros disponibles
@app.get("/v1/libros/disponibles", tags=['Libros'])
async def listar_disponibles():
    await asyncio.sleep(1)
    
    disponibles = []
    for libro in libros_db:
        if libro.estado == "disponible":
            disponibles.append(libro)
            
    return {"Libros disponibles": disponibles}

# c. Buscar un libro por su nombre
@app.get("/v1/libro/buscar", tags=['Libros'])
async def buscar_libro(nombre: str):
    await asyncio.sleep(1)
    
    for libro in libros_db:
        if libro.nombre.lower() == nombre.lower():
            return {"Libro encontrado": libro}
            
    return {"Aviso": "Libro no encontrado"}

# d. Registrar el préstamo de un libro a un usuario
@app.post("/v1/prestamo", status_code=status.HTTP_201_CREATED, tags=['Prestamos'])
async def registrar_prestamo(prestamo: Prestamo):
    await asyncio.sleep(1)
    
    # Buscamos el libro para verificar su estado
    libro_encontrado = False
    for libro in libros_db:
        if libro.id == prestamo.id_libro:
            libro_encontrado = True
            if libro.estado == "prestado":
                # 409 Conflict si ya está prestado
                raise HTTPException(status_code=409, detail="El libro ya está prestado.")
            
            # Cambiamos el estado del libro y registramos el préstamo
            libro.estado = "prestado"
            prestamos_db.append(prestamo)
            return {"Mensaje": "Préstamo registrado exitosamente", "Datos": prestamo}
            
    if not libro_encontrado:
        raise HTTPException(status_code=400, detail="El libro solicitado no existe.")

# e. Marcar un libro como devuelto
@app.put("/v1/prestamo/devolver/{id_prestamo}", status_code=status.HTTP_200_OK, tags=['Prestamos'])
async def devolver_libro(id_prestamo: int):
    await asyncio.sleep(1)
    
    for prestamo in prestamos_db:
        if prestamo.id_prestamo == id_prestamo:
            if not prestamo.activo:
                raise HTTPException(status_code=409, detail="El libro ya fue devuelto anteriormente.")
                
            # Marcamos el préstamo como inactivo
            prestamo.activo = False
            
            # Buscamos el libro y lo marcamos como disponible
            for libro in libros_db:
                if libro.id == prestamo.id_libro:
                    libro.estado = "disponible"
                    
            return {"Mensaje": "Libro devuelto con éxito", "Estatus": "200"}
            
    # 409 Conflict si el registro no existe
    raise HTTPException(status_code=409, detail="El registro de préstamo no existe.")

# f. Eliminar el registro de un préstamo
@app.delete("/v1/prestamo/{id_prestamo}", tags=['Prestamos'])
async def eliminar_prestamo(id_prestamo: int):
    await asyncio.sleep(1)
    
    for i in range(len(prestamos_db)):
        if prestamos_db[i].id_prestamo == id_prestamo:
            prestamo_eliminado = prestamos_db.pop(i)
            return {"Mensaje": "Registro de préstamo eliminado físicamente", "Datos": prestamo_eliminado}
            
    return {"Aviso": "No se encontró el ID de préstamo proporcionado"}