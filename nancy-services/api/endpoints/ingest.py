from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import logging

from core.legacy_adapter import get_nancy_adapter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest")
async def ingest_data(
    file: UploadFile = File(...),
    author: Optional[str] = Form("Unknown")
):
    """
    Handles file ingestion through Nancy Core MCP architecture.
    Maintains backwards compatibility with legacy API.
    """
    try:
        # Get Nancy adapter
        nancy_adapter = get_nancy_adapter()
        if not nancy_adapter:
            raise HTTPException(status_code=503, detail="Nancy Core not available")
        
        # Read file content
        content = await file.read()
        
        # Use legacy adapter for backwards compatibility
        result = nancy_adapter.ingest_file(file.filename, content, author)
        
        logger.info(f"Successfully ingested file: {file.filename}")
        return result
        
    except Exception as e:
        logger.error(f"Ingestion failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")


@router.post("/ingest/knowledge-packet")
async def ingest_knowledge_packet(packet_data: dict):
    """
    Direct Knowledge Packet ingestion endpoint for MCP servers.
    This is a new endpoint specifically for the MCP architecture.
    """
    try:
        # Debug logging - log what we received
        logger.info(f"Received knowledge packet with keys: {list(packet_data.keys()) if packet_data else 'None'}")
        if packet_data:
            logger.info(f"packet_version field: {packet_data.get('packet_version', 'MISSING!')}")
            if len(str(packet_data)) < 1000:  # Only log small packets fully
                logger.info(f"Full packet data: {packet_data}")
            else:
                logger.info(f"Large packet received, size: {len(str(packet_data))} chars")
        # Get Nancy adapter
        nancy_adapter = get_nancy_adapter()
        if not nancy_adapter:
            raise HTTPException(status_code=503, detail="Nancy Core not available")
        
        # Validate we're in MCP mode
        if not hasattr(nancy_adapter, 'mcp_host') or not nancy_adapter.mcp_host:
            current_mode = nancy_adapter.migration_mode
            raise HTTPException(
                status_code=501, 
                detail=f"Knowledge Packet ingestion requires MCP mode. Current mode: {current_mode}. Set NANCY_MIGRATION_MODE=mcp or use /api/ingest endpoint for legacy compatibility."
            )
        
        # Import Knowledge Packet validation
        from schemas.knowledge_packet import NancyKnowledgePacket, KnowledgePacketValidator
        
        # Validate packet
        validator = KnowledgePacketValidator()
        validator.validate(packet_data)
        
        # Create Knowledge Packet object
        packet = NancyKnowledgePacket(packet_data)
        
        # Queue for processing
        await nancy_adapter.mcp_host.packet_queue.put(packet)
        
        return {
            "status": "success",
            "message": "Knowledge Packet queued for processing",
            "packet_id": packet.packet_id
        }
        
    except ValueError as e:
        logger.error(f"Invalid Knowledge Packet: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid Knowledge Packet: {e}")
    except Exception as e:
        logger.error(f"Knowledge Packet processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")


@router.get("/ingest/status")
async def ingestion_status():
    """
    Get ingestion system status and metrics.
    """
    try:
        nancy_adapter = get_nancy_adapter()
        if not nancy_adapter:
            raise HTTPException(status_code=503, detail="Nancy Core not available")
        
        # Get metrics from Nancy adapter
        metrics = nancy_adapter.get_metrics()
        
        # Add ingestion-specific information
        status = {
            "system_status": "operational",
            "migration_mode": nancy_adapter.migration_mode,
            "metrics": metrics
        }
        
        # Add MCP-specific metrics if available
        if hasattr(nancy_adapter, 'mcp_host') and nancy_adapter.mcp_host:
            mcp_metrics = nancy_adapter.mcp_host.get_metrics()
            status["mcp_metrics"] = mcp_metrics
        
        return status
        
    except Exception as e:
        logger.error(f"Status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {e}")
