"""
Préstamo management endpoints
CU-08: Solicitar Préstamo
CU-09: Registrar Préstamo (Aprobar + Entregar)
CU-10: Registrar Devolución y Evaluación
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from app.core.dependencies import get_db, get_current_admin_user, get_current_user
from app.models.usuario import Usuario
from app.models.carta import Carta, DisponibilidadEnum
from app.models.prestamo import Prestamo, EstadoPrestamoEnum
from app.schemas.prestamo import (
    PrestamoSolicitar,
    PrestamoAprobar,
    PrestamoRechazar,
    PrestamoEntregar,
    PrestamoDevolver,
    PrestamoRead,
)


router = APIRouter()


# CU-08: Solicitar Préstamo
@router.post("/", response_model=PrestamoRead, status_code=status.HTTP_201_CREATED)
def solicitar_prestamo(
    data: PrestamoSolicitar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    CU-08: Un usuario solicita el préstamo de una carta.
    Valida disponibilidad y que no tenga préstamos vencidos.
    """
    # Verificar que la carta existe y está disponible
    carta = db.query(Carta).filter(Carta.id == data.carta_id).first()
    if not carta:
        raise HTTPException(status_code=404, detail="Carta no encontrada")

    if carta.disponibilidad not in [DisponibilidadEnum.FISICA, DisponibilidadEnum.AMBAS]:
        raise HTTPException(
            status_code=400,
            detail="La carta no está disponible para préstamo físico"
        )

    # Verificar que la carta no esté ya prestada
    prestamo_activo = db.query(Prestamo).filter(
        Prestamo.carta_id == data.carta_id,
        Prestamo.estado.in_([
            EstadoPrestamoEnum.SOLICITADO,
            EstadoPrestamoEnum.APROBADO,
            EstadoPrestamoEnum.ENTREGADO,
        ])
    ).first()

    if prestamo_activo:
        raise HTTPException(
            status_code=400,
            detail="Esta carta ya tiene un préstamo activo"
        )

    # Verificar que el usuario no tenga préstamos vencidos
    prestamos_vencidos = db.query(Prestamo).filter(
        Prestamo.usuario_id == current_user.id,
        Prestamo.estado == EstadoPrestamoEnum.VENCIDO,
    ).count()

    if prestamos_vencidos > 0:
        raise HTTPException(
            status_code=400,
            detail="Tienes préstamos vencidos. Devuelve el material pendiente antes de solicitar uno nuevo."
        )

    # Crear solicitud
    prestamo = Prestamo(
        usuario_id=current_user.id,
        carta_id=data.carta_id,
        estado=EstadoPrestamoEnum.SOLICITADO,
        notas_solicitud=data.notas_solicitud,
    )

    db.add(prestamo)
    db.commit()
    db.refresh(prestamo)

    return prestamo


