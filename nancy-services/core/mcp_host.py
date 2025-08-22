"""
Nancy Core MCP Host Implementation
Manages MCP client connections and Knowledge Packet processing.
"""

import asyncio
import logging
import json
import subprocess
import os
import signal
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path

from .config_manager import NancyConfiguration, MCPServerConfig
from schemas.knowledge_packet import NancyKnowledgePacket, KnowledgePacketValidator
from .search import AnalyticalBrain
from .knowledge_graph import GraphBrain
from .nlp import VectorBrain

logger = logging.getLogger(__name__)


class MCPServerProcess:
    """Manages a single MCP server process."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.last_health_check = None
        self.is_healthy = False
        
    async def start(self) -> bool:
        """Start the MCP server process."""
        if self.process and self.process.poll() is None:
            logger.warning(f"MCP server {self.config.name} is already running")
            return True
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(self.config.environment)
            
            # Build command
            cmd = [self.config.executable] + self.config.args
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True
            )
            
            # Give process time to start
            await asyncio.sleep(1)
            
            # Check if process started successfully
            if self.process.poll() is None:
                logger.info(f"Started MCP server {self.config.name} (PID: {self.process.pid})")
                self.is_healthy = True
                return True
            else:
                stdout, stderr = self.process.communicate()
                logger.error(f"MCP server {self.config.name} failed to start: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start MCP server {self.config.name}: {e}")
            return False
    
    async def stop(self):
        """Stop the MCP server process."""
        if not self.process:
            return
        
        try:
            # Try graceful shutdown first
            self.process.terminate()
            
            # Wait for graceful shutdown
            try:
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process()),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                # Force kill if graceful shutdown fails
                logger.warning(f"Force killing MCP server {self.config.name}")
                self.process.kill()
                await self._wait_for_process()
            
            logger.info(f"Stopped MCP server {self.config.name}")
            
        except Exception as e:
            logger.error(f"Error stopping MCP server {self.config.name}: {e}")
        finally:
            self.process = None
            self.is_healthy = False
    
    async def _wait_for_process(self):
        """Wait for process to terminate."""
        while self.process and self.process.poll() is None:
            await asyncio.sleep(0.1)
    
    async def health_check(self) -> bool:
        """Perform health check on the MCP server."""
        if not self.process:
            self.is_healthy = False
            return False
        
        # Check if process is still running
        if self.process.poll() is not None:
            self.is_healthy = False
            logger.warning(f"MCP server {self.config.name} process has died")
            return False
        
        # TODO: Implement actual MCP protocol health check
        # For now, just check if process is alive
        self.is_healthy = True
        self.last_health_check = datetime.utcnow()
        return True
    
    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send MCP request to server."""
        if not self.is_healthy:
            raise RuntimeError(f"MCP server {self.config.name} is not healthy")
        
        # TODO: Implement actual MCP protocol communication
        # For now, return mock response
        return {
            "result": {"status": "success", "method": method, "params": params},
            "id": "mock_request"
        }


