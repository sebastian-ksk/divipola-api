from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.municipio import Municipio


class MunicipioRepository:
    """Repositorio para operaciones de base de datos de Municipios"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_cod_mpio(self, cod_mpio: str) -> Optional[Municipio]:
        """Obtiene un municipio por su código"""
        return self.db.query(Municipio).filter(Municipio.cod_mpio == cod_mpio).first()
    
    def get_all(
        self,
        dpto: Optional[str] = None,
        cod_dpto: Optional[str] = None,
        nom_mpio: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Municipio]:
        """Obtiene todos los municipios con filtros opcionales"""
        query = self.db.query(Municipio)
        
        if dpto:
            query = query.filter(func.lower(Municipio.dpto).like(f"%{dpto.lower()}%"))
        if cod_dpto:
            query = query.filter(Municipio.cod_dpto == cod_dpto)
        if nom_mpio:
            query = query.filter(func.lower(Municipio.nom_mpio).like(f"%{nom_mpio.lower()}%"))
        
        return query.offset(skip).limit(limit).all()
    
    def get_departamentos(self) -> List[tuple]:
        """Obtiene todos los departamentos únicos"""
        return self.db.query(
            Municipio.cod_dpto,
            Municipio.dpto
        ).distinct().order_by(Municipio.dpto).all()
    
    def count(
        self,
        dpto: Optional[str] = None,
        cod_dpto: Optional[str] = None
    ) -> int:
        """Cuenta municipios con filtros opcionales"""
        query = self.db.query(Municipio)
        if dpto:
            query = query.filter(func.lower(Municipio.dpto).like(f"%{dpto.lower()}%"))
        if cod_dpto:
            query = query.filter(Municipio.cod_dpto == cod_dpto)
        return query.count()
    
    def create(self, municipio_data: dict) -> Municipio:
        """Crea un nuevo municipio"""
        municipio = Municipio(**municipio_data)
        self.db.add(municipio)
        self.db.commit()
        self.db.refresh(municipio)
        return municipio
    
    def update(self, municipio: Municipio, municipio_data: dict) -> Municipio:
        """Actualiza un municipio existente"""
        for key, value in municipio_data.items():
            if key not in ["pdet", "zomac"]:  # No sobrescribir pdet y zomac
                setattr(municipio, key, value)
        self.db.commit()
        self.db.refresh(municipio)
        return municipio

