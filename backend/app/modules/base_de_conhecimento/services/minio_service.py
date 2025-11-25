
class MinioService:

    def __init__(self, repository):
        self.repository = repository

    def inserir(self, bytes: bytes, metadata: dict):
        """
        Insere um arquivo no minio.
        
        Args:
            bytes (bytes): arquivo em bytes.
            metadata: (dict): metadados.
        
        Raises:
            Exception: Se ocorrer algum erro inesperado.
        """ 
        try:
            dict = {
                "uploaded_by": metadata.get("uploaded_by"),
                "tags": metadata.get("tags")
            }
            # o nome do objeto no minio vai ser formado pelo nome do arquivo + $ + doc_id
            obj_name = f"{metadata['file_name']}${metadata['doc_id']}"
            self.repository.insert(bytes, obj_name, dict)

        except Exception as e:
            print(f"Erro ao inserir arquivo no minio: {e}")
            raise

    def excluir(self, object_names: list[str]):
        """
        Exclui um ou mais arquivos no minio.
        
        Args:
            object_names (list[str]): lista com nomes dos arquivos a serem excluídos. Como aparecem no minio.
        
        Raises:
            Exception: Se ocorrer algum erro inesperado.
        """ 
        try:

            self.repository.delete(object_names)

        except Exception as e:
            print(f"Erro ao excluir arquivo no minio: {e}")
            raise

    def listar_arquivos(self):
        """
        Lista os arquivos do minio.
        
        Raises:
            Exception: Se ocorrer algum erro inesperado.
        """ 
        try:

            lista = self.repository.list_files()
            return lista
        
        except Exception as e:
            print(f"Erro ao baixar arquivo no minio: {e}")
            raise

    def download(self, obj_name: str):
        """
        Baixa um arquivo do minio.
        
        Args:
            obj_name (str): nome do arquivo/objeto a ser baixado.
        
        Raises:
            Exception: Se ocorrer algum erro inesperado.
        """ 
        try:

            response = self.repository.download(obj_name)
            return {
                "stream": response[0],
                "content_type": "application/pdf",
                "filename": f"{response[1].split('$')[0]}.pdf"
            }
        
        except Exception as e:
            print(f"Erro ao baixar arquivo no minio: {e}")
            raise