class MCPClient:
    """Client for communicating with MCP servers."""
    
    def __init__(self, server_process: MCPServerProcess):
        self.server_process = server_process
        self.request_id = 0
    
    async def initialize(self) -> bool:
        """Initialize MCP client connection."""
        # TODO: Implement MCP protocol initialization
        return await self.server_process.health_check()
    
    async def ingest_file(self, file_path: str, metadata: Dict[str, Any]) -> NancyKnowledgePacket:
        """
        Request MCP server to ingest a file and return Knowledge Packet.
        
        Args:
            file_path: Path to file to ingest
            metadata: Additional metadata for ingestion
            
        Returns:
            NancyKnowledgePacket containing processed data
        """
        self.request_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "nancy/ingest",
            "params": {
                "file_path": file_path,
                "metadata": metadata
            }
        }
        
        # TODO: Send actual MCP request
        response = await self.server_process.send_request("nancy/ingest", request["params"])
        
        # For now, create a mock Knowledge Packet
        # This will be replaced with actual MCP server response processing
        packet_data = self._create_mock_knowledge_packet(file_path, metadata)
        return NancyKnowledgePacket(packet_data)
    
    def _create_mock_knowledge_packet(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create mock Knowledge Packet for development."""
        import hashlib
        
        # Generate mock packet ID
        packet_id = hashlib.sha256(f"{file_path}{datetime.utcnow().isoformat()}".encode()).hexdigest()
        
        return {
            "packet_version": "1.0",
            "packet_id": packet_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": {
                "mcp_server": self.server_process.config.name,
                "server_version": "1.0.0",
                "original_location": file_path,
                "content_type": "document",
                "extraction_method": "mock_extractor"
            },
            "metadata": {
                "title": Path(file_path).stem,
                "author": metadata.get("author", "Unknown"),
                **metadata
            },
            "content": {
                "vector_data": {
                    "chunks": [
                        {
                            "chunk_id": "chunk_1",
                            "text": f"Mock content from {file_path}",
                            "chunk_metadata": {"file": file_path}
                        }
                    ],
                    "embedding_model": "BAAI/bge-small-en-v1.5",
                    "chunk_strategy": "mock"
                }
            },
            "processing_hints": {
                "priority_brain": "vector",
                "semantic_weight": 0.8,
                "content_classification": "technical"
            },
            "quality_metrics": {
                "extraction_confidence": 0.9,
                "content_completeness": 0.95
            }
        }


class NancyMCPHost:
    """
    Nancy Core MCP Host - manages MCP servers and processes Knowledge Packets.
    """
    
    def __init__(self, config: NancyConfiguration):
        self.config = config
        self.server_processes: Dict[str, MCPServerProcess] = {}
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.packet_validator = KnowledgePacketValidator()
        self.packet_queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Brain instances for packet processing
        self.vector_brain = VectorBrain()
        self.analytical_brain = AnalyticalBrain()
        self.graph_brain = GraphBrain()
        
        # Metrics
        self.packets_processed = 0
        self.packets_failed = 0
        self.start_time = None
    
    async def start(self) -> bool:
        """Start the MCP host and all configured servers."""
        logger.info("Starting Nancy MCP Host...")
        
        try:
            # Start MCP servers
            if not await self._start_mcp_servers():
                logger.error("Failed to start MCP servers")
                return False
            
            # Start packet processing
            self.processing_task = asyncio.create_task(self._process_packet_queue())
            self.is_running = True
            self.start_time = datetime.utcnow()
            
            logger.info(f"Nancy MCP Host started with {len(self.mcp_clients)} servers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Nancy MCP Host: {e}")
            return False
    
    async def stop(self):
        """Stop the MCP host and all servers."""
        logger.info("Stopping Nancy MCP Host...")
        
        self.is_running = False
        
        # Stop packet processing
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        # Stop MCP servers
        await self._stop_mcp_servers()
        
        logger.info("Nancy MCP Host stopped")
    
    async def _start_mcp_servers(self) -> bool:
        """Start all configured MCP servers."""
        success_count = 0
        
        for server_config in self.config.mcp_servers.enabled_servers:
            if not server_config.auto_start:
                logger.info(f"Skipping auto-start for server {server_config.name}")
                continue
            
            try:
                # Create server process
                server_process = MCPServerProcess(server_config)
                self.server_processes[server_config.name] = server_process
                
                # Start server
                if await server_process.start():
                    # Create MCP client
                    client = MCPClient(server_process)
                    if await client.initialize():
                        self.mcp_clients[server_config.name] = client
                        success_count += 1
                        logger.info(f"Successfully started MCP server: {server_config.name}")
                    else:
                        logger.error(f"Failed to initialize MCP client for {server_config.name}")
                else:
                    logger.error(f"Failed to start MCP server: {server_config.name}")
                    
            except Exception as e:
                logger.error(f"Error starting MCP server {server_config.name}: {e}")
        
        # Allow Nancy to run with zero MCP servers - this is valid for core functionality
        total_servers = len(self.config.mcp_servers.enabled_servers)
        if total_servers == 0:
            logger.info("No MCP servers configured - Nancy running in core-only mode")
            return True
        
        # If servers are configured, at least one must start successfully
        return success_count > 0
    
    async def _stop_mcp_servers(self):
        """Stop all MCP servers."""
        for server_name, server_process in self.server_processes.items():
            try:
                await server_process.stop()
            except Exception as e:
                logger.error(f"Error stopping MCP server {server_name}: {e}")
        
        self.server_processes.clear()
        self.mcp_clients.clear()
    
    async def ingest_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None, 
                         server_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest a file through appropriate MCP server.
        
        Args:
            file_path: Path to file to ingest
            metadata: Additional metadata
            server_name: Specific MCP server to use (if None, auto-select)
            
        Returns:
            Ingestion result dictionary
        """
        if not self.is_running:
            raise RuntimeError("MCP Host is not running")
        
        if metadata is None:
            metadata = {}
        
        try:
            # Select MCP server
            if server_name:
                if server_name not in self.mcp_clients:
                    raise ValueError(f"MCP server {server_name} not available")
                client = self.mcp_clients[server_name]
            else:
                client = self._select_mcp_server_for_file(file_path)
                if not client:
                    raise ValueError("No suitable MCP server found for file")
            
            # Request ingestion from MCP server
            knowledge_packet = await client.ingest_file(file_path, metadata)
            
            # Queue packet for processing
            await self.packet_queue.put(knowledge_packet)
            
            return {
                "status": "success",
                "packet_id": knowledge_packet.packet_id,
                "message": "File queued for processing"
            }
            
        except Exception as e:
            logger.error(f"Failed to ingest file {file_path}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _select_mcp_server_for_file(self, file_path: str) -> Optional[MCPClient]:
        """Select appropriate MCP server based on file type."""
        file_ext = Path(file_path).suffix.lower()
        
        # Route based on file extension and server capabilities
        for server_name, server_process in self.server_processes.items():
            if hasattr(server_process.config, 'supported_extensions'):
                if file_ext in server_process.config.supported_extensions:
                    if server_name in self.mcp_clients:
                        logger.info(f"Selected MCP server {server_name} for file type {file_ext}")
                        return self.mcp_clients[server_name]
        
        # Specific routing for known file types
        spreadsheet_extensions = ['.xlsx', '.xls', '.csv']
        if file_ext in spreadsheet_extensions:
            if "nancy-spreadsheet-server" in self.mcp_clients:
                logger.info(f"Selected spreadsheet server for {file_ext} file")
                return self.mcp_clients["nancy-spreadsheet-server"]
        
        # Fallback to document server for text-based files
        document_extensions = ['.txt', '.md', '.pdf', '.doc', '.docx']
        if file_ext in document_extensions:
            if "nancy-document-server" in self.mcp_clients:
                logger.info(f"Selected document server for {file_ext} file")
                return self.mcp_clients["nancy-document-server"]
        
        # Return first available client as last resort
        if self.mcp_clients:
            client_name = next(iter(self.mcp_clients.keys()))
            logger.warning(f"No specific server found for {file_ext}, using {client_name}")
            return next(iter(self.mcp_clients.values()))
        
        logger.error(f"No MCP servers available for file {file_path}")
        return None
    
    async def _process_packet_queue(self):
        """Process Knowledge Packets from the queue."""
        logger.info("Started Knowledge Packet processing")
        
        while self.is_running:
            try:
                # Get packet from queue with timeout
                packet = await asyncio.wait_for(
                    self.packet_queue.get(),
                    timeout=1.0
                )
                
                await self._process_knowledge_packet(packet)
                self.packets_processed += 1
                
            except asyncio.TimeoutError:
                # Normal timeout, continue processing
                continue
            except Exception as e:
                logger.error(f"Error processing packet: {e}")
                self.packets_failed += 1
    
    async def _process_knowledge_packet(self, packet: NancyKnowledgePacket):
        """
        Process a Knowledge Packet through the Four-Brain architecture.
        
        Args:
            packet: Validated Knowledge Packet to process
        """
        try:
            logger.debug(f"Processing Knowledge Packet {packet.packet_id}")
            
            # Validate packet
            self.packet_validator.validate_packet(packet)
            
            # Route to appropriate brains based on content and hints
            await self._route_to_brains(packet)
            
            logger.info(f"Successfully processed Knowledge Packet {packet.packet_id}")
            
        except Exception as e:
            logger.error(f"Failed to process Knowledge Packet {packet.packet_id}: {e}")
            raise
    
    async def _route_to_brains(self, packet: NancyKnowledgePacket):
        """Route packet content to appropriate brains for storage."""
        
        # Store in Vector Brain if vector data present
        if packet.has_vector_data():
            await self._store_vector_content(packet)
        
        # Store in Analytical Brain if analytical data present
        if packet.has_analytical_data():
            await self._store_analytical_content(packet)
        
        # Store in Graph Brain if graph data present
        if packet.has_graph_data():
            await self._store_graph_content(packet)
        
        # Always store basic metadata in Analytical Brain
        await self._store_packet_metadata(packet)
    
    async def _store_vector_content(self, packet: NancyKnowledgePacket):
        """Store vector data in Vector Brain."""
        try:
            vector_data = packet.content.get("vector_data", {})
            chunks = vector_data.get("chunks", [])
            
            for chunk in chunks:
                # Extract chunk data
                chunk_text = chunk.get("text", "")
                chunk_metadata = chunk.get("chunk_metadata", {})
                
                # Add packet metadata to chunk
                chunk_metadata.update({
                    "packet_id": packet.packet_id,
                    "source_file": packet.source.get("original_location"),
                    "author": packet.metadata.get("author"),
                    "title": packet.metadata.get("title")
                })
                
                # Store in vector brain
                self.vector_brain.add_text(
                    text=chunk_text,
                    metadata=chunk_metadata,
                    doc_id=f"{packet.packet_id}_{chunk.get('chunk_id', 'chunk')}"
                )
            
            logger.debug(f"Stored {len(chunks)} chunks in Vector Brain for packet {packet.packet_id}")
            
        except Exception as e:
            logger.error(f"Failed to store vector content for packet {packet.packet_id}: {e}")
            raise
    
    async def _store_analytical_content(self, packet: NancyKnowledgePacket):
        """Store analytical data in Analytical Brain."""
        try:
            analytical_data = packet.content.get("analytical_data", {})
            
            # Store structured fields
            structured_fields = analytical_data.get("structured_fields", {})
            if structured_fields:
                # TODO: Implement structured data storage in analytical brain
                logger.debug(f"Would store structured fields: {list(structured_fields.keys())}")
            
            # Store table data
            table_data = analytical_data.get("table_data", [])
            for table in table_data:
                # TODO: Implement table data storage in analytical brain
                table_name = table.get("table_name")
                logger.debug(f"Would store table: {table_name}")
            
            logger.debug(f"Stored analytical content in Analytical Brain for packet {packet.packet_id}")
            
        except Exception as e:
            logger.error(f"Failed to store analytical content for packet {packet.packet_id}: {e}")
            raise
    
    async def _store_graph_content(self, packet: NancyKnowledgePacket):
        """Store graph data in Graph Brain."""
        try:
            graph_data = packet.content.get("graph_data", {})
            
            # Store entities
            entities = graph_data.get("entities", [])
            for entity in entities:
                entity_type = entity.get("type")
                entity_name = entity.get("name")
                properties = entity.get("properties", {})
                
                # Add packet context to properties
                properties.update({
                    "packet_id": packet.packet_id,
                    "source_file": packet.source.get("original_location")
                })
                
                # Create node in graph brain
                self.graph_brain.add_concept_node(entity_name, entity_type)
            
            # Store relationships
            relationships = graph_data.get("relationships", [])
            for rel in relationships:
                source = rel.get("source", {})
                target = rel.get("target", {})
                rel_type = rel.get("relationship")
                rel_props = rel.get("properties", {})
                
                # Add packet context
                context = f"From {packet.metadata.get('title', 'Unknown')} (packet: {packet.packet_id})"
                
                # Create relationship in graph brain
                self.graph_brain.add_relationship(
                    source_node_label=source.get("type"),
                    source_node_name=source.get("name"),
                    relationship_type=rel_type,
                    target_node_label=target.get("type"),
                    target_node_name=target.get("name"),
                    context=context
                )
            
            logger.debug(f"Stored {len(entities)} entities and {len(relationships)} relationships in Graph Brain for packet {packet.packet_id}")
            
        except Exception as e:
            logger.error(f"Failed to store graph content for packet {packet.packet_id}: {e}")
            raise
    
    async def _store_packet_metadata(self, packet: NancyKnowledgePacket):
        """Store packet metadata in Analytical Brain."""
        try:
            # Insert document metadata
            self.analytical_brain.insert_document_metadata(
                doc_id=packet.packet_id,
                filename=packet.metadata.get("title", "Unknown"),
                size=packet.metadata.get("file_size", 0),
                file_type=packet.source.get("content_type", "unknown")
            )
            
            logger.debug(f"Stored packet metadata in Analytical Brain for packet {packet.packet_id}")
            
        except Exception as e:
            logger.error(f"Failed to store packet metadata for packet {packet.packet_id}: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on MCP host and servers."""
        status = {
            "nancy_mcp_host": {
                "status": "healthy" if self.is_running else "stopped",
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0,
                "packets_processed": self.packets_processed,
                "packets_failed": self.packets_failed,
                "queue_size": self.packet_queue.qsize()
            },
            "mcp_servers": {}
        }
        
        # Check each MCP server
        for server_name, server_process in self.server_processes.items():
            is_healthy = await server_process.health_check()
            status["mcp_servers"][server_name] = {
                "status": "healthy" if is_healthy else "unhealthy",
                "last_health_check": server_process.last_health_check.isoformat() if server_process.last_health_check else None,
                "capabilities": server_process.config.capabilities
            }
        
        return status
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "packets_processed": self.packets_processed,
            "packets_failed": self.packets_failed,
            "success_rate": (self.packets_processed / (self.packets_processed + self.packets_failed)) if (self.packets_processed + self.packets_failed) > 0 else 0,
            "active_servers": len([s for s in self.server_processes.values() if s.is_healthy]),
            "total_servers": len(self.server_processes),
            "queue_size": self.packet_queue.qsize(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
        }