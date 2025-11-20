from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class Pagination(BaseModel):
    page: int = 0
    size: int = 10

class ChamadaPublicaFilter(BaseModel):
    titulo: Optional[str] = None
    origem: Optional[str] = None
    data_publicacao: Optional[date] = None
    link: Optional[str] = None

class CrawlerListRequest(BaseModel):
    filters: Optional[ChamadaPublicaFilter] = None
    pagination: Optional[Pagination] = Pagination()

class ChamadaPublicaResponse(BaseModel):
    uuid: str
    titulo: str
    origem: str
    data_publicacao: date
    link: str