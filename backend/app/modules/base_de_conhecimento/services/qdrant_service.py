from typing import Literal

class QdrantService:

    def __init__(self, repository, preprocess_service):
        self.repository = repository
        self.preprocess_service = preprocess_service

    def inserir(self, bytes: bytes, metadata: dict):
        """
        Pré-processa o texto do arquivo e insere os chunks no qdrant.
        
        Args:
            bytes (bytes): arquivo em bytes.
            metadata (dict): metadados do arquivo.
        
        Raises:
            Exception: Se ocorrer algum erro inesperado.
        """ 
        try:

            chunks = self.preprocess_service.preprocess(bytes, metadata)
            self.repository.insert(chunks)

        except Exception as e:
            print(f"Erro ao inserir doc ao Qdrant: {e}")
            raise

    def excluir(self, doc_ids: list[str]):
        """
        Exclui os chunks de um ou varios arquivos no qdrant.
        
        Args:
            doc_ids (list[str]): lista com os ids dos documentos a serem excluídos.
        
        Raises:
            Exception: Se ocorrer algum erro inesperado.
        """ 
        try:

            for doc_id in doc_ids:
                self.repository.delete(doc_id)
        
        except Exception as e:
            print(f"Erro ao excluir docs no Qdrant: {e}")
            raise

    def buscar(self, query: str, search_type: Literal["hybrid", "naive"]):
        """
        Busca os chunks relacionados à query no qdrant.
        
        Args:
            query (str): frase ou pergunta.
            search_type: ("hybrid", "naive"): tipo de busca a ser feita.
        
        Raises:
            Exception: Se ocorrer algum erro inesperado.

        Return:
            resultado
        """ 
        try:

            resultado = self.repository.search(query, search_type)
            
            # for hit in resultado.points:
            #     texto = hit.payload["page_content"]       
            #     print(f"Texto: {texto}\n")
            
            return resultado
        
        except Exception as e:
            print(f"Erro ao buscar chunks no Qdrant: {e}")
            raise
