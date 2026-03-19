"""
Database initialization script

Creates tables and loads initial data:
- Admin user
- Sample cartas for testing
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.usuario import Usuario, TipoUsuarioEnum
from app.models.carta import Carta, TipoCartaEnum, DisponibilidadEnum, TipoCoordenadasEnum
from app.core.security import get_password_hash
from app.core.config import settings
from datetime import date
import uuid


def init_db(db: Session) -> None:
    """Initialize database with initial data"""
    
    # Create admin user if it doesn't exist
    admin = db.query(Usuario).filter(
        Usuario.tipo_usuario == TipoUsuarioEnum.ADMIN
    ).first()
    
    if not admin:
        print("Creating admin user...")
        admin = Usuario(
            id=uuid.uuid4(),
            tipo_usuario=TipoUsuarioEnum.ADMIN,
            numero_identificacion="ADMIN001",
            nombre_completo=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password_hash=get_password_hash(settings.ADMIN_PASSWORD),
            debe_cambiar_password=False,  # Admin doesn't need to change password
            activo=True
        )
        db.add(admin)
        print(f"✓ Admin user created: {settings.ADMIN_USERNAME}")
        print(f"  Email: {settings.ADMIN_EMAIL}")
        print(f"  Password: {settings.ADMIN_PASSWORD}")
        print("  ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!")
    
    # Create sample users
    sample_users = [
        {
            "tipo_usuario": TipoUsuarioEnum.ESTUDIANTE,
            "numero_identificacion": "0123456-7",
            "nombre_completo": "Juan Pérez García",
            "email": "juan.perez@uas.edu.mx",
            "password": "Estudiante123"
        },
        {
            "tipo_usuario": TipoUsuarioEnum.MAESTRO,
            "numero_identificacion": "EMP-001",
            "nombre_completo": "Dr. María García López",
            "email": "maria.garcia@uas.edu.mx",
            "password": "Maestro123"
        },
        {
            "tipo_usuario": TipoUsuarioEnum.EXTERNO,
            "numero_identificacion": None,
            "nombre_completo": "Carlos Rodríguez",
            "email": "carlos@externo.com",
            "institucion": "Instituto Tecnológico de Los Mochis",
            "password": None
        }
    ]
    
    for user_data in sample_users:
        existing = db.query(Usuario).filter(
            Usuario.numero_identificacion == user_data.get("numero_identificacion")
        ).first() if user_data.get("numero_identificacion") else None
        
        if not existing:
            user = Usuario(
                id=uuid.uuid4(),
                tipo_usuario=user_data["tipo_usuario"],
                numero_identificacion=user_data.get("numero_identificacion"),
                nombre_completo=user_data["nombre_completo"],
                email=user_data.get("email"),
                institucion=user_data.get("institucion"),
                password_hash=get_password_hash(user_data["password"]) if user_data.get("password") else None,
                debe_cambiar_password=True if user_data.get("password") else False,
                activo=True
            )
            db.add(user)
            print(f"✓ Sample user created: {user_data['nombre_completo']} ({user_data['tipo_usuario']})")
    
    # Create sample cartas
    sample_cartas = [
        {
            "nomenclatura": "G13-A12",
            "nombre": "Culiacán",
            "escala": "1:50,000",
            "tipo_carta": TipoCartaEnum.TOPOGRAFICA,
            "elipsoide": "GRS80",
            "zona_utm": "13N",
            "tipo_coordenadas": TipoCoordenadasEnum.GEODESICO,
            "limites_norte": 25.00,
            "limites_sur": 24.75,
            "limites_este": -107.25,
            "limites_oeste": -107.50,
            "fecha_edicion": date(1985, 10, 15),
            "estado_republica": "Sinaloa",
            "disponibilidad": DisponibilidadEnum.AMBAS,
            "url_inegi": "https://www.inegi.org.mx/app/mapas/",
            "metadata_inegi": {
                "año_digital": 2024,
                "formatos_disponibles": ["PDF", "SHP", "KML"],
                "escala_digital": "1:50,000",
                "fecha_actualizacion": "2024-01-15"
            }
        },
        {
            "nomenclatura": "G13-C56",
            "nombre": "Culiacán Rosales",
            "escala": "1:50,000",
            "tipo_carta": TipoCartaEnum.TOPOGRAFICA,
            "elipsoide": "GRS80",
            "zona_utm": "13N",
            "tipo_coordenadas": TipoCoordenadasEnum.GEODESICO,
            "limites_norte": 24.85,
            "limites_sur": 24.60,
            "limites_este": -107.30,
            "limites_oeste": -107.55,
            "fecha_edicion": date(1985, 8, 20),
            "estado_republica": "Sinaloa",
            "disponibilidad": DisponibilidadEnum.FISICA
        },
        {
            "nomenclatura": "F13-A23",
            "nombre": "Mazatlán Sur",
            "escala": "1:50,000",
            "tipo_carta": TipoCartaEnum.HIDROLOGICA,
            "elipsoide": "WGS84",
            "zona_utm": "13N",
            "tipo_coordenadas": TipoCoordenadasEnum.GEODESICO,
            "limites_norte": 23.30,
            "limites_sur": 23.05,
            "limites_este": -106.35,
            "limites_oeste": -106.60,
            "fecha_edicion": date(1984, 5, 10),
            "estado_republica": "Sinaloa",
            "disponibilidad": DisponibilidadEnum.FISICA
        },
        {
            "nomenclatura": "G12-B12",
            "nombre": "Los Mochis",
            "escala": "1:250,000",
            "tipo_carta": TipoCartaEnum.TOPOGRAFICA,
            "elipsoide": "Clarke 1866",
            "zona_utm": "12N",
            "tipo_coordenadas": TipoCoordenadasEnum.ALTOMETRICO,
            "limites_norte": 26.00,
            "limites_sur": 25.50,
            "limites_este": -108.50,
            "limites_oeste": -109.00,
            "fecha_edicion": date(1983, 12, 1),
            "estado_republica": "Sinaloa",
            "disponibilidad": DisponibilidadEnum.FISICA
        },
        {
            "nomenclatura": "E13-B21",
            "nombre": "Chihuahua Región Minera",
            "escala": "1:50,000",
            "tipo_carta": TipoCartaEnum.GEOLOGICA,
            "elipsoide": "GRS80",
            "zona_utm": "13N",
            "tipo_coordenadas": TipoCoordenadasEnum.GEODESICO,
            "fecha_edicion": date(1985, 6, 15),
            "estado_republica": "Chihuahua",
            "disponibilidad": DisponibilidadEnum.FISICA,
            "notas": "Carta utilizada frecuentemente en prácticas de minería"
        },
        {
            "nomenclatura": "H14-D35",
            "nombre": "Sonora Hermosillo",
            "escala": "1:50,000",
            "tipo_carta": TipoCartaEnum.TOPOGRAFICA,
            "elipsoide": "WGS84",
            "zona_utm": "12N",
            "fecha_edicion": date(1984, 3, 20),
            "estado_republica": "Sonora",
            "disponibilidad": DisponibilidadEnum.EXTRAVIADA,
            "notas": "Carta reportada como extraviada en inventario 2023"
        },
        {
            "nomenclatura": "F14-A11",
            "nombre": "Zacatecas Norte",
            "escala": "1:50,000",
            "tipo_carta": TipoCartaEnum.EDAFOLOGICA,
            "elipsoide": "GRS80",
            "fecha_edicion": date(1985, 11, 5),
            "estado_republica": "Zacatecas",
            "disponibilidad": DisponibilidadEnum.FISICA
        },
        {
            "nomenclatura": "DIGITAL-001",
            "nombre": "México Digital Completo",
            "escala": "1:1,000,000",
            "tipo_carta": TipoCartaEnum.TOPOGRAFICA,
            "estado_republica": "Nacional",
            "disponibilidad": DisponibilidadEnum.SOLO_DIGITAL,
            "url_inegi": "https://www.inegi.org.mx/app/mapas/",
            "metadata_inegi": {
                "año_digital": 2024,
                "formatos_disponibles": ["PDF", "SHP", "KML", "GeoJSON"],
                "escala_digital": "1:1,000,000"
            },
            "notas": "Referencia digital de INEGI - no existe versión física en la mapoteca"
        }
    ]
    
    for carta_data in sample_cartas:
        existing = db.query(Carta).filter(
            Carta.nomenclatura == carta_data["nomenclatura"]
        ).first()
        
        if not existing:
            carta = Carta(**carta_data)
            db.add(carta)
            print(f"✓ Sample carta created: {carta_data['nomenclatura']} - {carta_data['nombre']}")
    
    # Commit all changes
    db.commit()
    print("\n✅ Database initialization completed successfully!")
    print(f"\nTotal users: {db.query(Usuario).count()}")
    print(f"Total cartas: {db.query(Carta).count()}")


def main():
    """Main function to initialize database"""
    print("=" * 60)
    print("Database Initialization Script")
    print("Sistema de Gestión de Mapoteca UAS")
    print("=" * 60)
    print()
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")
    print()
    
    # Initialize data
    db = SessionLocal()
    try:
        init_db(db)
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    print()
    print("=" * 60)
    print("🚀 You can now start the server with: uvicorn app.main:app --reload")
    print("=" * 60)


if __name__ == "__main__":
    main()
