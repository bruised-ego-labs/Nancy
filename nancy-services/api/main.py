from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging
import os

from api.endpoints import ingest, query, directory
from core.legacy_adapter import initialize_nancy, shutdown_nancy, get_nancy_adapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global Nancy adapter
nancy_adapter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage Nancy lifecycle during FastAPI startup/shutdown."""
    global nancy_adapter
    
    logger.info("Starting Nancy Core API...")
    
    try:
        # Initialize Nancy system
        if await initialize_nancy():
            nancy_adapter = get_nancy_adapter()
            logger.info("Nancy Core initialized successfully")
        else:
            logger.error("Failed to initialize Nancy Core")
            raise HTTPException(status_code=500, detail="Nancy initialization failed")
            
        yield
        
    finally:
        logger.info("Shutting down Nancy Core...")
        await shutdown_nancy()
        logger.info("Nancy Core shutdown complete")


app = FastAPI(
    title="Project Nancy - Core API", 
    description="Nancy Core MCP Architecture API",
    version="2.0.0",
    lifespan=lifespan
)

# Include routers from the endpoints
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(query.router, prefix="/api", tags=["Querying"])
app.include_router(directory.router, prefix="/api", tags=["Directory Ingestion"])


@app.get("/")
def read_root():
    """Root endpoint with Nancy Core information."""
    migration_mode = os.getenv("NANCY_MIGRATION_MODE", "mcp")
    return {
        "message": "Welcome to Nancy Core MCP Architecture API",
        "version": "2.0.0",
        "migration_mode": migration_mode,
        "architecture": "Four-Brain MCP Orchestration Platform"
    }


@app.get("/health")
async def health_check():
    """Enhanced health check including Nancy Core systems."""
    try:
        if nancy_adapter:
            nancy_health = await nancy_adapter.async_health_check()
            return {
                "status": "healthy",
                "api": "ok",
                "nancy_core": nancy_health
            }
        else:
            return {
                "status": "degraded",
                "api": "ok",
                "nancy_core": {"status": "not_initialized"}
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "api": "ok",
            "nancy_core": {"status": "error", "error": str(e)}
        }


@app.get("/api/nancy/status")
async def nancy_status():
    """Get detailed Nancy Core status and metrics."""
    try:
        if not nancy_adapter:
            raise HTTPException(status_code=503, detail="Nancy Core not initialized")
        
        # Get status and metrics asynchronously
        status_info = await nancy_adapter.async_health_check()
        metrics = nancy_adapter.get_metrics()
        
        return {
            "status": status_info,
            "metrics": metrics,
            "migration_mode": nancy_adapter.migration_mode
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {e}")


@app.get("/api/nancy/configuration")
async def nancy_configuration():
    """Get Nancy Core configuration information (non-sensitive)."""
    try:
        if not nancy_adapter:
            raise HTTPException(status_code=503, detail="Nancy Core not initialized")
        
        # Return basic configuration info without sensitive data
        config = nancy_adapter.config
        
        return {
            "nancy_core": {
                "version": config.nancy_core.version,
                "instance_name": config.nancy_core.instance_name,
                "description": config.nancy_core.description
            },
            "orchestration": {
                "mode": config.orchestration.mode.value,
                "routing_strategy": config.orchestration.routing_strategy.value
            },
            "brains": {
                "vector": {"backend": config.brains.vector.backend.value},
                "analytical": {"backend": config.brains.analytical.backend.value},
                "graph": {"backend": config.brains.graph.backend.value},
                "linguistic": {"primary_llm": config.brains.linguistic.primary_llm}
            },
            "mcp_servers": {
                "enabled_count": len(config.mcp_servers.enabled_servers),
                "server_names": [server.name for server in config.mcp_servers.enabled_servers]
            }
        }
        
    except Exception as e:
        logger.error(f"Configuration retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration retrieval failed: {e}")
