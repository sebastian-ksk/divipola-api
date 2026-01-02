from fastapi import Header, HTTPException, status
from typing import Optional
from app.core.config import get_settings


async def verify_rapidapi_proxy_secret(
    x_rapidapi_proxy_secret: Optional[str] = Header(None, alias="X-RapidAPI-Proxy-Secret")
):
    """
    Verifica que el header X-RapidAPI-Proxy-Secret coincida con el valor configurado.
    Esta dependencia protege los endpoints para que solo puedan ser consumidos desde RapidAPI.
    """
    settings = get_settings()
    
    if not settings.rapidapi_proxy_secret:
        # Si no está configurado el secret, no se valida (modo desarrollo)
        return True
    
    if not x_rapidapi_proxy_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-RapidAPI-Proxy-Secret header"
        )
    
    if x_rapidapi_proxy_secret != settings.rapidapi_proxy_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid X-RapidAPI-Proxy-Secret header"
        )
    
    return True

