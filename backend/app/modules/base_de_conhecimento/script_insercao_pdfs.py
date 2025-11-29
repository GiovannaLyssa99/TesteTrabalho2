from pathlib import Path
import os
import asyncio
from app.infra.dependency_provider import get_admin_service

BASE_DIR = Path(__file__).resolve().parent
PDF_FOLDER = BASE_DIR / "files"

UPLOADED_BY = "admin"
TAGS = "teste,batch"

admin_service = get_admin_service()

async def upload_all_pdfs():
    if not PDF_FOLDER.exists():
        print(f"Pasta {PDF_FOLDER} não encontrada. Criando...")
        os.makedirs(PDF_FOLDER, exist_ok=True)
        
    pdf_files = [f for f in PDF_FOLDER.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
    print(f"{len(pdf_files)} arquivos encontrados para upload.")

    for pdf_path in pdf_files:
        with open(pdf_path, "rb") as f:
            file_bytes = f.read()

        metadata = await admin_service.upload_document(
            file_bytes=file_bytes,
            file_name=pdf_path.name,
            uploaded_by=UPLOADED_BY,
            tags=TAGS
        )

        print(f"{pdf_path.name} enviado com sucesso. doc_id={metadata['doc_id']}\n--------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(upload_all_pdfs())