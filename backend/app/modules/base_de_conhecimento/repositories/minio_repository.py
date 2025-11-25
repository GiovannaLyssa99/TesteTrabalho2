from app.infra.db_clients import get_minio_client
from minio.deleteobjects import DeleteObject
import io

class MinioRepository:

    BUCKET_NAME = "chatbotinova"

    def __init__(self):
        self.client = get_minio_client()


    def create_bucket(self):
        """
        Cria um bucket (pasta) no MinIO para os arquivos do chatbot inova
        """
        self.client.make_bucket(bucket_name=self.BUCKET_NAME, location="us-west-1")


    def insert(self, bytes: bytes, obj_name: str, metadata: dict):
        """
        Insere um object (arquivo) no bucket MinIO.
        
        Args:
            bytes (bytes): bytes do arquivo a ser inserido.
            obj_name (str): Nome do object a ser criado. 
                No MinIO o nome do object funciona como id dentro do bucket.
        """
        if not self.client.bucket_exists(self.BUCKET_NAME):
            self.create_bucket()

        resultado = self.client.put_object(
            bucket_name=self.BUCKET_NAME,
            object_name=obj_name,
            data=io.BytesIO(bytes),
            length= -1,
            part_size=1024*1024*5, 
            metadata=metadata
        )

        print(resultado)



    def delete(self, object_names: list[str]):
        """
        Deleta um ou vários objects (arquivos) no bucket MinIO.
        
        Args:
            object_names (list[str]): Lista com os obj_names dos arquivos a serem excluídos. 
        """
        delete_list = list(map(lambda name: DeleteObject(name), object_names))

        errors = self.client.remove_objects(
            self.BUCKET_NAME,
            delete_list,
        )
        for error in errors:
            print("error occurred when deleting object - Minio", error)
        

    def list_files(self):
        """
        Lista os objects(arquivos) do bucket MinIO.
        
        """
        objects = self.client.list_objects(self.BUCKET_NAME)
        list = []
        for obj in objects:
            print(obj)
            list.append({"obj_name": obj.object_name, "metadata": obj.metadata})
        
        return list

    def download(self, obj_name: str):
        """
        Faz o download de um object(arquivo) do bucket MinIO.
        
        Args:
            object_name (str): object_name do arquivo a ser excluído. 
        """

        response = self.client.get_object(self.BUCKET_NAME, obj_name)
        return [response, obj_name]

    # @staticmethod
    # def chunks_iter(documents, batch_size):
    #     for i in range(0, len(documents), batch_size):
    #         yield {
    #             "page_content": [doc.page_content for doc in documents[i:i+batch_size]],
    #             "metadata": [doc.metadata for doc in documents[i:i+batch_size]],
    #         }
