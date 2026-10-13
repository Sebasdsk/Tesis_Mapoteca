"""
Reglas de negocio de préstamos.
"""
from datetime import date
from sqlalchemy.orm import Session

from app.models.prestamo import Prestamo, EstadoPrestamoEnum


def actualizar_prestamos_vencidos(db: Session) -> int:
    """
    Marca como VENCIDO todo préstamo ENTREGADO cuya fecha_limite ya pasó.

    Se ejecuta on-the-fly al consultar/solicitar préstamos, porque no hay un
    scheduler en el entorno de despliegue. Devuelve cuántos se actualizaron.
    """
    hoy = date.today()
    vencidos = db.query(Prestamo).filter(
        Prestamo.estado == EstadoPrestamoEnum.ENTREGADO,
        Prestamo.fecha_limite.isnot(None),
        Prestamo.fecha_limite < hoy,
    ).all()

    for prestamo in vencidos:
        prestamo.estado = EstadoPrestamoEnum.VENCIDO

    if vencidos:
        db.commit()

    return len(vencidos)
