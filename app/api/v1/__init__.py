from fastapi import APIRouter, Depends
from app.api.v1.endpoints import municipios
from app.core.security import verify_rapidapi_proxy_secret

api_router = APIRouter(
    dependencies=[Depends(verify_rapidapi_proxy_secret)]
)

api_router.include_router(municipios.router, prefix="/municipios", tags=["municipios"])
api_router.include_router(municipios.router_departamentos, prefix="/departamentos", tags=["departamentos"])
api_router.include_router(municipios.router_stats, prefix="/stats", tags=["estadisticas"])

