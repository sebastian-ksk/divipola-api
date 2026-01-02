import httpx
import asyncio
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.municipio import Municipio
from app.repositories.municipio_repository import MunicipioRepository
from app.core.redis_client import delete_cache

logger = logging.getLogger(__name__)

DATA_URL = "https://www.datos.gov.co/resource/gdxc-w37w.json"


def init_db():
    """Crea las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)


async def fetch_data():
    """Obtiene los datos del API de Datos Abiertos Colombia"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        logger.info(f"Obteniendo datos de: {DATA_URL}")
        response = await client.get(DATA_URL)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Datos obtenidos exitosamente: {len(data)} registros")
        return data


def save_municipios(data: list, db: Session):
    """Guarda los municipios en la base de datos"""
    repository = MunicipioRepository(db)
    saved = 0
    updated = 0
    
    logger.info("Procesando registros...")
    for item in data:
        municipio_data = {
            "cod_dpto": item.get("cod_dpto", ""),
            "dpto": item.get("dpto", ""),
            "cod_mpio": item.get("cod_mpio", ""),
            "nom_mpio": item.get("nom_mpio", ""),
            "tipo_municipio": item.get("tipo_municipio", ""),
            "longitud": item.get("longitud", ""),
            "latitud": item.get("latitud", ""),
            "pdet": False,  # Por defecto False hasta definir fuente
            "zomac": False  # Por defecto False hasta definir fuente
        }
        
        # Verificar si el municipio ya existe
        existing = repository.get_by_cod_mpio(municipio_data["cod_mpio"])
        
        if existing:
            # Actualizar datos existentes
            repository.update(existing, municipio_data)
            updated += 1
        else:
            # Crear nuevo municipio
            repository.create(municipio_data)
            saved += 1
    
    logger.info(f"Procesamiento completado: {saved} nuevos, {updated} actualizados")
    return saved, updated


async def main():
    """Función principal para recolectar datos"""
    try:
        logger.info("Inicializando base de datos...")
        init_db()
        
        logger.info("Obteniendo datos del API de Datos Abiertos Colombia...")
        data = await fetch_data()
        
        logger.info("Guardando datos en la base de datos...")
        db = SessionLocal()
        try:
            saved, updated = save_municipios(data, db)
            logger.info(f"✓ Municipios nuevos: {saved}")
            logger.info(f"✓ Municipios actualizados: {updated}")
            
            # Limpiar cache
            logger.info("Limpiando cache de Redis...")
            delete_cache("municipios:*")
            delete_cache("departamentos:*")
            logger.info("✓ Cache limpiado exitosamente")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error al guardar datos: {e}", exc_info=True)
            raise
        finally:
            db.close()
        
        logger.info("✓ Proceso de recolección completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en el proceso de recolección: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())

