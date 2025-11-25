from qdrant_client import QdrantClient
from minio import Minio
from app.infra.config import Config

# Singleton de Qdrant
_qdrant_client: QdrantClient | None = None

def get_qdrant_client() -> QdrantClient:
    """Retorna instância única do cliente Qdrant"""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY
        )

        # Para qdrant rodando local
        # _qdrant_client = QdrantClient(
        #     url=Config.QDRANT_URL
        # )
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
