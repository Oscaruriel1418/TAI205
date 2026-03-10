from fastapi import FastAPI, status, HTTPException, Depends
from typing import Optional
import asyncio
from pydantic import BaseModel,Field
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import datetime

app= FastAPI(title='Examen 2do ', 
             description='Examen segundo parcial', 
             version='1.0.0'
            )

reservas = [{"id":1, "Nombre de usuario":"Oscar Uriel", "Tipo de habitacion":"Doble", "Fecha de reserva":"14-05-2024"},
            {"id":2, "Nombre de usuario":"Benjamin", "Tipo de habitacion":"Suite","Fecha de reserva":"15-05-2024"},
            {"id":3, "Nombre de usuario":"Gerardo abraham", "Tipo de habitacion":"doble","Fecha de reserva":"18-05-2024"},
            {"id":4, "Nombre de usuario":"Francisco Linares", "Tipo de habitacion":"sencilla","Fecha de reserva":"25-05-2024"}]

seguridad=HTTPBasic()

def verificar_peticion(credenciales:HTTPBasicCredentials=Depends(seguridad)):
    userAuth=secrets.compare_digest(credenciales.username, "hotel")
    passAuth=secrets.compare_digest(credenciales.password, "r2026")

    if not(userAuth and passAuth):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Credenciales no autorizadas")
    return credenciales.username


@app.post("/v1/reserva", tags=['Crear Reserva'], status_code=status.HTTP_201_CREATED)
async def crear_reserva(reserva: dict, userAuth:str=Depends(verificar_peticion)):
    # Validamos si el id ya existe iterando la lista
    for rsv in reservas:
         if rsv.get("id") == reserva.get("id"):
            raise HTTPException(
                status_code=400,
                detail="El id ya existe"
            ) 
    reservas.append(reserva)
     
    return {
        "mensaje": "Reserva agregada correctamente",
        "status": "200",
        "Usuario": reserva
    }


@app.get("/v1/reservas",tags=['Listar reservas'])
async def consultaT():
    return{
        "Status":"200",
        "Total": len(reservas),
        "data": reservas
    }
            
@app.get("/v1/reservas/{id}",tags=['Listar por id'])
async def consultaUno(id:Optional[int]=None):
    await asyncio.sleep(2)
            #Llave      #Valor
    if id is not None:
        for reserva in reservas:
                if reserva["id"] == id:
                        return {"reserva encontrada":id, "Datos":reserva}
        return {"Resultado":"Reserva encontrada","Estatus":"200",}
    else:
        return {"Aviso":"No se proporciono ID"}
    

@app.delete("/v1/Resrva/{id}", tags=['Cancelar reserva'],status_code=status.HTTP_200_OK)
async def cancelar_reserva(id: int,userAuth:str=Depends(verificar_peticion)):
    for index, rsv in enumerate(reservas):
        if rsv["id"] == id:
            reservas.pop(index)
            return{
                "message":f"Usuario eliminado por {userAuth}"
            }            
    # Si termina el ciclo y no encontró al usuario, lanza el error
    raise HTTPException(
        status_code=404, 
        detail="No se encontró el usuario para eliminar"
    )