from pydantic import BaseModel
from typing import Optional


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

