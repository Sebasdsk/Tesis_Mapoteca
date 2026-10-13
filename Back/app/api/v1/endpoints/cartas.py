"""
Carta management endpoints - CU-03: Registrar Carta Individual
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import csv
import io
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.dependencies import get_db, get_current_admin_user, get_current_active_user
from app.models.usuario import Usuario
from app.models.carta import Carta, TipoCartaEnum, DisponibilidadEnum
from app.models.consulta import ConsultaCatalogo
from app.models.prestamo import Prestamo, EstadoPrestamoEnum
from app.schemas.carta import (
    CartaCreate,
    CartaRead,
    CartaUpdate,
    CartaSimple,
    CartaBaja,
    CargaMasivaResult,
    CargaMasivaResultRow
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
    current_user: Usuario = Depends(get_current_active_user)
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
    
    # Register search query (CU-07 Audit)
    if search or tipo_carta or disponibilidad or estado_republica or escala:
        filtros = {}
        if tipo_carta: filtros["tipo_carta"] = str(tipo_carta)
        if disponibilidad: filtros["disponibilidad"] = str(disponibilidad)
        if estado_republica: filtros["estado_republica"] = estado_republica
        if escala: filtros["escala"] = escala
        
        nueva_consulta = ConsultaCatalogo(
            usuario_id=current_user.id,
            termino_busqueda=search,
            filtros=filtros
        )
        db.add(nueva_consulta)
        db.commit()
    
    return cartas


@router.get("/{carta_id}", response_model=CartaRead)
def get_carta(
    carta_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
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
    
    # Register consulta in consultas_catalogo table (CU-07 Audit)
    nueva_consulta = ConsultaCatalogo(
        usuario_id=current_user.id,
        carta_id=carta.id
    )
    db.add(nueva_consulta)
    db.commit()
    
    return carta


@router.get("/nomenclatura/{nomenclatura}", response_model=CartaRead)
def get_carta_by_nomenclatura(
    nomenclatura: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
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
    
    # Verify no active prestamos before deleting
    prestamo_activo = db.query(Prestamo).filter(
        Prestamo.carta_id == carta_id,
        Prestamo.estado.in_([
            EstadoPrestamoEnum.SOLICITADO,
            EstadoPrestamoEnum.APROBADO,
            EstadoPrestamoEnum.ENTREGADO,
            EstadoPrestamoEnum.VENCIDO
        ])
    ).first()
    
    if prestamo_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la carta porque tiene un préstamo activo o pendiente. "
                   "Considére darla de baja en su lugar."
        )
    
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

# CU-04: Carga Masiva de Cartas
@router.post("/carga-masiva", response_model=CargaMasivaResult)
async def carga_masiva_cartas(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user),
):
    """
    CU-04: Importacion masiva de cartas desde archivo CSV.
    Columnas esperadas: nomenclatura,nombre,escala,tipo_carta,estado_republica,zona_utm,elipsoide,disponibilidad,notas
    """
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV (.csv)")
    
    try:
        content = await file.read()
        decoded = content.decode('utf-8-sig')  # utf-8-sig handles BOM from Excel
    except UnicodeDecodeError:
        try:
            decoded = content.decode('latin-1')
        except Exception:
            raise HTTPException(status_code=400, detail="No se pudo decodificar el archivo. Use codificacion UTF-8.")
    
    reader = csv.DictReader(io.StringIO(decoded))
    
    # Flexible header mapping
    header_mapping = {
        'nombre': ['nombre', 'nombre de la carta', 'nombre_carta', 'title'],
        'tipo_carta': ['tipo_carta', 'tipo de carta', 'tipo'],
        'escala': ['escala', 'scale'],
        'proyeccion_cartografica': ['proyeccion_cartografica', 'proyeccion', 'proyección', 'proyeccion cartografica', 'proyección cartográfica'],
        'elipsoide': ['elipsoide', 'elipsoide de referencia', 'elipsoide_referencia', 'elipsoide de referencia', 'elipsoide de referencia'],
        'zona_utm': ['zona_utm', 'zona utm', 'zona'],
        'coordenadas_utm_x': ['coordenadas_utm_x', 'coordenadas utm x', 'x', 'utm x', 'coordenada utm x'],
        'coordenadas_utm_y': ['coordenadas_utm_y', 'coordenadas utm y', 'y', 'utm y', 'coordenada utm y'],
        'coordenadas_latitud': ['coordenadas_latitud', 'coordenadas geodesicas latitud', 'coordenadas geodésicas latitud', 'latitud', 'latitud geodesica', 'latitud geodésica'],
        'coordenadas_longitud': ['coordenadas_longitud', 'coordenadas geodesicas longitud', 'coordenadas geodésicas longitud', 'longitud', 'longitud geodesica', 'longitud geodésica'],
        'limites_detalle': ['limites_detalle', 'limites', 'límites', 'limite', 'límite'],
        'nomenclatura': ['nomenclatura', 'nomeclatura', 'clave', 'codigo', 'código'],
        'fecha_edicion': ['fecha_edicion', 'fecha de edición', 'fecha de edicion', 'año', 'anio', 'fecha', 'fecha de edicion'],
        'estado_republica': ['estado_republica', 'estado', 'estados', 'estado de la republica', 'estado de la república'],
        'disponibilidad': ['disponibilidad', 'status', 'disponible'],
        'notas': ['notas', 'notas_adicionales', 'comentarios', 'comentario', 'notes']
    }

    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="El archivo CSV esta vacio o no tiene encabezados")

    import unicodedata
    import re
    from datetime import date, datetime

    def clean_header(h):
        h = h.strip().lower()
        h = ''.join(c for c in unicodedata.normalize('NFD', h) if unicodedata.category(c) != 'Mn')
        h = h.replace('_', ' ').replace('-', ' ')
        return h

    # Map actual CSV headers to standard database fields
    field_map = {}
    for db_field, aliases in header_mapping.items():
        for alias in aliases:
            cleaned_alias = clean_header(alias)
            for h in reader.fieldnames:
                if clean_header(h) == cleaned_alias:
                    field_map[db_field] = h
                    break
            if db_field in field_map:
                break

    # Required database fields
    required_fields = ['nomenclatura', 'nombre', 'escala', 'tipo_carta']
    missing = [req for req in required_fields if req not in field_map]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Faltan columnas obligatorias (o no se pudieron mapear): {', '.join(missing)}. Columnas encontradas: {', '.join(reader.fieldnames)}"
        )

    def parse_csv_date(val: str) -> Optional[date]:
        val = val.strip()
        if not val:
            return None
        # Try 4-digit year
        if val.isdigit() and len(val) == 4:
            try:
                return date(int(val), 1, 1)
            except ValueError:
                pass
        # Try different formats
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(val, fmt).date()
            except ValueError:
                continue
        return None

    def normalize_estados(val: str) -> Optional[str]:
        if not val:
            return None
        # Replace " Y " or " y " with comma
        val_clean = re.sub(r'\s+[yY]\s+', ', ', val)
        parts = [p.strip().title() for p in val_clean.split(',') if p.strip()]
        # Fix casing for known articles in states
        parts = [p.replace(" De ", " de ").replace(" D.f.", " D.F.").replace(" Cdmx", " CDMX") for p in parts]
        # Max length check to avoid truncating
        return ", ".join(parts)[:100] if parts else None

    resultados = []
    exitosas = 0
    errores_count = 0
    
    tipos_validos = {e.value: e for e in TipoCartaEnum}
    disponibilidad_validos = {e.value: e for e in DisponibilidadEnum}
    
    # Iterate through rows
    for i, row in enumerate(reader, start=2):
        # Check if row is completely empty
        if not any(row.values()):
            continue

        # Get values using field_map
        def get_val(field_name):
            col_name = field_map.get(field_name)
            if col_name and col_name in row:
                return (row[col_name] or '').strip()
            return ''

        nomenclatura = get_val('nomenclatura').upper()
        nombre = get_val('nombre')
        escala = get_val('escala')
        tipo_carta_str = get_val('tipo_carta').upper()
        
        # Validations
        if not nomenclatura:
            errores_count += 1
            resultados.append(CargaMasivaResultRow(
                fila=i, nomenclatura='', nombre=nombre, exito=False,
                mensaje='Nomenclatura es obligatoria'
            ))
            continue
        
        if not nombre:
            errores_count += 1
            resultados.append(CargaMasivaResultRow(
                fila=i, nomenclatura=nomenclatura, nombre='', exito=False,
                mensaje='Nombre es obligatorio'
            ))
            continue
        
        if not escala:
            errores_count += 1
            resultados.append(CargaMasivaResultRow(
                fila=i, nomenclatura=nomenclatura, nombre=nombre, exito=False,
                mensaje='Escala es obligatoria'
            ))
            continue
        
        # Normalize escala format (replace spaces)
        escala = escala.replace(' ', '')
        # If it doesn't start with 1:, add it
        if escala and not escala.startswith('1:'):
            escala = f"1:{escala}"

        if tipo_carta_str not in tipos_validos:
            errores_count += 1
            resultados.append(CargaMasivaResultRow(
                fila=i, nomenclatura=nomenclatura, nombre=nombre, exito=False,
                mensaje=f'Tipo de carta invalido: {tipo_carta_str}. Validos: {", ".join(tipos_validos.keys())}'
            ))
            continue
        
        # Check duplicate in DB
        existing = db.query(Carta).filter(Carta.nomenclatura == nomenclatura).first()
        if existing:
            errores_count += 1
            resultados.append(CargaMasivaResultRow(
                fila=i, nomenclatura=nomenclatura, nombre=nombre, exito=False,
                mensaje=f'Ya existe una carta con nomenclatura {nomenclatura}'
            ))
            continue
        
        # Check duplicate within this CSV batch
        nomenclaturas_procesadas = [r.nomenclatura for r in resultados if r.exito]
        if nomenclatura in nomenclaturas_procesadas:
            errores_count += 1
            resultados.append(CargaMasivaResultRow(
                fila=i, nomenclatura=nomenclatura, nombre=nombre, exito=False,
                mensaje=f'Nomenclatura duplicada en el archivo CSV'
            ))
            continue
        
        disponibilidad_str = get_val('disponibilidad').upper()
        disponibilidad = disponibilidad_validos.get(disponibilidad_str, DisponibilidadEnum.FISICA)
        
        # Determine TipoCoordenadas
        utm_x = get_val('coordenadas_utm_x')
        utm_y = get_val('coordenadas_utm_y')
        lat = get_val('coordenadas_latitud')
        lng = get_val('coordenadas_longitud')
        limites = get_val('limites_detalle')
        
        tipo_coord = None
        from app.models.carta import TipoCoordenadasEnum
        if utm_x and utm_y and lat and lng:
            tipo_coord = TipoCoordenadasEnum.AMBAS
        elif utm_x and utm_y:
            tipo_coord = TipoCoordenadasEnum.UTM
        elif lat and lng:
            tipo_coord = TipoCoordenadasEnum.GEODESICO
        elif limites:
            tipo_coord = TipoCoordenadasEnum.LIMITES

        try:
            # Parse year/date
            f_edicion = parse_csv_date(get_val('fecha_edicion'))
            
            carta = Carta(
                nomenclatura=nomenclatura,
                nombre=nombre,
                escala=escala,
                tipo_carta=tipos_validos[tipo_carta_str],
                proyeccion_cartografica=get_val('proyeccion_cartografica') or None,
                elipsoide=get_val('elipsoide') or None,
                zona_utm=get_val('zona_utm') or None,
                coordenadas_utm_x=utm_x or None,
                coordenadas_utm_y=utm_y or None,
                coordenadas_latitud=lat or None,
                coordenadas_longitud=lng or None,
                limites_detalle=limites or None,
                tipo_coordenadas=tipo_coord,
                fecha_edicion=f_edicion,
                estado_republica=normalize_estados(get_val('estado_republica')),
                disponibilidad=disponibilidad,
                notas=get_val('notas') or None,
            )
            db.add(carta)
            db.flush()
            
            exitosas += 1
            resultados.append(CargaMasivaResultRow(
                fila=i, nomenclatura=nomenclatura, nombre=nombre, exito=True,
                mensaje='Carta registrada exitosamente'
            ))
        except Exception as e:
            db.rollback()
            errores_count += 1
            resultados.append(CargaMasivaResultRow(
                fila=i, nomenclatura=nomenclatura, nombre=nombre, exito=False,
                mensaje=f'Error al guardar: {str(e)}'
            ))
    
    # Commit all successful inserts
    if exitosas > 0:
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al guardar en la base de datos: {str(e)}")
    
    return CargaMasivaResult(
        total_procesadas=len(resultados),
        exitosas=exitosas,
        errores=errores_count,
        detalle=resultados
    )

