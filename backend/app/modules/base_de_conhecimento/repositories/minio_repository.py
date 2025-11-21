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


    def insert(self, bytes: bytes, obj_name: str):
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
            part_size=1024*1024*5
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
        



    # def download(self, obj_name: str):

    #     response = self.client.get_object(self.BUCKET_NAME, obj_name)
    #     return [response, obj_name]
        # try:
        #     response = self.client.get_object(self.BUCKET_NAME, id)
        #     #print(response.read())
        #     return [response, id]
        # finally:
        #     response.close()
        #     response.release_conn()


    # @staticmethod
    # def chunks_iter(documents, batch_size):
    #     for i in range(0, len(documents), batch_size):
    #         yield {
    #             "page_content": [doc.page_content for doc in documents[i:i+batch_size]],
    #             "metadata": [doc.metadata for doc in documents[i:i+batch_size]],
    #         }
