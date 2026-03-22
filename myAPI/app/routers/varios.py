from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from app.data.database import usuarios
from typing import Optional
import asyncio

routerV=APIRouter(tags=['Inicio'])

#3. Endpoints
@routerV.get("/")
async def holamundo():
            #Llave      #Valor
    return { "mensaje":"Hola mundo FASTAPI" }

@routerV.get("/v1/bienvenidos")
async def bien():
            #Llave      #Valor
    return { "mensaje":"Bienvenidos" }

@routerV.get("/v1/promedio")
async def promedio():
        #simulacion de peticion, consulta a BD, etc...
    await asyncio.sleep(3)
            #Llave      #Valor
    return {
        "Calificacion":"7.5",
        "Status":"200"
                }

@routerV.get("/v1/usuario/{id}")
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
