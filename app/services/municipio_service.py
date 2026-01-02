from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.repositories.municipio_repository import MunicipioRepository
from app.core.redis_client import get_cache, set_cache
from app.schemas.municipio import MunicipioResponse, DepartamentoResponse
import hashlib


class MunicipioService:
    """Servicio para lógica de negocio de Municipios"""
    
    def __init__(self, db: Session):
        self.repository = MunicipioRepository(db)
        self.db = db
    
    def get_municipio_by_cod(self, cod_mpio: str) -> Optional[Dict[str, Any]]:
        """Obtiene un municipio por código con cache"""
        cache_key = f"municipio:{cod_mpio}"
        cached = get_cache(cache_key)
        if cached:
            return cached
        
        municipio = self.repository.get_by_cod_mpio(cod_mpio)
        if not municipio:
            return None
        
        result = self._municipio_to_dict(municipio)
        set_cache(cache_key, result)
        return result
    
    def get_municipios(
        self,
        dpto: Optional[str] = None,
        cod_dpto: Optional[str] = None,
        nom_mpio: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtiene municipios con filtros y cache"""
        # Crear clave de cache basada en los filtros
        filter_params = {
            "dpto": dpto,
            "cod_dpto": cod_dpto,
            "nom_mpio": nom_mpio,
            "skip": skip,
            "limit": limit
        }
        cache_key = f"municipios:{hashlib.md5(str(filter_params).encode()).hexdigest()}"
        
        cached = get_cache(cache_key)
        if cached:
            return cached
        
        municipios = self.repository.get_all(
            dpto=dpto,
            cod_dpto=cod_dpto,
            nom_mpio=nom_mpio,
            skip=skip,
            limit=limit
        )
        
        result = [self._municipio_to_dict(m) for m in municipios]
        set_cache(cache_key, result)
        return result
    
    def get_departamentos(self) -> List[Dict[str, str]]:
        """Obtiene todos los departamentos con cache"""
        cache_key = "departamentos:all"
        cached = get_cache(cache_key)
        if cached:
            return cached
        
        departamentos = self.repository.get_departamentos()
        result = [{"cod_dpto": d.cod_dpto, "dpto": d.dpto} for d in departamentos]
        set_cache(cache_key, result, expire=7200)
        return result
    
    def count_municipios(
        self,
        dpto: Optional[str] = None,
        cod_dpto: Optional[str] = None
    ) -> int:
        """Cuenta municipios con filtros"""
        return self.repository.count(dpto=dpto, cod_dpto=cod_dpto)
    
    def _municipio_to_dict(self, municipio) -> Dict[str, Any]:
        """Convierte un modelo Municipio a diccionario"""
        return {
            "cod_dpto": municipio.cod_dpto,
            "dpto": municipio.dpto,
            "cod_mpio": municipio.cod_mpio,
            "nom_mpio": municipio.nom_mpio,
            "tipo_municipio": municipio.tipo_municipio,
            "longitud": municipio.longitud,
            "latitud": municipio.latitud,
            "pdet": municipio.pdet,
            "zomac": municipio.zomac
        }

