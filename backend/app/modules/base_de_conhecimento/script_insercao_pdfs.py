from pathlib import Path
from app.infra.dependency_provider import get_admin_service

# Caminho para a pasta com PDFs
PDF_FOLDER = Path(r"")

# Configurações do upload
UPLOADED_BY = "admin"
TAGS = "teste,batch"

# Instância do service
admin_service = get_admin_service()

def upload_all_pdfs():
    pdf_files = [f for f in PDF_FOLDER.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
    print(f"{len(pdf_files)} arquivos encontrados para upload.")

    for pdf_path in pdf_files:
        with open(pdf_path, "rb") as f:
            file_bytes = f.read()

        metadata = admin_service.upload_document(
            file_bytes=file_bytes,
            file_name=pdf_path.name,
            uploaded_by=UPLOADED_BY,
            tags=TAGS
        )

        print(f"{pdf_path.name} enviado com sucesso. doc_id={metadata['doc_id']}\n--------------------------------------------------")

if __name__ == "__main__":
    upload_all_pdfs()
