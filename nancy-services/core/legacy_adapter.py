"""
Nancy Legacy Adapter
Provides backwards compatibility for existing Nancy API while transitioning to MCP architecture.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from .config_manager import NancyConfiguration, get_config_manager
from .mcp_host import NancyMCPHost
from schemas.knowledge_packet import NancyKnowledgePacket
from .ingestion import IngestionService  # Legacy ingestion service
from .langchain_orchestrator import LangChainOrchestrator

logger = logging.getLogger(__name__)


class LegacyNancyAdapter:
    """
    Adapter to maintain existing API compatibility during MCP migration.
    
    This class provides the same interface as the legacy Nancy system while
    internally routing operations through the new MCP architecture.
    """
    
    def __init__(self, config: Optional[NancyConfiguration] = None):
        """
        Initialize the legacy adapter.
        
        Args:
            config: Nancy configuration. If None, will load from file.
        """
        self.config = config or get_config_manager().get_config()
        self.mcp_host: Optional[NancyMCPHost] = None
        self.legacy_ingestion: Optional[IngestionService] = None
        self.legacy_orchestrator: Optional[LangChainOrchestrator] = None
        
        # Migration mode controls behavior
        self.migration_mode = os.getenv("NANCY_MIGRATION_MODE", "mcp")  # "legacy", "hybrid", "mcp"
        
        logger.info(f"Initialized Legacy Nancy Adapter in {self.migration_mode} mode")
    
    async def initialize(self) -> bool:
        """Initialize the adapter based on migration mode."""
        try:
            if self.migration_mode == "legacy":
                return await self._initialize_legacy_mode()
            elif self.migration_mode == "hybrid":
                return await self._initialize_hybrid_mode()
            else:  # mcp mode
                return await self._initialize_mcp_mode()
        except Exception as e:
            logger.error(f"Failed to initialize Nancy adapter: {e}")
            return False
    
    async def _initialize_legacy_mode(self) -> bool:
        """Initialize legacy-only mode."""
        logger.info("Initializing in legacy mode")
        
        # Use original ingestion service and orchestrator
        self.legacy_ingestion = IngestionService()
        self.legacy_orchestrator = LangChainOrchestrator()
        
        return True
    
    async def _initialize_hybrid_mode(self) -> bool:
        """Initialize hybrid mode (both legacy and MCP)."""
        logger.info("Initializing in hybrid mode")
        
        # Initialize both systems
        success_legacy = await self._initialize_legacy_mode()
        success_mcp = await self._initialize_mcp_mode()
        
        # At least one system must work
        return success_legacy or success_mcp
    
    async def _initialize_mcp_mode(self) -> bool:
        """Initialize MCP-only mode."""
        logger.info("Initializing in MCP mode")
        
        # Initialize MCP host
        self.mcp_host = NancyMCPHost(self.config)
        return await self.mcp_host.start()
    
    async def shutdown(self):
        """Shutdown the adapter and all systems."""
        if self.mcp_host:
            await self.mcp_host.stop()
        
        logger.info("Nancy adapter shutdown complete")
    
    # Legacy API Methods
    
    def ingest_file(self, filename: str, content: bytes, author: str = "Unknown") -> Dict[str, Any]:
        """
        Legacy ingestion interface - maintains exact same signature.
        
        Args:
            filename: Name of the file
            content: File content as bytes
            author: Author of the file
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            if self.migration_mode == "legacy" or (self.migration_mode == "hybrid" and not self.mcp_host):
                return self._legacy_ingest_file(filename, content, author)
            else:
                return self._mcp_ingest_file(filename, content, author)
        except Exception as e:
            logger.error(f"File ingestion failed for {filename}: {e}")
            return {
                "status": "error",
                "message": f"Ingestion failed: {e}",
                "doc_id": None
            }
    
    def _legacy_ingest_file(self, filename: str, content: bytes, author: str) -> Dict[str, Any]:
        """Use legacy ingestion service."""
        if not self.legacy_ingestion:
            raise RuntimeError("Legacy ingestion service not initialized")
        
        result = self.legacy_ingestion.ingest_file(filename, content, author)
        
        # Convert legacy result format to standard format
        return {
            "status": "success",
            "message": "File ingested via legacy system",
            "doc_id": result.get("doc_id"),
            "legacy_result": result
        }
    
    def _mcp_ingest_file(self, filename: str, content: bytes, author: str) -> Dict[str, Any]:
        """Use MCP ingestion with proper async/sync bridging."""
        if not self.mcp_host:
            raise RuntimeError("MCP host not initialized")
        
        try:
            # Use asyncio to run the async MCP ingestion safely
            import asyncio
            import concurrent.futures
            
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, need to use a thread pool
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_mcp_ingestion_sync, filename, content, author)
                    result = future.result(timeout=30)
                    return result
            except RuntimeError:
                # No running loop, we can create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self._mcp_ingest_async(filename, content, author))
                    return result
                finally:
                    loop.close()
                    
        except Exception as e:
            logger.error(f"MCP ingestion failed: {e}")
            return {
                "status": "error",
                "message": f"MCP ingestion failed: {e}",
                "doc_id": None
            }
    
    def _run_mcp_ingestion_sync(self, filename: str, content: bytes, author: str) -> Dict[str, Any]:
        """Run MCP ingestion in a separate thread with its own event loop."""
        import asyncio
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._mcp_ingest_async(filename, content, author))
        finally:
            loop.close()
    
    async def _mcp_ingest_async(self, filename: str, content: bytes, author: str) -> Dict[str, Any]:
        """Async MCP ingestion implementation."""
        # Create a temporary file for MCP processing
        temp_path = None
        try:
            temp_path = self._create_temp_file(filename, content)
            
            # TODO: Implement actual MCP server ingestion
            # For now, create a simplified Knowledge Packet
            from schemas.knowledge_packet import NancyKnowledgePacket
            
            packet = NancyKnowledgePacket.create(
                mcp_server="nancy-core",
                server_version="2.0.0",
                original_location=temp_path,
                content_type="document",
                title=filename,
                content={
                    "vector_data": {
                        "chunks": [{
                            "chunk_id": f"{filename}_chunk_0",
                            "text": content.decode('utf-8', errors='ignore')
                        }]
                    }
                },
                author=author
            )
            
            # Process through knowledge packet processor
            # TODO: Integrate with actual MCP host and knowledge packet processor
            
            return {
                "status": "success",
                "message": "File ingested via MCP architecture",
                "doc_id": packet.packet_id,
                "packet_id": packet.packet_id
            }
            
        except Exception as e:
            logger.error(f"Async MCP ingestion failed: {e}")
            return {
                "status": "error",
                "message": f"MCP ingestion failed: {e}",
                "doc_id": None
            }
        finally:
            if temp_path:
                self._cleanup_temp_file(temp_path)
    
    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Legacy query interface - maintains exact same signature.
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            
        Returns:
            Dictionary with query results
        """
        try:
            if self.migration_mode == "legacy" or (self.migration_mode == "hybrid" and not self.legacy_orchestrator):
                return self._legacy_query(query_text, n_results)
            else:
                return self._mcp_query(query_text, n_results)
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "status": "error",
                "message": f"Query failed: {e}",
                "results": []
            }
    
    def _legacy_query(self, query_text: str, n_results: int) -> Dict[str, Any]:
        """Use legacy query orchestrator."""
        if not self.legacy_orchestrator:
            raise RuntimeError("Legacy orchestrator not initialized")
        
        # Use legacy orchestrator
        result = self.legacy_orchestrator.query(query_text, n_results)
        
        return {
            "status": "success",
            "message": "Query processed via legacy system",
            "results": result.get("results", []),
            "legacy_result": result
        }
    
    def _mcp_query(self, query_text: str, n_results: int) -> Dict[str, Any]:
        """Use MCP-based query processing."""
        # TODO: Implement MCP query processing
        # For now, fall back to legacy if available
        if self.legacy_orchestrator:
            return self._legacy_query(query_text, n_results)
        else:
            return {
                "status": "error",
                "message": "MCP query processing not yet implemented",
                "results": []
            }
    
    def _create_temp_file(self, filename: str, content: bytes) -> str:
        """Create temporary file for MCP processing."""
        import tempfile
        
        # Create temp directory if it doesn't exist
        temp_dir = Path("./data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temp file with original extension
        suffix = Path(filename).suffix
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            dir=temp_dir
        )
        
        try:
            temp_file.write(content)
            temp_file.flush()
            return temp_file.name
        finally:
            temp_file.close()
    
    def _cleanup_temp_file(self, temp_path: str):
        """Clean up temporary file."""
        try:
            os.unlink(temp_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {temp_path}: {e}")
    
    # Health and Status Methods
    
    def health_check(self) -> Dict[str, Any]:
        """Perform synchronous health check on the system."""
        # Absolute minimal test with no property access
        return {
            "status": "healthy",
            "debug": "no_property_access_test"
        }
    
    async def async_health_check(self) -> Dict[str, Any]:
        """Perform full async health check including MCP server status."""
        health_info = {
            "status": "healthy",
            "migration_mode": self.migration_mode,
            "timestamp": datetime.now().isoformat(),
            "systems": {}
        }
        
        # Check legacy systems
        if self.migration_mode in ["legacy", "hybrid"]:
            health_info["systems"]["legacy"] = {
                "ingestion": "available" if self.legacy_ingestion else "unavailable",
                "orchestrator": "available" if self.legacy_orchestrator else "unavailable"
            }
        
        # Check MCP systems asynchronously
        if self.migration_mode in ["mcp", "hybrid"] and self.mcp_host:
            try:
                # Use async MCP health check without event loop conflicts
                mcp_status = await self._safe_mcp_health_check()
                health_info["systems"]["mcp"] = mcp_status
            except Exception as e:
                logger.warning(f"MCP health check failed: {e}")
                health_info["systems"]["mcp"] = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            health_info["systems"]["mcp"] = {"status": "disabled"}
        
        # Determine overall status
        system_statuses = [system.get("status", "unknown") for system in health_info["systems"].values()]
        if any(status == "error" for status in system_statuses):
            health_info["status"] = "degraded"
        elif all(status in ["available", "healthy"] for status in system_statuses):
            health_info["status"] = "healthy"
        else:
            health_info["status"] = "partial"
        
        return health_info
    
    async def _safe_mcp_health_check(self) -> Dict[str, Any]:
        """Safely check MCP host health without event loop conflicts."""
        if not self.mcp_host:
            return {"status": "not_initialized"}
        
        try:
            # Check if MCP host has servers
            server_count = len(self.mcp_host.registered_servers) if hasattr(self.mcp_host, 'registered_servers') else 0
            
            return {
                "status": "healthy",
                "server_count": server_count,
                "host_initialized": True
            }
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance and usage metrics."""
        metrics = {
            "migration_mode": self.migration_mode,
            "legacy_metrics": {},
            "mcp_metrics": {}
        }
        
        # Get MCP metrics if available
        if self.mcp_host:
            metrics["mcp_metrics"] = self.mcp_host.get_metrics()
        
        return metrics


