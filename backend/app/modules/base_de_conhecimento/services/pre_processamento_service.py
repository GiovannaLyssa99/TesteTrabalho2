import re
import io
import pymupdf4llm
import pymupdf
from langchain_core.documents import Document
from langchain_text_splitters.markdown import MarkdownTextSplitter

class PreProcessamentoService:

    def __init__(self, chunk_size = 700):
        self.chunk_size = chunk_size
        

    def preprocess(self, file_bytes: bytes, metadata: dict):
        """
        Pré-processa o conteúdo de um documento e o divide em chunks.

        Args:
            file_bytes (bytes): arquivo em bytes.
            metadata (dict): metadados

        Returns:
            chunks (List[Document]): Lista de objetos `Document`, cada um contendo um trecho do texto
            original em `page_content` e metadados associados em `metadata`.
        """
        try:

            stream = io.BytesIO(file_bytes)
            doc = pymupdf.open(stream=stream, filetype="pdf")

            md_text = pymupdf4llm.to_markdown(doc)
            md_text = self.clean_markdown(md_text)

            doc_data = {"md_text": md_text, "metadata": metadata}

            chunks_text = self.chunking(doc_data["md_text"])
            chunks = self.generate_chunk_metadata(doc_data["metadata"], chunks_text)

            return chunks
        
        except Exception as e:
            print(f"Erro ao pré-processar conteúdo do arquivo: {e}")
            raise

    @staticmethod
    def clean_markdown(md_text: str):
        """
        Limpa Markdown de PDFs convertidos:
        - Remove linhas de sumário com muitos pontos
        - Normaliza quebras de linha
        - Preserva títulos (#, ##, **)
        - Remove espaços múltiplos
        """
        # Remove sequências de pontos (sumário)
        md_text = re.sub(r'\.{3,}', ' ', md_text)

        # Divide por linha
        lines = md_text.split('\n')
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()

            # Mantém linhas de título ou cabeçalhos
            if stripped.startswith('#') or stripped.startswith('**'):
                cleaned_lines.append(stripped)
                cleaned_lines.append('')  # garante uma linha vazia depois do título
                continue

            # Remove linhas inúteis (ex: só hifens, iguais, pontos)
            if re.fullmatch(r'[-= ]+', stripped):
                continue

            if stripped == '':
                # Mantém no máximo uma linha vazia seguida
                if cleaned_lines and cleaned_lines[-1] == '':
                    continue
                cleaned_lines.append('')
            else:
                # Concatena no parágrafo anterior se não for título
                if cleaned_lines and cleaned_lines[-1] not in ['', None]:
                    cleaned_lines[-1] += ' ' + stripped
                else:
                    cleaned_lines.append(stripped)

        # Junta e remove espaços duplicados
        text = '\n'.join(cleaned_lines)
        text = re.sub(r' +', ' ', text)  # normaliza múltiplos espaços

        return text.strip()

    def chunking(self, doc_md_text: str) -> list[Document]:
        """
        Divide um texto em chunks (partes menores) usando o MarkdownTextSplitter.

        Args:
            doc_md_text (str): Texto em formato Markdown a ser dividido.

        Raises:
            Exception: Se ocorrer algum erro inesperado durante a criação do bucket.

        Returns:
            chunks (List[Document]): Lista de objetos `Document`, cada um contendo um trecho do texto
            original em `page_content` e metadados associados em `metadata`.
        """
        try:

            splitter = MarkdownTextSplitter(chunk_size=self.chunk_size, chunk_overlap=100)
            chunks = splitter.create_documents([doc_md_text])

            return chunks
        
        except Exception as e:
            print(f"Erro ao dividir em chunks: {e}")
            raise

    @staticmethod
    def generate_chunk_metadata(doc_metadata: dict, chunks: list[Document]) -> list[Document]:
        """
        Adiciona metadata a cada chunk.
        
        Args:
            doc_metadata (dict): metadados do documento de origem dos chunks.
            chunks (list[Document]): chunks do documento.
        
        Return:
            chunks: chunks com seus conteúdos e metadados.
        """ 
        for idx, text in enumerate(chunks):
            chunk_id = f"{doc_metadata['doc_id']}_{idx}"

            chunk_metadata = {
                **doc_metadata,  # herda todos os metadados do documento
                "chunk_id": chunk_id,
                "chunk_index": idx
            }

            chunks[idx].metadata = chunk_metadata

        return chunks