from datetime import datetime, timezone
from app.utils import generate_hash

class AdminService:

    def __init__(self, minio_service, bd_vetorial_service):
        self.minio_service = minio_service
        self.bd_vetorial_service = bd_vetorial_service

    async def upload_document(
        self, 
        file_bytes: bytes, 
        file_name: str, 
        uploaded_by: str, 
        tags: str
    ):
        """
        Insere um ou mais arquivos do minio e qdrant
        """ 
        try:
            doc_id = generate_hash(file_name)

            metadata = {
                "doc_id": doc_id,
                "file_name": file_name,
                "uploaded_by": uploaded_by,
                "tags": tags.split(",") if tags else [],
                "insertion_date": datetime.now(timezone.utc).isoformat(),
            }


            self.minio_service.inserir(file_bytes, metadata=metadata)
            
  
            await self.bd_vetorial_service.inserir(file_bytes, metadata)

            return metadata
        
        except Exception as e:
            print(f"Erro ao inserir documentos: {e}")
            raise


    def delete_documents(self, file_names: list[str]):
        """
        Deleta um ou mais arquivos do minio e qdrant
        """ 
        try:
            doc_ids = [name.split('$')[1] for name in file_names]

            self.minio_service.excluir(file_names)

 
            self.bd_vetorial_service.excluir(doc_ids)   
        
        except Exception as e:
            print(f"Erro ao deletar documentos: {e}")
            raise

    def list_files(self):
        """
        Lista os arquivos do minio.
        """ 
        try:
            lista = self.minio_service.listar_arquivos()
            return lista
        except Exception as e:
            print(f"Erro ao baixar arquivo no minio: {e}")
            raise

    def download_documents(self, file_name: str):
            """
            Faz o download de um arquivo do minio
            """ 
            try:
                return self.minio_service.download(file_name)
            except Exception as e:
                print(f"Erro ao baixar documentos: {e}")
                raise