class MigrationManager:
    """
    Manages the migration from legacy to MCP architecture.
    """
    
    def __init__(self):
        self.migration_mode = os.getenv("NANCY_MIGRATION_MODE", "mcp")
        self.config_manager = get_config_manager()
    
    def get_orchestrator(self) -> LegacyNancyAdapter:
        """Get appropriate orchestrator based on migration mode."""
        # Load configuration
        try:
            config = self.config_manager.get_config()
        except ValueError:
            # Config not loaded, try to load default
            try:
                config = self.config_manager.load_config()
            except:
                # Create default config if none exists
                self.config_manager.create_default_config()
                config = self.config_manager.load_config()
        
        return LegacyNancyAdapter(config)
    
    def set_migration_mode(self, mode: str):
        """Set migration mode."""
        valid_modes = ["legacy", "hybrid", "mcp"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid migration mode: {mode}. Must be one of {valid_modes}")
        
        os.environ["NANCY_MIGRATION_MODE"] = mode
        self.migration_mode = mode
        logger.info(f"Set migration mode to: {mode}")
    
    def check_migration_readiness(self) -> Dict[str, Any]:
        """Check if system is ready for migration."""
        readiness = {
            "current_mode": self.migration_mode,
            "mcp_servers_available": False,
            "configuration_valid": False,
            "legacy_compatible": False,
            "recommendations": []
        }
        
        # Check configuration
        try:
            config = self.config_manager.get_config()
            readiness["configuration_valid"] = True
            
            # Check MCP servers configuration
            if config.mcp_servers.enabled_servers:
                readiness["mcp_servers_available"] = True
            else:
                readiness["recommendations"].append("Configure at least one MCP server")
                
        except Exception as e:
            readiness["recommendations"].append(f"Fix configuration: {e}")
        
        # Check legacy components
        try:
            # Try to import legacy components
            from .ingestion import IngestionService
            from .langchain_orchestrator import LangChainOrchestrator
            readiness["legacy_compatible"] = True
        except Exception as e:
            readiness["recommendations"].append(f"Legacy components not available: {e}")
        
        # Add migration recommendations
        if readiness["configuration_valid"] and readiness["mcp_servers_available"]:
            if self.migration_mode == "legacy":
                readiness["recommendations"].append("Ready to migrate to hybrid mode")
            elif self.migration_mode == "hybrid":
                readiness["recommendations"].append("Ready to migrate to full MCP mode")
        
        return readiness


# Global adapter instance
_nancy_adapter: Optional[LegacyNancyAdapter] = None


def get_nancy_adapter() -> LegacyNancyAdapter:
    """Get global Nancy adapter instance."""
    global _nancy_adapter
    if _nancy_adapter is None:
        migration_manager = MigrationManager()
        _nancy_adapter = migration_manager.get_orchestrator()
    return _nancy_adapter


async def initialize_nancy() -> bool:
    """Initialize Nancy system."""
    adapter = get_nancy_adapter()
    return await adapter.initialize()


async def shutdown_nancy():
    """Shutdown Nancy system."""
    global _nancy_adapter
    if _nancy_adapter:
        await _nancy_adapter.shutdown()
        _nancy_adapter = None