# Listar préstamos
@router.get("/", response_model=List[PrestamoRead])
def list_prestamos(
    estado: Optional[EstadoPrestamoEnum] = None,
    usuario_id: Optional[UUID] = None,
    carta_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Listar préstamos. Admin ve todos, usuarios normales solo los suyos.
    """
    query = db.query(Prestamo)

    # Non-admin users only see their own
    if current_user.tipo_usuario != "ADMIN":
        query = query.filter(Prestamo.usuario_id == current_user.id)
    else:
        if usuario_id:
            query = query.filter(Prestamo.usuario_id == usuario_id)

    if estado:
        query = query.filter(Prestamo.estado == estado)

    if carta_id:
        query = query.filter(Prestamo.carta_id == carta_id)

    query = query.order_by(Prestamo.created_at.desc())
    return query.offset(skip).limit(limit).all()


# Ver detalle de un préstamo
@router.get("/{prestamo_id}", response_model=PrestamoRead)
def get_prestamo(
    prestamo_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    # Non-admin can only see their own
    if current_user.tipo_usuario != "ADMIN" and prestamo.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sin permiso")

    return prestamo


# CU-09: Aprobar solicitud (admin)
@router.post("/{prestamo_id}/aprobar", response_model=PrestamoRead)
def aprobar_prestamo(
    prestamo_id: UUID,
    data: PrestamoAprobar,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user),
):
    """CU-09: Admin aprueba una solicitud de préstamo."""
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    if prestamo.estado != EstadoPrestamoEnum.SOLICITADO:
        raise HTTPException(status_code=400, detail=f"No se puede aprobar un préstamo en estado {prestamo.estado}")

    prestamo.estado = EstadoPrestamoEnum.APROBADO
    prestamo.fecha_aprobacion = datetime.now(timezone.utc)
    prestamo.fecha_limite = data.fecha_limite
    prestamo.notas_admin = data.notas_admin

    db.commit()
    db.refresh(prestamo)
    return prestamo


# CU-09: Rechazar solicitud (admin)
@router.post("/{prestamo_id}/rechazar", response_model=PrestamoRead)
def rechazar_prestamo(
    prestamo_id: UUID,
    data: PrestamoRechazar,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user),
):
    """CU-09: Admin rechaza una solicitud de préstamo."""
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    if prestamo.estado != EstadoPrestamoEnum.SOLICITADO:
        raise HTTPException(status_code=400, detail=f"No se puede rechazar un préstamo en estado {prestamo.estado}")

    prestamo.estado = EstadoPrestamoEnum.RECHAZADO
    prestamo.motivo_rechazo = data.motivo_rechazo

    db.commit()
    db.refresh(prestamo)
    return prestamo


# CU-09: Registrar entrega física (admin)
@router.post("/{prestamo_id}/entregar", response_model=PrestamoRead)
def entregar_prestamo(
    prestamo_id: UUID,
    data: PrestamoEntregar,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user),
):
    """CU-09: Admin registra la entrega física del material."""
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    if prestamo.estado != EstadoPrestamoEnum.APROBADO:
        raise HTTPException(status_code=400, detail=f"Solo se puede entregar un préstamo APROBADO, no {prestamo.estado}")

    prestamo.estado = EstadoPrestamoEnum.ENTREGADO
    prestamo.fecha_entrega = datetime.now(timezone.utc)
    if data.notas_admin:
        prestamo.notas_admin = (prestamo.notas_admin or "") + f"\n[Entrega] {data.notas_admin}"

    db.commit()
    db.refresh(prestamo)
    return prestamo


# CU-10: Registrar devolución + evaluación (admin)
@router.post("/{prestamo_id}/devolver", response_model=PrestamoRead)
def devolver_prestamo(
    prestamo_id: UUID,
    data: PrestamoDevolver,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user),
):
    """CU-10: Admin registra devolución con evaluación del estado físico."""
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    if prestamo.estado not in [EstadoPrestamoEnum.ENTREGADO, EstadoPrestamoEnum.VENCIDO]:
        raise HTTPException(
            status_code=400,
            detail=f"Solo se puede devolver un préstamo ENTREGADO o VENCIDO, no {prestamo.estado}"
        )

    prestamo.estado = EstadoPrestamoEnum.DEVUELTO
    prestamo.fecha_devolucion = datetime.now(timezone.utc)
    prestamo.evaluacion_estado = data.evaluacion_estado
    prestamo.evaluacion_notas = data.evaluacion_notas

    # Si el estado es MALO, agregar nota de alerta a la carta
    if data.evaluacion_estado.value == "MALO":
        carta = db.query(Carta).filter(Carta.id == prestamo.carta_id).first()
        if carta:
            alerta = f"\n⚠️ DAÑO DETECTADO ({datetime.now(timezone.utc).strftime('%Y-%m-%d')}): {data.evaluacion_notas or 'Sin detalles'}"
            carta.notas = (carta.notas or "") + alerta

    db.commit()
    db.refresh(prestamo)
    return prestamo
