#1. Importaciones
from fastapi import FastAPI, status, HTTPException
from typing import Optional
import asyncio

#2. Inicialización APP
app= FastAPI(title='Mi primera API ', 
             description='API de ejemplo con FastAPI', 
             version='1.0.0'
            )

#BD fictisia por el momento 
usuarios = [
    { "id":"1", "nombre":"Oscar", "edad":"25" },
    { "id":"2", "nombre":"Benja", "edad":"30" },
    { "id":"3", "nombre":"Osman", "edad":"22" },
    { "id":"4", "nombre":"Uriel", "edad":"28" },
]

#3. Endpoints
@app.get("/",tags=['Inicio'])
async def holamundo():
            #Llave      #Valor
    return { "mensaje":"Hola mundo FASTAPI" }

@app.get("/v1/bienvenidos",tags=['Inicio'])
async def bien():
            #Llave      #Valor
    return { "mensaje":"Bienvenidos" }

@app.get("/v1/promedio",tags=['Calificaciones'])
async def promedio():
        #simulacion de peticion, consulta a BD, etc...
    await asyncio.sleep(3)
            #Llave      #Valor
    return {
        "Calificacion":"7.5",
        "Status":"200"
                }

@app.get("/v1/usuario/{id}",tags=['Parametros'])
async def consultaUno(id:Optional[int]=None):
    await asyncio.sleep(2)
            #Llave      #Valor
    if id is not None:
        for usuario in usuarios:
                if usuario["id"] == id:
                        return {"Usuario encontrado":id, "Datos":usuario}
        return {"Resultado":"Usuario encontrado","Estatus":"200",}
    else:
        return {"Aviso":"No se proporciono ID"}

@app.get("/v1/usuarios",tags=['CRUD HTTP'])
async def consultaT():
    return{
        "Status":"200",
        "Total": len(usuarios),
        "data": usuarios
    }

@app.get("/v1/usuarios",tags=['CRUD HTTP'])
async def crea_usuario(usuario:dict):
    for usr in usuarios:
        if usr["id"] == usuario.get("id"):
            raise HTTPException(
                status_code=400,
                detail="El id ya existe"
            )
    usuarios.append(usuario)
    return{
        "mensaje":"Usuario agregado correctamente",
        "status":"200",
        "usuario":usuario
    }    