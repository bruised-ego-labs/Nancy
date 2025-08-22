from fastapi import APIRouter, HTTPException, Form
from typing import Optional, Dict, Any
from core.ingestion import DirectoryIngestionService

router = APIRouter()
directory_service = DirectoryIngestionService()

@router.post("/directory/scan")
async def scan_directory(
    directory_path: str = Form(...),
    recursive: bool = Form(True),
    file_patterns: Optional[str] = Form(None),
    ignore_patterns: Optional[str] = Form(None),
    author: str = Form("Directory Scan")
) -> Dict[str, Any]:
    """
    Scan a directory for files and detect changes using hash-based comparison.
    This performs Phase 1 directory scanning with change detection.
    
    Parameters:
    - directory_path: Absolute path to directory to scan
    - recursive: Whether to scan subdirectories (default: True)
    - file_patterns: Comma-separated patterns to include (e.g., "*.txt,*.md")
    - ignore_patterns: Comma-separated patterns to ignore (e.g., ".git/*,*.pyc")
    - author: Author attribution for discovered files
    
    Returns:
    - Scan results including file counts and change detection
    """
    try:
        result = directory_service.scan_directory(
            directory_path=directory_path,
            recursive=recursive,
            file_patterns=file_patterns,
            ignore_patterns=ignore_patterns,
            author=author
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Directory scan failed: {str(e)}")

@router.post("/directory/process")
async def process_pending_files(
    limit: int = Form(50),
    author: str = Form("Directory Processing")
) -> Dict[str, Any]:
    """
    Process files that are pending ingestion through Nancy's four-brain architecture.
    
    Parameters:
    - limit: Maximum number of files to process in this batch
    - author: Author attribution for processed files
    
    Returns:
    - Processing results including success/failure counts and detailed results
    """
    try:
        result = directory_service.process_pending_files(limit=limit, author=author)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@router.post("/directory/scan-and-process")
async def scan_and_process_directory(
    directory_path: str = Form(...),
    recursive: bool = Form(True),
    file_patterns: Optional[str] = Form(None),
    ignore_patterns: Optional[str] = Form(None),
    author: str = Form("Directory Ingestion"),
    process_limit: int = Form(50)
) -> Dict[str, Any]:
    """
    Complete directory ingestion: scan for changes and process pending files.
    This is the primary endpoint for directory-based ingestion.
    
    Parameters:
    - directory_path: Absolute path to directory to scan
    - recursive: Whether to scan subdirectories (default: True)
    - file_patterns: Comma-separated patterns to include
    - ignore_patterns: Comma-separated patterns to ignore
    - author: Author attribution for processed files
    - process_limit: Maximum number of files to process
    
    Returns:
    - Combined scan and processing results
    """
    try:
        result = directory_service.scan_and_process_directory(
            directory_path=directory_path,
            recursive=recursive,
            file_patterns=file_patterns,
            ignore_patterns=ignore_patterns,
            author=author,
            process_limit=process_limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Directory ingestion failed: {str(e)}")

@router.post("/directory/config")
async def add_directory_config(
    directory_path: str = Form(...),
    recursive: bool = Form(True),
    file_patterns: Optional[str] = Form(None),
    ignore_patterns: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Add a directory to the configuration for regular scanning.
    
    Parameters:
    - directory_path: Absolute path to directory to monitor
    - recursive: Whether to scan subdirectories
    - file_patterns: Comma-separated patterns to include
    - ignore_patterns: Comma-separated patterns to ignore
    
    Returns:
    - Configuration details including assigned config ID
    """
    try:
        result = directory_service.add_directory_config(
            directory_path=directory_path,
            recursive=recursive,
            file_patterns=file_patterns,
            ignore_patterns=ignore_patterns
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add directory config: {str(e)}")

@router.get("/directory/status")
async def get_directory_status() -> Dict[str, Any]:
    """
    Get comprehensive status of directory-based ingestion system.
    
    Returns:
    - Directory configurations, file statistics, and processing status
    """
    try:
        result = directory_service.get_directory_status()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get directory status: {str(e)}")

@router.get("/directory/health")
async def directory_health_check() -> Dict[str, Any]:
    """
    Health check for directory ingestion service.
    
    Returns:
    - Service status and basic statistics
    """
    try:
        # Perform basic health checks
        status = directory_service.get_directory_status()
        
        health_info = {
            "service": "directory_ingestion",
            "status": "healthy" if "error" not in status else "unhealthy",
            "timestamp": status.get("last_updated", "unknown"),
            "directories_configured": status.get("configured_directories", 0),
            "pending_files": status.get("pending_files", 0)
        }
        
        return health_info
        
    except Exception as e:
        return {
            "service": "directory_ingestion",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": None
        }