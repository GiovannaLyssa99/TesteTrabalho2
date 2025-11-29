from qdrant_client import QdrantClient, AsyncQdrantClient
from minio import Minio
from app.infra.config import Config

_qdrant_client: AsyncQdrantClient | None = None

def get_qdrant_client() -> AsyncQdrantClient:
    """Retorna instância única do cliente Qdrant (Assíncrono)"""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = AsyncQdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY,
            timeout=30
        )
    return _qdrant_client

# Singleton do MinIO
_minio_client: Minio | None = None

def get_minio_client() -> Minio:
    """Retorna instância única do cliente Minio"""
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(endpoint=Config.MINIO_ENDPOINT, 
            access_key=Config.MINIO_ACCESS_KEY, 
            secret_key=Config.MINIO_SECRET_KEY,
            secure=False
        )
        
    return _minio_client