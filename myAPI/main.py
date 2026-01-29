#1. Importaciones
from fastapi import FastAPI

#2. Inicialización APP
app= FastAPI()

#3. Endpoints
@app.get("/")
async def holamundo():
            #Llave      #Valor
    return { "mensaje":"Hola mundo FASTAPI" }

@app.get("/bienvenidos")
async def bien():
            #Llave      #Valor
    return { "mensaje":"Bienvenidos" }

