"""Gestión de referencias oficiales INEGI por escala y tipo de carta."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_admin_or_maestro
from app.models.fuente_inegi import FuenteInegi, EstadoEnlaceEnum
from app.models.usuario import Usuario
from app.schemas.fuente_inegi import FuenteInegiCreate, FuenteInegiUpdate, FuenteInegiRead

router = APIRouter()


def guardar_fuente(db: Session, fuente: FuenteInegi) -> FuenteInegi:
    """La restricción de BD cubre también altas/ediciones simultáneas."""
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        diagnostico = getattr(error.orig, "diag", None)
        if getattr(diagnostico, "constraint_name", None) == "uq_fuentes_inegi_escala_tipo":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una fuente INEGI para esa escala y tipo de carta.",
            ) from error
        raise
    db.refresh(fuente)
    return fuente


@router.get("/", response_model=list[FuenteInegiRead])
def listar_fuentes(
    db: Session = Depends(get_db),
    personal: Usuario = Depends(get_current_admin_or_maestro),
):
    return db.query(FuenteInegi).order_by(FuenteInegi.escala, FuenteInegi.tipo_carta).all()


@router.post("/", response_model=FuenteInegiRead, status_code=status.HTTP_201_CREATED)
def crear_fuente(
    datos: FuenteInegiCreate,
    db: Session = Depends(get_db),
    personal: Usuario = Depends(get_current_admin_or_maestro),
):
    fuente = FuenteInegi(**datos.model_dump())
    db.add(fuente)
    return guardar_fuente(db, fuente)


@router.put("/{fuente_id}", response_model=FuenteInegiRead)
def editar_fuente(
    fuente_id: UUID,
    datos: FuenteInegiUpdate,
    db: Session = Depends(get_db),
    personal: Usuario = Depends(get_current_admin_or_maestro),
):
    fuente = db.get(FuenteInegi, fuente_id)
    if fuente is None:
        raise HTTPException(status_code=404, detail="Fuente INEGI no encontrada")

    cambios = datos.model_dump(exclude_unset=True)
    if "url" in cambios and cambios["url"] != fuente.url:
        fuente.estado_enlace = EstadoEnlaceEnum.SIN_VERIFICAR
        fuente.fecha_verificacion = None
    for campo, valor in cambios.items():
        setattr(fuente, campo, valor)
    return guardar_fuente(db, fuente)


@router.delete("/{fuente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_fuente(
    fuente_id: UUID,
    db: Session = Depends(get_db),
    personal: Usuario = Depends(get_current_admin_or_maestro),
):
    fuente = db.get(FuenteInegi, fuente_id)
    if fuente is None:
        raise HTTPException(status_code=404, detail="Fuente INEGI no encontrada")
    db.delete(fuente)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
