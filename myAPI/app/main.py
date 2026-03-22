#1. Importaciones
from fastapi import FastAPI
from app.routers import usuarios, varios

#2. Inicialización APP
app= FastAPI(title='Mi primera API ', 
             description='API de ejemplo con FastAPI', 
             version='1.0.0'
            )
app.include_router(usuarios.routerU)
app.include_router(varios.routerV)
