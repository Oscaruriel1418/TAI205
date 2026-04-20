from fastapi import FastAPI, status, HTTPException, Depends
from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import datetime

app = FastAPI(
    title='Examen 2do Parcial',
    description='API de Sistema de Reservas Hospedaje',
    version='1.0.0'
)

security = HTTPBasic()

# ── Modelo de datos ────────────────────────────────────────────────────────────

class ReservaSchema(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de la reserva")
    huesped: str = Field(..., min_length=5, examples=["Juana Pérez"])
    habitacion: Literal["sencilla", "doble", "suite"] = Field(
        ..., description="Tipo de habitación permitido"
    )
    fecha_entrada: datetime.date = Field(..., description="Fecha de entrada (YYYY-MM-DD)")
    fecha_salida: datetime.date = Field(..., description="Fecha de salida (YYYY-MM-DD)")

    @model_validator(mode="after")
    def validar_fechas(self):
        hoy = datetime.date.today()

        if self.fecha_entrada < hoy:
            raise ValueError("La fecha de entrada no puede ser menor a la fecha actual")

        if self.fecha_salida <= self.fecha_entrada:
            raise ValueError("La fecha de salida debe ser mayor que la fecha de entrada")

        duracion = (self.fecha_salida - self.fecha_entrada).days
        if duracion > 7:
            raise ValueError(f"La estancia no puede ser mayor a 7 días (solicitaste {duracion} días)")

        return self


# ── Datos en memoria ───────────────────────────────────────────────────────────

reservas = [
    {
        "id": 1,
        "huesped": "Oscar Uriel",
        "habitacion": "doble",
        "fecha_entrada": "2025-06-01",
        "fecha_salida": "2025-06-03",
        "confirmada": False
    },
    {
        "id": 2,
        "huesped": "Benjamin Torres",
        "habitacion": "suite",
        "fecha_entrada": "2025-06-05",
        "fecha_salida": "2025-06-07",
        "confirmada": False
    },
]


# ── Seguridad ──────────────────────────────────────────────────────────────────

def verificar_peticion(credenciales: HTTPBasicCredentials = Depends(security)):
    user_ok = secrets.compare_digest(credenciales.username, "hotel")
    pass_ok = secrets.compare_digest(credenciales.password, "r2026")

    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no autorizadas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credenciales.username


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.post("/v1/reserva", tags=["Reservas"], status_code=status.HTTP_201_CREATED)
async def crear_reserva(
    reserva: ReservaSchema,                        # ahora usa el modelo Pydantic
    user: str = Depends(verificar_peticion)
):
    for rsv in reservas:
        if rsv["id"] == reserva.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una reserva con el id {reserva.id}"
            )

    nueva = reserva.model_dump()
    nueva["confirmada"] = False                    # toda reserva inicia sin confirmar
    reservas.append(nueva)

    return {
        "mensaje": "Reserva creada correctamente",
        "data": nueva
    }


@app.get("/v1/reservas", tags=["Reservas"])
async def listar_reservas():
    return {
        "status": 200,
        "total": len(reservas),
        "data": reservas
    }


@app.get("/v1/reservas/{id}", tags=["Reservas"])
async def consultar_reserva(id: int):
    for reserva in reservas:
        if reserva["id"] == id:
            return {
                "status": 200,
                "data": reserva
            }
    # si no encontró nada lanza el 404 correcto
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se encontró ninguna reserva con el id {id}"
    )


@app.patch("/v1/reserva/{id}/confirmar", tags=["Reservas"], status_code=status.HTTP_200_OK)
async def confirmar_reserva(id: int):
    for reserva in reservas:
        if reserva["id"] == id:
            if reserva["confirmada"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La reserva ya estaba confirmada"
                )
            reserva["confirmada"] = True
            return {
                "mensaje": f"Reserva {id} confirmada exitosamente",
                "data": reserva
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se encontró ninguna reserva con el id {id}"
    )


@app.delete("/v1/reserva/{id}", tags=["Reservas"], status_code=status.HTTP_200_OK)
async def cancelar_reserva(
    id: int,
    user: str = Depends(verificar_peticion)
):
    for index, rsv in enumerate(reservas):
        if rsv["id"] == id:
            reservas.pop(index)
            return {
                "mensaje": f"Reserva {id} cancelada por {user}"
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se encontró la reserva con id {id} para cancelar"
    )