from app.infra.db_clients import get_qdrant_client
from qdrant_client import models
from qdrant_client.models import Filter, FieldCondition, MatchValue
from fastembed import TextEmbedding, SparseTextEmbedding
from langchain_core.documents import Document
import tqdm
import uuid

class QdrantRepository:

    DENSE_EMBEDDING_MODEL = TextEmbedding("intfloat/multilingual-e5-large")
    BM25_EMBEDDING_MODEL = SparseTextEmbedding("Qdrant/bm25")
    DENSE_VECTOR_NAME = "multilingual-e5-large"
    SPARSE_VECTOR_NAME = "bm25"
    COLLECTION_NAME = "inova_V6"

    def __init__(self):
        self.client = get_qdrant_client()

    async def create_collection(self, dense_embed_size: int):
        """
        Cria uma collection no Qdrant para os vetores do chatbotinova.
        
        Args:
            dense_embed_size (int): tamanho do vetor gerado pelo modelo de embedding.
        """   
        await self.client.create_collection(
            self.COLLECTION_NAME,
            vectors_config={
                self.DENSE_VECTOR_NAME: models.VectorParams(
                    size=dense_embed_size,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                self.SPARSE_VECTOR_NAME: models.SparseVectorParams(
                    modifier=models.Modifier.IDF,
                )
            }
        ) 

        await self.client.create_payload_index(
            collection_name=self.COLLECTION_NAME,
            field_name="doc_id",
            field_schema=models.KeywordIndexParams(type="keyword")
        )

        await self.client.create_payload_index(
            collection_name=self.COLLECTION_NAME,
            field_name="tags",
            field_schema=models.KeywordIndexParams(type="keyword")
        )   

        collection_info = await self.client.get_collection(self.COLLECTION_NAME)
        print(collection_info.payload_schema)

        

    async def insert(self, chunks: list[Document]):
        """
        Passa chunks pelo processo de embeddings e os insere na collection do Qdrant.
        
        Args:
            chunks (list[Document]): chunks de texto com seus metadados.
        """ 
        if not chunks:
            print("Nenhum chunk foi gerado. Verifique o conteúdo do arquivo.")
            return

        batch_size = 4

        dense_embeddings = list(self.DENSE_EMBEDDING_MODEL.passage_embed([chunks[0].page_content]))
        dense_embed_size = len(dense_embeddings[0])

        if not await self.client.collection_exists(self.COLLECTION_NAME):
            await self.create_collection(dense_embed_size)

        for batch in tqdm.tqdm(self.chunks_iter(chunks, batch_size), 
                            total=len(chunks) // batch_size):
            dense_embeddings = list(self.DENSE_EMBEDDING_MODEL.passage_embed(batch["page_content"]))
            bm25_embeddings = list(self.BM25_EMBEDDING_MODEL.passage_embed(batch["page_content"]))
            
            self.client.upload_points(
                self.COLLECTION_NAME,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector={
                            self.DENSE_VECTOR_NAME: dense_embeddings[i].tolist(),
                            self.SPARSE_VECTOR_NAME: bm25_embeddings[i].as_object()
                        },
                        payload={
                            "_id": batch["metadata"][i]["chunk_id"],
                            "page_content": batch["page_content"][i],
                            "doc_id": batch["metadata"][i]["doc_id"],
                            "file_name": batch["metadata"][i]["file_name"],
                            "tags": batch["metadata"][i]["tags"] or [],
                            "insertion_date": batch["metadata"][i]["insertion_date"],
                        }
                    )
                    for i, _ in enumerate(batch["page_content"])
                ],
                
                batch_size=batch_size,  
            )

    async def delete(self, doc_id: str):
        """
        Deleta todos os chunks de um documento na collection do Qdrant.
        
        Args:
            doc_id (str): id do documento a ser excluído.
        """ 
        filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=doc_id)
                    )
                ]
            )

        # Deletar points da coleção
        await self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=filter_condition
        )

    def hybrid_search(self, query: str):
        """
        Busca vetorial e semÂmntica de chunks relacionados à query.
        
        Args:
            query (str): pergunta ou frase a ser utilizada para a busca.
        """     
        dense_query_vector = next(self.DENSE_EMBEDDING_MODEL.query_embed(query))
        sparse_query_vector = next(self.BM25_EMBEDDING_MODEL.query_embed(query))

        prefetch = [
            models.Prefetch(
                query=dense_query_vector,
                using=self.DENSE_VECTOR_NAME,
                limit=20,
                score_threshold=0.70
            ),
            models.Prefetch(
                query=models.SparseVector(**sparse_query_vector.as_object()),
                using=self.SPARSE_VECTOR_NAME,
                limit=20,
            ),
        ]
        results = self.client.query_points(
            self.COLLECTION_NAME,
            prefetch=prefetch,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF,
            ),
            with_payload=True,
            limit=10,
        )
        return results
    

    @staticmethod
    def chunks_iter(documents, batch_size):
        for i in range(0, len(documents), batch_size):
            yield {
                "page_content": [doc.page_content for doc in documents[i:i+batch_size]],
                "metadata": [doc.metadata for doc in documents[i:i+batch_size]],
            }
