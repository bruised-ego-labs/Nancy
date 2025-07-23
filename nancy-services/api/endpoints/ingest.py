from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from core.ingestion import IngestionService

router = APIRouter()
ingestion_service = IngestionService()

@router.post("/ingest")
async def ingest_data(
    file: UploadFile = File(...),
    author: Optional[str] = Form("Unknown")
):
    """
    Handles file ingestion by passing the file and author to the IngestionService.
    """
    content = await file.read()
    result = ingestion_service.ingest_file(file.filename, content, author)
    return result
