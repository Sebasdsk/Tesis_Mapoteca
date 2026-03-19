"""
Carta management endpoints - CU-03: Registrar Carta Individual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.dependencies import get_db, get_current_admin_user, get_current_user
from app.models.usuario import Usuario
from app.models.carta import Carta, TipoCartaEnum, DisponibilidadEnum
from app.schemas.carta import (
    CartaCreate,
    CartaRead,
    CartaUpdate,
    CartaSimple,
    CartaBaja
)


router = APIRouter()


@router.post("/", response_model=CartaRead, status_code=status.HTTP_201_CREATED)
def create_carta(
    carta_data: CartaCreate,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-03: Registrar Carta Individual
    
    Create a new carta in the system (admin only).
    Validates that nomenclatura is unique.
    """
    # Validate unique nomenclatura
    existing = db.query(Carta).filter(
        Carta.nomenclatura == carta_data.nomenclatura.upper()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La nomenclatura {carta_data.nomenclatura} ya está registrada. "
                   f"Carta existente: {existing.nombre}"
        )
    
    # Create new carta
    new_carta = Carta(**carta_data.dict())
    
    db.add(new_carta)
    db.commit()
    db.refresh(new_carta)
    
    return new_carta


@router.get("/", response_model=List[CartaSimple])
def list_cartas(
    skip: int = 0,
    limit: int = 50,
    tipo_carta: Optional[TipoCartaEnum] = None,
    disponibilidad: Optional[DisponibilidadEnum] = None,
    estado_republica: Optional[str] = None,
    escala: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    CU-06: Búsqueda y Filtrado (implementación parcial)
    
    List all cartas with optional filters.
    This is a simplified version - full search will be in CU-06.
    """
    query = db.query(Carta)
    
    # Apply filters
    if tipo_carta:
        query = query.filter(Carta.tipo_carta == tipo_carta)
    
    if disponibilidad:
        query = query.filter(Carta.disponibilidad == disponibilidad)
    
    if estado_republica:
        query = query.filter(Carta.estado_republica.ilike(f"%{estado_republica}%"))
    
    if escala:
        query = query.filter(Carta.escala == escala)
    
    # Text search (simple - full implementation in CU-06)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Carta.nombre.ilike(search_term)) |
            (Carta.nomenclatura.ilike(search_term)) |
            (Carta.estado_republica.ilike(search_term))
        )
    
    # Order by creation date (newest first)
    query = query.order_by(Carta.created_at.desc())
    
    # Pagination
    cartas = query.offset(skip).limit(limit).all()
    
    return cartas


@router.get("/{carta_id}", response_model=CartaRead)
def get_carta(
    carta_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    CU-07: Consultar Ficha Técnica (implementación parcial)
    
    Get a specific carta by ID with all details.
    """
    carta = db.query(Carta).filter(Carta.id == carta_id).first()
    
    if not carta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carta no encontrada"
        )
    
    # TODO: Register consulta in consultas_catalogo table (CU-07 full implementation)
    
    return carta


@router.get("/nomenclatura/{nomenclatura}", response_model=CartaRead)
def get_carta_by_nomenclatura(
    nomenclatura: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    CU-07: Consultar Ficha Técnica por Nomenclatura
    
    Get a specific carta by its nomenclatura (INEGI code).
    """
    carta = db.query(Carta).filter(
        Carta.nomenclatura == nomenclatura.upper()
    ).first()
    
    if not carta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró una carta con nomenclatura {nomenclatura}"
        )
    
    return carta


@router.put("/{carta_id}", response_model=CartaRead)
def update_carta(
    carta_id: UUID,
    carta_data: CartaUpdate,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-05: Modificar Carta
    
    Update an existing carta (admin only).
    """
    carta = db.query(Carta).filter(Carta.id == carta_id).first()
    
    if not carta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carta no encontrada"
        )
    
    # Update fields
    update_data = carta_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(carta, field, value)
    
    db.commit()
    db.refresh(carta)
    
    return carta


@router.post("/{carta_id}/baja")
def dar_baja_carta(
    carta_id: UUID,
    baja_data: CartaBaja,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-05: Dar de Baja Carta (Expurgo)
    
    Mark a carta as unavailable due to loss, damage, or obsolescence.
    Does not delete the record (preserves history).
    """
    carta = db.query(Carta).filter(Carta.id == carta_id).first()
    
    if not carta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carta no encontrada"
        )
    
    # Determine new status based on motivo
    motivo_upper = baja_data.motivo.upper()
    
    if motivo_upper == "PERDIDA":
        carta.disponibilidad = DisponibilidadEnum.EXTRAVIADA
    elif motivo_upper in ["DETERIORO_IRREPARABLE", "OBSOLESCENCIA"]:
        carta.disponibilidad = DisponibilidadEnum.DANADA
    else:
        carta.disponibilidad = DisponibilidadEnum.DANADA
    
    # Add note
    nota_baja = f"BAJA - Motivo: {baja_data.motivo}"
    if baja_data.descripcion:
        nota_baja += f" - {baja_data.descripcion}"
    
    if carta.notas:
        carta.notas += f"\n\n{nota_baja}"
    else:
        carta.notas = nota_baja
    
    db.commit()
    db.refresh(carta)
    
    return {
        "message": "Carta dada de baja correctamente",
        "carta_id": str(carta.id),
        "nomenclatura": carta.nomenclatura,
        "nombre": carta.nombre,
        "nueva_disponibilidad": carta.disponibilidad,
        "motivo": baja_data.motivo
    }


@router.delete("/{carta_id}")
def delete_carta(
    carta_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-05: Eliminar Carta (Hard Delete)
    
    Permanently delete a carta from the system.
    Use with caution - prefer dar_baja_carta instead.
    """
    carta = db.query(Carta).filter(Carta.id == carta_id).first()
    
    if not carta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carta no encontrada"
        )
    
    # TODO: Verify no active prestamos before deleting
    
    nomenclatura = carta.nomenclatura
    nombre = carta.nombre
    
    db.delete(carta)
    db.commit()
    
    return {
        "message": "Carta eliminada permanentemente",
        "nomenclatura": nomenclatura,
        "nombre": nombre
    }


@router.get("/stats/summary")
def get_cartas_summary(
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    Get summary statistics of cartas
    
    Returns total count and breakdown by availability.
    """
    total = db.query(Carta).count()
    
    disponibles = db.query(Carta).filter(
        Carta.disponibilidad.in_([DisponibilidadEnum.FISICA, DisponibilidadEnum.AMBAS])
    ).count()
    
    solo_digital = db.query(Carta).filter(
        Carta.disponibilidad == DisponibilidadEnum.SOLO_DIGITAL
    ).count()
    
    extraviadas = db.query(Carta).filter(
        Carta.disponibilidad == DisponibilidadEnum.EXTRAVIADA
    ).count()
    
    danadas = db.query(Carta).filter(
        Carta.disponibilidad == DisponibilidadEnum.DANADA
    ).count()
    
    return {
        "total_cartas": total,
        "disponibles": disponibles,
        "solo_digital": solo_digital,
        "extraviadas": extraviadas,
        "danadas": danadas,
        "porcentaje_disponible": round((disponibles / total * 100) if total > 0 else 0, 2)
    }
