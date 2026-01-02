from sqlalchemy import Column, String, Boolean
from app.core.database import Base


class Municipio(Base):
    __tablename__ = "municipios"

    cod_mpio = Column(String, primary_key=True, index=True)
    cod_dpto = Column(String, index=True)
    dpto = Column(String, index=True)
    nom_mpio = Column(String, index=True)
    tipo_municipio = Column(String)
    longitud = Column(String)
    latitud = Column(String)
    pdet = Column(Boolean, default=False)
    zomac = Column(Boolean, default=False)

