from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.municipio import (
    MunicipioResponse,
    DepartamentoResponse,
    StatsResponse
)
from app.services.municipio_service import MunicipioService

router = APIRouter()
router_departamentos = APIRouter()
router_stats = APIRouter()


def get_municipio_service(db: Session = Depends(get_db)) -> MunicipioService:
    """Dependency para obtener el servicio de municipios"""
    return MunicipioService(db)


@router.get("", response_model=List[MunicipioResponse])
def list_municipios(
    dpto: Optional[str] = Query(None, description="Filtrar por nombre de departamento (búsqueda parcial)"),
    cod_dpto: Optional[str] = Query(None, description="Filtrar por código de departamento"),
    nom_mpio: Optional[str] = Query(None, description="Filtrar por nombre de municipio (búsqueda parcial)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: MunicipioService = Depends(get_municipio_service)
):
    """
    Lista todos los municipios con filtros opcionales.
    
    - **dpto**: Búsqueda parcial por nombre de departamento
    - **cod_dpto**: Filtro exacto por código de departamento
    - **nom_mpio**: Búsqueda parcial por nombre de municipio
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar (máximo 1000)
    """
    municipios = service.get_municipios(
        dpto=dpto,
        cod_dpto=cod_dpto,
        nom_mpio=nom_mpio,
        skip=skip,
        limit=limit
    )
    return municipios


@router.get("/{cod_mpio}", response_model=MunicipioResponse)
def get_municipio(
    cod_mpio: str,
    service: MunicipioService = Depends(get_municipio_service)
):
    """
    Obtiene un municipio por su código DIVIPOLA.
    
    - **cod_mpio**: Código del municipio (ej: 05001 para Medellín)
    """
    municipio = service.get_municipio_by_cod(cod_mpio)
    if not municipio:
        raise HTTPException(
            status_code=404,
            detail=f"Municipio con código {cod_mpio} no encontrado"
        )
    return municipio


@router_departamentos.get("", response_model=List[DepartamentoResponse])
def list_departamentos(
    service: MunicipioService = Depends(get_municipio_service)
):
    """
    Lista todos los departamentos de Colombia.
    
    Retorna una lista única de departamentos con su código y nombre.
    """
    departamentos = service.get_departamentos()
    return departamentos


@router_stats.get("", response_model=StatsResponse)
def get_stats(
    dpto: Optional[str] = Query(None, description="Filtrar por nombre de departamento"),
    cod_dpto: Optional[str] = Query(None, description="Filtrar por código de departamento"),
    service: MunicipioService = Depends(get_municipio_service)
):
    """
    Obtiene estadísticas de municipios.
    
    - **dpto**: Filtrar por nombre de departamento
    - **cod_dpto**: Filtrar por código de departamento
    
    Retorna el total de municipios según los filtros aplicados.
    """
    total = service.count_municipios(dpto=dpto, cod_dpto=cod_dpto)
    return {"total_municipios": total}

