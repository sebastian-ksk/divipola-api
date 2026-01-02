import httpx
import asyncio
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal, engine, Base
from app.models.municipio import Municipio
from app.repositories.municipio_repository import MunicipioRepository
from app.core.redis_client import delete_cache
from app.core.config import get_settings
from app.core.zomac_data import get_zomac_pdet

logger = logging.getLogger(__name__)

# IDs de los datasets en datos.gov.co
DIVIPOLA_DATASET_ID = "gdxc-w37w"
DIVIPOLA_API_URL = "https://www.datos.gov.co/api/v3/views/gdxc-w37w/query.json"
PDET_DATASET_ID = "idrk-ba8y"
PDET_API_URL = "https://www.datos.gov.co/api/v3/views/idrk-ba8y/query.json"


def init_db():
    """Crea las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)


async def fetch_data():
    """Obtiene los datos del API de Datos Abiertos Colombia usando POST"""
    settings = get_settings()
    app_token = settings.datos_gov_app_token
    
    if not app_token:
        logger.warning("⚠️  DATOS_GOV_APP_TOKEN no configurado. Usando API sin autenticación (límites reducidos)")
        # Si no hay token, usar GET en lugar de POST
        return await fetch_data_without_token()
    
    headers = {
        "Content-Type": "application/json",
        "X-App-Token": app_token
    }
    
    # Paginación: obtener todos los registros en lotes
    all_data = []
    page_number = 1
    page_size = 5000  # Máximo permitido por la API
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            payload = {
                "query": "SELECT *",
                "page": {
                    "pageNumber": page_number,
                    "pageSize": page_size
                },
                "includeSynthetic": False
            }
            
            logger.info(f"Obteniendo página {page_number} de datos (lote de {page_size} registros)...")
            
            try:
                response = await client.post(
                    DIVIPOLA_API_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                page_data = response.json()
                
                # La API puede retornar los datos directamente o en un campo 'data'
                if isinstance(page_data, list):
                    records = page_data
                elif isinstance(page_data, dict) and "data" in page_data:
                    records = page_data["data"]
                else:
                    records = []
                
                if not records:
                    break
                
                all_data.extend(records)
                logger.info(f"✓ Página {page_number}: {len(records)} registros obtenidos")
                
                # Si obtenemos menos registros que el page_size, es la última página
                if len(records) < page_size:
                    break
                
                page_number += 1
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP al obtener página {page_number}: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error al obtener página {page_number}: {e}")
                raise
    
    logger.info(f"✓ Datos obtenidos exitosamente: {len(all_data)} registros totales")
    return all_data


async def fetch_data_without_token():
    """Obtiene datos usando GET cuando no hay app token (fallback)"""
    fallback_url = "https://www.datos.gov.co/resource/gdxc-w37w.json"
    logger.info(f"Usando método GET sin autenticación: {fallback_url}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Obtener todos los datos de una vez (sin paginación)
        response = await client.get(fallback_url, params={"$limit": 50000})
        response.raise_for_status()
        data = response.json()
        logger.info(f"✓ Datos obtenidos exitosamente: {len(data)} registros totales")
        return data


async def fetch_pdet_data():
    """Obtiene los datos de municipios PDET desde la API"""
    settings = get_settings()
    app_token = settings.datos_gov_app_token
    
    if not app_token:
        logger.warning("⚠️  DATOS_GOV_APP_TOKEN no configurado. No se pueden obtener datos PDET")
        return []
    
    headers = {
        "Content-Type": "application/json",
        "X-App-Token": app_token
    }
    
    # Paginación: obtener todos los registros en lotes
    all_data = []
    page_number = 1
    page_size = 5000
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            payload = {
                "query": "SELECT *",
                "page": {
                    "pageNumber": page_number,
                    "pageSize": page_size
                },
                "includeSynthetic": False
            }
            
            logger.info(f"Obteniendo página {page_number} de datos PDET (lote de {page_size} registros)...")
            
            try:
                response = await client.post(
                    PDET_API_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                page_data = response.json()
                
                # La API puede retornar los datos directamente o en un campo 'data'
                if isinstance(page_data, list):
                    records = page_data
                elif isinstance(page_data, dict) and "data" in page_data:
                    records = page_data["data"]
                else:
                    records = []
                
                if not records:
                    break
                
                all_data.extend(records)
                logger.info(f"✓ Página {page_number} PDET: {len(records)} registros obtenidos")
                
                # Si obtenemos menos registros que el page_size, es la última página
                if len(records) < page_size:
                    break
                
                page_number += 1
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP al obtener página PDET {page_number}: {e.response.status_code} - {e.response.text}")
                # Si falla, continuar sin datos PDET
                break
            except Exception as e:
                logger.error(f"Error al obtener página PDET {page_number}: {e}")
                break
    
    logger.info(f"✓ Datos PDET obtenidos exitosamente: {len(all_data)} registros totales")
    return all_data


def update_pdet_municipios(pdet_data: list, db: Session):
    """Actualiza los municipios marcándolos como PDET según los datos obtenidos y ZOMAC desde constantes"""
    repository = MunicipioRepository(db)
    updated = 0
    not_found = 0
    zomac_updated = 0
    
    logger.info("Actualizando municipios PDET...")
    
    # Crear un set con los códigos de municipios PDET
    # La API PDET usa 'cod_muni' que corresponde a 'cod_mpio' en nuestra BD
    pdet_codes = set()
    for item in pdet_data:
        cod_muni = item.get("cod_muni", "")
        if cod_muni:
            pdet_codes.add(cod_muni)
    
    logger.info(f"Total de códigos PDET únicos: {len(pdet_codes)}")
    
    # Primero, marcar todos los municipios como no PDET
    db.execute(text("UPDATE municipios SET pdet = false"))
    db.commit()
    
    # Luego, marcar los que están en la lista PDET y actualizar ZOMAC desde constantes
    for cod_mpio in pdet_codes:
        municipio = repository.get_by_cod_mpio(cod_mpio)
        if municipio:
            municipio.pdet = True
            # Actualizar ZOMAC desde constantes
            zomac_pdet = get_zomac_pdet(municipio.dpto, municipio.nom_mpio)
            if zomac_pdet["zomac"]:
                municipio.zomac = True
                zomac_updated += 1
            updated += 1
        else:
            not_found += 1
            logger.warning(f"Municipio PDET con código {cod_mpio} no encontrado en la base de datos")
    
    # Actualizar ZOMAC para todos los municipios desde constantes
    logger.info("Actualizando datos ZOMAC desde constantes...")
    all_municipios = db.query(Municipio).all()
    for municipio in all_municipios:
        zomac_pdet = get_zomac_pdet(municipio.dpto, municipio.nom_mpio)
        if zomac_pdet["zomac"] != municipio.zomac:
            municipio.zomac = zomac_pdet["zomac"]
            zomac_updated += 1
    
    db.commit()
    logger.info(f"✓ Municipios PDET actualizados: {updated} marcados como PDET, {not_found} no encontrados")
    logger.info(f"✓ Municipios ZOMAC actualizados: {zomac_updated} actualizados desde constantes")
    return updated, not_found


def save_municipios(data: list, db: Session):
    """Guarda los municipios en la base de datos"""
    repository = MunicipioRepository(db)
    saved = 0
    updated = 0
    
    logger.info("Procesando registros...")
    for item in data:
        dpto = item.get("dpto", "")
        nom_mpio = item.get("nom_mpio", "")
        
        # Obtener datos ZOMAC/PDET desde constantes
        zomac_pdet = get_zomac_pdet(dpto, nom_mpio)
        
        municipio_data = {
            "cod_dpto": item.get("cod_dpto", ""),
            "dpto": dpto,
            "cod_mpio": item.get("cod_mpio", ""),
            "nom_mpio": nom_mpio,
            "tipo_municipio": item.get("tipo_municipio", ""),
            "longitud": item.get("longitud", ""),
            "latitud": item.get("latitud", ""),
            "pdet": zomac_pdet["pdet"],
            "zomac": zomac_pdet["zomac"]
        }
        
        # Verificar si el municipio ya existe
        existing = repository.get_by_cod_mpio(municipio_data["cod_mpio"])
        
        if existing:
            # Actualizar datos existentes (incluyendo zomac y pdet)
            repository.update(existing, municipio_data, update_zomac_pdet=True)
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
            
            # Obtener y actualizar datos PDET
            logger.info("Obteniendo datos de municipios PDET...")
            pdet_data = await fetch_pdet_data()
            if pdet_data:
                pdet_updated, pdet_not_found = update_pdet_municipios(pdet_data, db)
                logger.info(f"✓ Municipios PDET actualizados: {pdet_updated}")
                if pdet_not_found > 0:
                    logger.warning(f"⚠️  {pdet_not_found} municipios PDET no encontrados en la base de datos")
            else:
                logger.warning("⚠️  No se obtuvieron datos PDET (puede ser por falta de token)")
            
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

