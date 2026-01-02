from pydantic import BaseModel
from typing import Optional, List, TypeVar, Generic

T = TypeVar('T')


class MunicipioBase(BaseModel):
    cod_dpto: str
    dpto: str
    cod_mpio: str
    nom_mpio: str
    tipo_municipio: str
    longitud: str
    latitud: str
    pdet: bool = False
    zomac: bool = False


class MunicipioCreate(MunicipioBase):
    pass


class MunicipioResponse(MunicipioBase):
    class Config:
        from_attributes = True


class MunicipioFilter(BaseModel):
    dpto: Optional[str] = None
    cod_dpto: Optional[str] = None
    nom_mpio: Optional[str] = None


class DepartamentoResponse(BaseModel):
    cod_dpto: str
    dpto: str
    
    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_municipios: int


class DepartamentosResponse(BaseModel):
    """Respuesta con lista de departamentos y total"""
    items: List[DepartamentoResponse]
    total: int


class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada genérica"""
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_previous: bool

