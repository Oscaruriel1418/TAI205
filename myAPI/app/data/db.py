from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

#1.definimos la URL de conexion con el contenedor 
DATABASE_URL= os.getenv("DATABASE_URL", "postgresql://admin:123456@postgres:5432/DB_miapi")

#2. Creamos motor de la conexion
engine= create_engine(DATABASE_URL)

#3. Definimos el manejador de sessiones
SessionLocal=  sessionmaker(autocommit=False, autoflush=False, bind= engine)


#4. Instanciamos la Base declarativa del modelo 
Base=declarative_base()

#5. Funcion para manejo de sesiones por peticion
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close