import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.core.database import engine, Base
from app.api.v1 import api_router
from app.core.scheduler import start_scheduler, shutdown_scheduler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación...")
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    logger.info("Aplicación iniciada correctamente")
    yield
    # Shutdown
    logger.info("Deteniendo aplicación...")
    shutdown_scheduler()
    logger.info("Aplicación detenida")


app = FastAPI(
    title="DIVIPOLA API",
    description="""
    API REST para consultar información de municipios de Colombia según el código DIVIPOLA.
    
    ## Características
    
    * Consulta de municipios con filtros avanzados
    * Información de departamentos
    * Estadísticas de municipios
    * Cache con Redis para mejor rendimiento
    * Actualización automática de datos semanalmente
    
    ## Endpoints principales
    
    * **Municipios**: Consulta y búsqueda de municipios
    * **Departamentos**: Lista de departamentos de Colombia
    * **Estadísticas**: Estadísticas y conteos de municipios
    """,
    version="1.0.0",
    contact={
        "name": "DIVIPOLA API",
        "url": "https://www.datos.gov.co/widgets/gdxc-w37w",
    },
    license_info={
        "name": "Datos Abiertos Colombia",
        "url": "https://www.datos.gov.co",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
        "displayRequestDuration": True,
        "filter": True,
    }
)


def custom_openapi():
    """Personaliza el esquema OpenAPI"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=[
            {
                "name": "municipios",
                "description": "Operaciones relacionadas con municipios de Colombia. Permite buscar y consultar información detallada de municipios según código DIVIPOLA.",
            },
            {
                "name": "departamentos",
                "description": "Operaciones para obtener información de departamentos de Colombia.",
            },
            {
                "name": "estadisticas",
                "description": "Estadísticas y conteos de municipios con filtros opcionales.",
            },
        ],
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Incluir routers de la API
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["General"])
def root():
    """
    Endpoint raíz de la API.
    
    Retorna información básica sobre la API y enlaces a la documentación.
    """
    return {
        "message": "DIVIPOLA API - Códigos de Municipios de Colombia",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "endpoints": {
            "municipios": "/api/v1/municipios",
            "departamentos": "/api/v1/departamentos",
            "estadisticas": "/api/v1/stats"
        }
    }


@app.get("/health", tags=["General"])
def health_check():
    """
    Health check endpoint.
    
    Verifica el estado de la API. Útil para monitoreo y balanceadores de carga.
    """
    from app.core.scheduler import scheduler
    
    jobs_info = []
    if scheduler.running:
        for job in scheduler.get_jobs():
            jobs_info.append({
                "id": job.id,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            })
    
    return {
        "status": "healthy",
        "service": "DIVIPOLA API",
        "scheduler": {
            "running": scheduler.running,
            "jobs": jobs_info
        }
    }

