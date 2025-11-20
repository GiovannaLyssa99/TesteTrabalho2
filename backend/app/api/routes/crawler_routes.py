from fastapi.responses import JSONResponse
from app.modules.crawler_editais.schemas import CrawlerListRequest, ChamadaPublicaResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_db
from app.infra.dependency_provider import get_crawler_service
from app.modules.auth.auth import get_current_user
from app.modules.usuarios.models import User

crawler_router = APIRouter(prefix="/crawler", tags=["Crawler"])

@crawler_router.post("/chamada-publica/listar", response_model=list[ChamadaPublicaResponse])
def listar_chamadas_publicas(list_request: CrawlerListRequest, service = Depends(get_crawler_service)):
    try:
        result = service.listar_chamadas_publicas(list_request)
        if not result:
            return JSONResponse(content=[])
        return JSONResponse(content=[r for r in result])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))