from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.repositories.municipio_repository import MunicipioRepository
from app.core.redis_client import get_cache, set_cache
from app.schemas.municipio import MunicipioResponse, DepartamentoResponse
import hashlib
import math


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
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Obtiene municipios con filtros, paginación y cache"""
        # Validar página
        if page < 1:
            page = 1
        
        # Calcular skip
        skip = (page - 1) * limit
        
        # Crear clave de cache basada en los filtros
        filter_params = {
            "dpto": dpto,
            "cod_dpto": cod_dpto,
            "nom_mpio": nom_mpio,
            "page": page,
            "limit": limit
        }
        cache_key = f"municipios:{hashlib.md5(str(filter_params).encode()).hexdigest()}"
        
        cached = get_cache(cache_key)
        if cached:
            return cached
        
        # Obtener total de registros con los mismos filtros
        total = self.repository.count(
            dpto=dpto,
            cod_dpto=cod_dpto,
            nom_mpio=nom_mpio
        )
        
        # Obtener municipios
        municipios = self.repository.get_all(
            dpto=dpto,
            cod_dpto=cod_dpto,
            nom_mpio=nom_mpio,
            skip=skip,
            limit=limit
        )
        
        # Calcular información de paginación
        total_pages = math.ceil(total / limit) if total > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1
        
        items = [self._municipio_to_dict(m) for m in municipios]
        
        result = {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
        
        set_cache(cache_key, result)
        return result
    
    def get_departamentos(self) -> Dict[str, Any]:
        """Obtiene todos los departamentos con cache y total"""
        cache_key = "departamentos:all"
        cached = get_cache(cache_key)
        
        # Si el cache existe y tiene el formato nuevo, retornarlo
        if cached and isinstance(cached, dict) and "items" in cached and "total" in cached:
            return cached
        
        # Si el cache tiene formato antiguo o no existe, obtener datos frescos
        departamentos = self.repository.get_departamentos()
        items = [{"cod_dpto": d.cod_dpto, "dpto": d.dpto} for d in departamentos]
        total = len(items)
        
        result = {
            "items": items,
            "total": total
        }
        set_cache(cache_key, result, expire=7200)
        return result
    
    def count_municipios(
        self,
        dpto: Optional[str] = None,
        cod_dpto: Optional[str] = None,
        nom_mpio: Optional[str] = None
    ) -> int:
        """Cuenta municipios con filtros"""
        return self.repository.count(dpto=dpto, cod_dpto=cod_dpto, nom_mpio=nom_mpio)
    
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

