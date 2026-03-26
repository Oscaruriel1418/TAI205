#1. Importaciones
from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from app.data.database import usuarios
from app.models.usuarios import crear_usuarios
from app.security.auth import verificar_peticion
from sqlalchemy.orm import session
from app.data.db import get_db
from app.data.usuario import usuario as usuarioDB

routerU= APIRouter(
    prefix="/v1/usuarios",
    tags=['CRUD HTTP']
)
@routerU.get("/")
async def leer_usuarios(db:session= Depends(get_db)):
    queryUsuarios= db.query(usuarioDB).all()
    return{
        "Status":"200",
        "Total": len(queryUsuarios),
        "Usuarios": queryUsuarios
    }




# POST de FastAPI 
@routerU.post("/", status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuarioP:dict, db:session= Depends(get_db)):
   usuarioNuevo= usuarioDB(nombre= usuarioP.nombre, edad= usuarioP.edad)
   db.add(usuarioNuevo)
   db.commit()
   db.refreah()
    
   return {
        "mensaje": "Usuario agregado correctamente",
        "Usuario": usuarioP
    }

# PUT de FastAPI 
@routerU.put("/{id}")
async def actualizar_usuario(id: int, usuario_actualizado: dict, status_code=status):
    # Usamos enumerate para recorrer la lista y obtener tanto el índice (i) como los datos (usr)
    for i, usr in enumerate(usuarios):
        if usr.get("id") == id:
            # Aseguramos que el ID del diccionario sea el mismo que el de la URL
            usuario_actualizado["id"] = id 
            
            # Actualizamos el usuario usando el índice 'i'
            usuarios[i] = usuario_actualizado
            
            # Retornamos el éxito inmediatamente después de actualizar
            return {
                "mensaje": "Usuario actualizado correctamente",
                "status": "200",
                "data": usuario_actualizado
            }
            
    # Si el ciclo 'for' termina y nunca entró al 'if', significa que no existe
    raise HTTPException(
        status_code=404, 
        detail="Usuario no encontrado para actualizar"
    )
# DELETE de FastAPI
@routerU.delete("/{id}",status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int,userAuth:str=Depends(verificar_peticion)):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuarios.pop(index)
            return{
                "message":f"Usuario eliminado por {userAuth}"
            }            
    # Si termina el ciclo y no encontró al usuario, lanza el error
    raise HTTPException(
        status_code=404, 
        detail="No se encontró el usuario para eliminar"
    )