from fastapi import APIRouter
from app.api.v1.endpoints import municipios

api_router = APIRouter()

api_router.include_router(municipios.router, prefix="/municipios", tags=["municipios"])
api_router.include_router(municipios.router_departamentos, prefix="/departamentos", tags=["departamentos"])
api_router.include_router(municipios.router_stats, prefix="/stats", tags=["estadisticas"])

