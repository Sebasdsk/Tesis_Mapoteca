"""
Reportes y Estadísticas endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime

from app.core.dependencies import get_db, get_current_admin_or_maestro
from app.models.usuario import Usuario
from app.models.carta import Carta
from app.models.prestamo import Prestamo, EstadoPrestamoEnum
from app.models.consulta import ConsultaCatalogo
from app.services.prestamos import actualizar_prestamos_vencidos
from app.schemas.reporte import (
    ReporteGeneral,
    CartaEstadistica,
    PrestamoVencido,
    PrestamoActivo,
    DistribucionUsuarios,
    ActividadMensual,
)

router = APIRouter()

@router.get("/general", response_model=ReporteGeneral)
def get_reporte_general(
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_or_maestro)
):
    """Obtener estadísticas generales de la mapoteca"""
    actualizar_prestamos_vencidos(db)

    total_usuarios = db.query(Usuario).count()
    total_cartas = db.query(Carta).count()
    
    prestamos_activos = db.query(Prestamo).filter(
        Prestamo.estado.in_([
            EstadoPrestamoEnum.SOLICITADO, 
            EstadoPrestamoEnum.APROBADO, 
            EstadoPrestamoEnum.ENTREGADO, 
            EstadoPrestamoEnum.VENCIDO
        ])
    ).count()
    
    consultas_totales = db.query(ConsultaCatalogo).count()
    
    return {
        "total_usuarios": total_usuarios,
        "total_cartas": total_cartas,
        "prestamos_activos": prestamos_activos,
        "consultas_totales": consultas_totales
    }

@router.get("/cartas-mas-buscadas", response_model=List[CartaEstadistica])
def get_cartas_mas_buscadas(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_or_maestro)
):
    """Top cartas más consultadas"""
    # Contar agrupando por carta_id
    resultados = db.query(
        Carta.id.label('carta_id'),
        Carta.nomenclatura,
        Carta.nombre,
        Carta.escala,
        func.count(ConsultaCatalogo.id).label('cantidad')
    ).join(ConsultaCatalogo, Carta.id == ConsultaCatalogo.carta_id)\
    .group_by(Carta.id)\
    .order_by(desc('cantidad'))\
    .limit(limit).all()
    
    return [
        {
            "carta_id": r.carta_id,
            "nomenclatura": r.nomenclatura,
            "nombre": r.nombre,
            "escala": r.escala,
            "cantidad": r.cantidad
        } for r in resultados
    ]

@router.get("/cartas-mas-prestadas", response_model=List[CartaEstadistica])
def get_cartas_mas_prestadas(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_or_maestro)
):
    """Top cartas más solicitadas para préstamo"""
    resultados = db.query(
        Carta.id.label('carta_id'),
        Carta.nomenclatura,
        Carta.nombre,
        Carta.escala,
        func.count(Prestamo.id).label('cantidad')
    ).join(Prestamo, Carta.id == Prestamo.carta_id)\
    .group_by(Carta.id)\
    .order_by(desc('cantidad'))\
    .limit(limit).all()
    
    return [
        {
            "carta_id": r.carta_id,
            "nomenclatura": r.nomenclatura,
            "nombre": r.nombre,
            "escala": r.escala,
            "cantidad": r.cantidad
        } for r in resultados
    ]

@router.get("/prestamos-vencidos", response_model=List[PrestamoVencido])
def get_prestamos_vencidos(
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_or_maestro)
):
    """Obtener lista de préstamos que han vencido"""
    actualizar_prestamos_vencidos(db)

    hoy = datetime.now().date()
    
    vencidos = db.query(Prestamo).filter(
        Prestamo.estado == EstadoPrestamoEnum.VENCIDO
    ).all()
    
    # También buscar los ENTREGADOS cuya fecha límite ya pasó pero que el cronjob tal vez no actualizó aún
    entregados_vencidos = db.query(Prestamo).filter(
        Prestamo.estado == EstadoPrestamoEnum.ENTREGADO,
        Prestamo.fecha_limite < hoy
    ).all()
    
    todos_vencidos = vencidos + entregados_vencidos
    
    resultado = []
    for p in todos_vencidos:
        # Calcular días de retraso
        dias = 0
        if p.fecha_limite:
            delta = hoy - p.fecha_limite
            dias = delta.days if delta.days > 0 else 0
            
        resultado.append({
            "prestamo_id": p.id,
            "usuario_nombre": p.usuario.nombre_completo,
            "usuario_email": p.usuario.email,
            "carta_nomenclatura": p.carta.nomenclatura,
            "carta_nombre": p.carta.nombre,
            "fecha_solicitud": p.fecha_solicitud,
            "fecha_limite": p.fecha_limite,
            "dias_retraso": dias
        })
        
    # Ordenar por días de retraso descendente
    resultado.sort(key=lambda x: x["dias_retraso"], reverse=True)
    return resultado

@router.get("/prestamos-activos", response_model=List[PrestamoActivo])
def get_prestamos_activos(
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_or_maestro)
):
    """Cartas actualmente prestadas (ENTREGADO) con datos de contacto del usuario."""
    actualizar_prestamos_vencidos(db)

    hoy = datetime.now().date()
    activos = db.query(Prestamo).filter(
        Prestamo.estado == EstadoPrestamoEnum.ENTREGADO
    ).order_by(Prestamo.fecha_entrega.desc()).all()

    resultado = []
    for p in activos:
        dias = 0
        if p.fecha_limite:
            delta = hoy - p.fecha_limite
            dias = delta.days if delta.days > 0 else 0

        resultado.append({
            "prestamo_id": p.id,
            "usuario_nombre": p.usuario.nombre_completo,
            "usuario_email": p.usuario.email,
            "usuario_telefono": p.usuario.telefono,
            "usuario_identificacion": p.usuario.numero_identificacion,
            "carta_nomenclatura": p.carta.nomenclatura,
            "carta_nombre": p.carta.nombre,
            "fecha_entrega": p.fecha_entrega,
            "fecha_limite": p.fecha_limite,
            "dias_retraso": dias,
        })

    return resultado

@router.get("/distribucion-usuarios", response_model=List[DistribucionUsuarios])
def get_distribucion_usuarios(
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_or_maestro)
):
    """Distribucion de usuarios registrados por tipo"""
    resultados = db.query(
        Usuario.tipo_usuario,
        func.count(Usuario.id).label('cantidad')
    ).filter(
        Usuario.activo == True
    ).group_by(Usuario.tipo_usuario).all()
    
    return [
        {"tipo_usuario": r.tipo_usuario.value if hasattr(r.tipo_usuario, 'value') else str(r.tipo_usuario), "cantidad": r.cantidad}
        for r in resultados
    ]


@router.get("/actividad-mensual", response_model=List[ActividadMensual])
def get_actividad_mensual(
    meses: int = 12,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_or_maestro)
):
    """Actividad de prestamos agrupada por mes (ultimos N meses)"""
    from datetime import timedelta
    fecha_inicio = datetime.now() - timedelta(days=meses * 30)
    
    resultados = db.query(
        func.to_char(Prestamo.fecha_solicitud, 'YYYY-MM').label('mes'),
        func.count(Prestamo.id).label('cantidad')
    ).filter(
        Prestamo.fecha_solicitud >= fecha_inicio
    ).group_by(
        func.to_char(Prestamo.fecha_solicitud, 'YYYY-MM')
    ).order_by('mes').all()
    
    return [{"mes": r.mes, "cantidad": r.cantidad} for r in resultados]

