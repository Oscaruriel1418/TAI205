#1. Importaciones
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, status, HTTPException, Depends
from typing import Optional
import asyncio
from pydantic import BaseModel,Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

#Simulamos una creacion de llave 
#Esta llave nunca debe de ir en el codigo
SECRET_KEY = "mi_llave_secreta_1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30# Límite máximo establecido a 30 minutos


#2. Inicialización APP
app= FastAPI(title='Mi primera API ', 
             description='API de ejemplo con FastAPI', 
             version='1.0.0'
            )

#BD fictisia por el momento 
usuarios = [
    { "id":1, "nombre":"Oscar", "edad":"25" },
    { "id":2, "nombre":"Benja", "edad":"30" },
    { "id":3, "nombre":"Osman", "edad":"22" },
    { "id":4, "nombre":"Uriel", "edad":"28" },
]
# BD ficticia para usuarios (los que vas a modificar)
usuarios = [
    { "id":1, "nombre":"Oscar", "edad":"25" },
    { "id":2, "nombre":"Benja", "edad":"30" },
    { "id":3, "nombre":"Osman", "edad":"22" },
    { "id":4, "nombre":"Uriel", "edad":"28" },
]

# NUEVA BD ficticia para ADMINISTRADORES (los que pueden iniciar sesión)
administradores = [
    {"username": "admin", "password": "123456"},
    {"username": "oscar", "password": "supersecreto"}
]

# Esto le dice a FastAPI dónde van a ir los usuarios a pedir su token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- 2. GENERACIÓN DE TOKENS ---
def crear_token_acceso(data: dict, expira_en: timedelta):
    to_encode = data.copy()
    # Definimos el tiempo de expiración (Hora actual + 30 minutos)
    expire = datetime.now(timezone.utc) + expira_en
    to_encode.update({"exp": expire})
    
    # Creamos el gafete digital firmado con nuestro secreto
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#Seguridad HTTP Basic
#seguridad=HTTPBasic()
#
#def verificar_peticion(credenciales:HTTPBasicCredentials=Depends(seguridad)):
#    userAuth=secrets.compare_digest(credenciales.username, "oscaruriel")
#    passAuth=secrets.compare_digest(credenciales.password, "123456")
#
#    if not(userAuth and passAuth):
#        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Credenciales no autorizadas")
#    return credenciales.username

# --- 3. VALIDACIÓN DE TOKENS ---
async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    # Este es el mensaje de error estándar si algo sale mal
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales o el token expiró",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Intentamos leer el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        # Si no hay usuario en el token, rechazamos
        if username is None:
            raise credenciales_exception
            
    except JWTError:
        # Si el token es falso, modificado o expiró, entra aquí y rechaza
        raise credenciales_exception
        
    return username


#Modelo de validacion pydantic
class crear_usuarios(BaseModel):
    id:int = Field(...,gt=0, description="Identificador de usuario")
    nombre:str =Field(..., min_length=3,max_length=50,examples="Juanita")
    edad:int =Field(..., ge=1,le=123,description="Edad valida entre 1 y 123")

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

# GET de FastAPI 
@app.get("/v1/usuarios", tags=['CRUD HTTP'])
async def consulta_usuarios():
    return {
        "Status": "200",
        "Total": len(usuarios),
        "data": usuarios
    }

# POST de FastAPI 
@app.post("/v1/usuarios", tags=['CRUD HTTP'], status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: dict):
    # Validamos si el id ya existe iterando la lista
    for usr in usuarios:
        if usr.get("id") == usuario.get("id"):
            raise HTTPException(
                status_code=400,
                detail="El id ya existe"
            ) 
            
    usuarios.append(usuario)
    
    return {
        "mensaje": "Usuario agregado correctamente",
        "status": "200",
        "Usuario": usuario
    }

# PUT de FastAPI 
@app.put("/v1/usuarios/{id}", tags=['CRUD HTTP'])
async def actualizar_usuario(id: int, usuario_actualizado: dict, userAuth:str=Depends(obtener_usuario_actual)):
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
@app.delete("/v1/usuarios/{id}", tags=['CRUD HTTP'],status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int,userAuth:str=Depends(obtener_usuario_actual)):
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


#Ruta en donde el usuario va a iniciar sesion
# Ruta en donde el usuario va a iniciar sesion
@app.post("/token")
async def iniciar_sesion(form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Buscamos al administrador en nuestra lista
    admin_encontrado = None
    for admin in administradores:
        if admin["username"] == form_data.username:
            admin_encontrado = admin
            break # Lo encontramos, dejamos de buscar
    
    # 2. Verificamos que exista y la contraseña coincida
    if not admin_encontrado or admin_encontrado["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 3. Si todo está bien, le generamos su token de 30 minutos
    tiempo_expiracion = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = crear_token_acceso(
        data={"sub": admin_encontrado["username"]}, 
        expira_en=tiempo_expiracion
    )
    
    return {"access_token": token, "token_type": "bearer"}