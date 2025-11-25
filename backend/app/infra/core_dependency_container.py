from app.modules.base_de_conhecimento.services.pre_processamento_service import PreProcessamentoService
from app.modules.base_de_conhecimento.services.qdrant_service import QdrantService
from app.modules.base_de_conhecimento.services.minio_service import MinioService
from app.modules.base_de_conhecimento.services.admin_service import AdminService
from app.modules.crawler_editais.service import CrawlerService
from app.modules.base_de_conhecimento.repositories.qdrant_repository import QdrantRepository
from app.modules.base_de_conhecimento.repositories.minio_repository import MinioRepository

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class CoreContainer:
    def __init__(self):
        qdrant_repo = QdrantRepository()
        minio_repo = MinioRepository()

        self.preprocess_service = PreProcessamentoService()
        self.bd_vetorial_service = QdrantService(repository=qdrant_repo, preprocess_service=self.preprocess_service)
        self.minio_service = MinioService(repository=minio_repo)
        self.admin_service = AdminService(
            minio_service=self.minio_service,
            bd_vetorial_service=self.bd_vetorial_service
        )
        self.crawler_service = CrawlerService()

container = CoreContainer()