from fastapi import FastAPI, status, HTTPException, Depends
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import datetime

app = FastAPI(
    title='Examen 2do Parcial vr2',
    description='API de Sistema de turnos bancarios',
    version='1.0.0'
)

security = HTTPBasic()

# ── Modelo de datos ────────────────────────────────────────────────────────────

class TurnoSchema(BaseModel):
    id: int = Field(..., gt=0, description="Identificador del turno")
    cliente: str = Field(..., min_length=8, examples=["Lorena Gómez"])
    tramite: Literal["deposito", "retiro", "consulta"] = Field(
        ..., description="Tipo de trámite permitido"
    )
    fecha_turno: datetime.date = Field(..., description="Fecha del turno (YYYY-MM-DD)")
    hora_turno: datetime.time = Field(..., description="Hora del turno (HH:MM), entre 09:00 y 15:00")

    @model_validator(mode="after")
    def validar_turno(self):
        hoy = datetime.date.today()
        ahora = datetime.datetime.now().time()

        # Fecha debe ser futura
        if self.fecha_turno < hoy:
            raise ValueError("La fecha del turno no puede ser en el pasado")

        # Si es hoy, la hora no puede haber pasado
        if self.fecha_turno == hoy and self.hora_turno <= ahora:
            raise ValueError("La hora del turno debe ser futura")

        # Rango horario permitido: 09:00 a 15:00
        hora_min = datetime.time(9, 0)
        hora_max = datetime.time(15, 0)
        if not (hora_min <= self.hora_turno <= hora_max):
            raise ValueError("La hora del turno debe estar entre las 9:00 AM y las 3:00 PM")

        return self


# ── Datos en memoria ───────────────────────────────────────────────────────────

turnos = [
    {
        "id": 1,
        "cliente": "Lorena Gómez",
        "tramite": "deposito",
        "fecha_turno": "2025-06-01",
        "hora_turno": "10:00",
        "atendido": False
    },
    {
        "id": 2,
        "cliente": "Carlos Mendoza",
        "tramite": "retiro",
        "fecha_turno": "2025-06-01",
        "hora_turno": "11:30",
        "atendido": False
    },
]


# ── Seguridad ──────────────────────────────────────────────────────────────────

def verificar_peticion(credenciales: HTTPBasicCredentials = Depends(security)):
    user_ok = secrets.compare_digest(credenciales.username, "banco")
    pass_ok = secrets.compare_digest(credenciales.password, "2468")

    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no autorizadas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credenciales.username


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.post("/v1/turno", tags=["Turnos"], status_code=status.HTTP_201_CREATED)
async def crear_turno(turno: TurnoSchema):
    # Verificar ID duplicado
    for t in turnos:
        if t["id"] == turno.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un turno con el id {turno.id}"
            )

    # Verificar máximo 5 turnos por día por cliente
    turnos_del_cliente_ese_dia = [
        t for t in turnos
        if t["cliente"] == turno.cliente
        and t["fecha_turno"] == str(turno.fecha_turno)
    ]
    if len(turnos_del_cliente_ese_dia) >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El cliente '{turno.cliente}' ya tiene 5 turnos para el {turno.fecha_turno}"
        )

    nuevo = turno.model_dump()
    # Convertir date y time a string para poder almacenarlos en la lista
    nuevo["fecha_turno"] = str(turno.fecha_turno)
    nuevo["hora_turno"] = str(turno.hora_turno)
    nuevo["atendido"] = False
    turnos.append(nuevo)

    return {
        "mensaje": "Turno creado correctamente",
        "data": nuevo
    }


@app.get("/v1/turnos", tags=["Turnos"])
async def listar_turnos():
    return {
        "status": 200,
        "total": len(turnos),
        "data": turnos
    }


@app.get("/v1/turnos/{id}", tags=["Turnos"])
async def consultar_turno(id: int):
    for turno in turnos:
        if turno["id"] == id:
            return {
                "status": 200,
                "data": turno
            }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se encontró ningún turno con el id {id}"
    )


@app.patch("/v1/turno/{id}/atender", tags=["Turnos"], status_code=status.HTTP_200_OK)
async def marcar_atendido(id: int, user: str = Depends(verificar_peticion)):
    for turno in turnos:
        if turno["id"] == id:
            if turno["atendido"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El turno ya fue marcado como atendido"
                )
            turno["atendido"] = True
            return {
                "mensaje": f"Turno {id} marcado como atendido por {user}",
                "data": turno
            }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se encontró ningún turno con el id {id}"
    )


@app.delete("/v1/turno/{id}", tags=["Turnos"], status_code=status.HTTP_200_OK)
async def eliminar_turno(id: int, user: str = Depends(verificar_peticion)):
    for index, turno in enumerate(turnos):
        if turno["id"] == id:
            turnos.pop(index)
            return {
                "mensaje": f"Turno {id} eliminado por {user}"
            }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se encontró el turno con id {id} para eliminar"
    )