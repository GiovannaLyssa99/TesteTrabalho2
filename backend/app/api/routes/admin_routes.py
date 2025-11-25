import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from app.modules.base_de_conhecimento.schemas import FileUploadResponse, FileDeleteResponse
from fastapi import Depends
from typing import Optional, List
from app.infra.dependency_provider import get_admin_service
from app.modules.auth.auth import require_admin

admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.post("/upload", response_model=FileUploadResponse, dependencies=[Depends(require_admin)])
async def upload(
    file: UploadFile = File(...),
    uploaded_by: str = Form(...),
    tags: str = Form(None),
    admin_service = Depends(get_admin_service),
):
    try:
        file_bytes = await file.read()
        #metadata = admin_service.upload_document(file_bytes, file.filename, uploaded_by, tags)
        metadata = await asyncio.to_thread(
            admin_service.upload_document,
            file_bytes, file.filename, uploaded_by, tags
        )
        return FileUploadResponse(success=True, message="Arquivo inserido com sucesso.", **metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.delete("/delete", response_model=FileDeleteResponse, dependencies=[Depends(require_admin)])
async def delete_documents(
    file_names: List[str],
    admin_service = Depends(get_admin_service)
):
    try:
        admin_service.delete_documents(file_names)
        return FileDeleteResponse(success=True, message="Documentos removidos com sucesso.", deleted_files=file_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@admin_router.get("/list", dependencies=[Depends(require_admin)])
async def list_files(
    admin_service = Depends(get_admin_service)
):
    
    try:
        list = admin_service.list_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return list



@admin_router.get("/download", dependencies=[Depends(require_admin)])
async def download_document(
    file_name: str,
    admin_service = Depends(get_admin_service)
):

    try:
        file_data = admin_service.download_documents(file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return StreamingResponse(
        file_data.get("stream"),
        media_type=file_data.get("content_type"),
        headers={
            "Content-Disposition": f'attachment; filename="{file_data.get("filename")}"'
        }
    )