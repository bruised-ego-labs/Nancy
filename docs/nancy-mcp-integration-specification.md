# Nancy MCP Integration Specification
## Model Context Protocol Integration Patterns and Communication Standards

**Document Version:** 1.0  
**Date:** August 15, 2025  
**Author:** Strategic Technical Architect  
**Status:** Technical Specification  

---

## Table of Contents

1. [Overview](#1-overview)
2. [MCP Protocol Foundation](#2-mcp-protocol-foundation)
3. [Nancy as MCP Host](#3-nancy-as-mcp-host)
4. [MCP Server Standards](#4-mcp-server-standards)
5. [Communication Patterns](#5-communication-patterns)
6. [Authentication and Security](#6-authentication-and-security)
7. [Error Handling and Retry Logic](#7-error-handling-and-retry-logic)
8. [Performance and Monitoring](#8-performance-and-monitoring)
9. [Development Guidelines](#9-development-guidelines)
10. [Testing and Validation](#10-testing-and-validation)

---

## 1. Overview

This specification defines how Nancy Core integrates with the Model Context Protocol (MCP) to create a composable intelligence platform. Nancy acts as an MCP host orchestrating multiple specialized MCP servers for data ingestion while maintaining its Four-Brain architectural advantages.

### 1.1 Strategic Goals

- **Composable Architecture**: Enable adding new data sources without modifying Nancy Core
- **Enterprise Flexibility**: Support diverse deployment and integration requirements
- **Preserved Intelligence**: Maintain Nancy's Four-Brain analytical capabilities
- **Ecosystem Growth**: Enable third-party MCP server development

### 1.2 Integration Patterns

```
┌─────────────────────────────────────────────────────────────────┐
│                      Nancy Core (MCP Host)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐    ┌─────────────────────────────────┐  │
│  │   MCP Manager       │    │    Four-Brain Orchestrator     │  │
│  │                     │    │                                 │  │
│  │ ┌─────────────────┐ │    │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │  │
│  │ │ Client Pool     │ │    │ │ Vec │ │ Ana │ │ Grp │ │ Lng │ │  │
│  │ │ Connection Mgmt │ │    │ │ tor │ │ lyt │ │ aph │ │ uis │ │  │
│  │ │ Message Routing │ │    │ │     │ │ ical│ │     │ │ tic │ │  │
│  │ └─────────────────┘ │    │ └─────┘ └─────┘ └─────┘ └─────┘ │  │
│  └─────────────────────┘    └─────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    MCP Protocol Layer                           │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Document  │ │ Spreadsheet │ │  Codebase   │ │   Slack     │ │
│ │ MCP Server  │ │ MCP Server  │ │ MCP Server  │ │ MCP Server  │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. MCP Protocol Foundation

### 2.1 Core MCP Concepts

The Model Context Protocol provides standardized communication between AI systems and external tools/data sources. Nancy extends MCP with domain-specific patterns for knowledge management.

**Key MCP Components**:
- **Host**: Nancy Core - manages MCP clients and orchestrates requests
- **Server**: Specialized ingestion servers - handle specific data types
- **Messages**: JSON-RPC 2.0 protocol for communication
- **Tools**: Server-provided capabilities (file ingestion, real-time sync, etc.)
- **Resources**: Server-managed data sources (files, databases, APIs)

### 2.2 Nancy MCP Extensions

Nancy extends standard MCP with specialized patterns:

```typescript
// Nancy-specific MCP message types
interface NancyMCPMessage extends MCPMessage {
  nancy_version: "1.0";
  packet_schema: "nancy-knowledge-packet-v1.0";
  brain_routing_hints?: BrainRoutingHints;
}

interface BrainRoutingHints {
  priority_brain?: "vector" | "analytical" | "graph" | "auto";
  semantic_weight?: number; // 0-1
  relationship_importance?: number; // 0-1
  content_classification?: "technical" | "financial" | "strategic" | "operational";
}
```

### 2.3 Standard MCP Operations Extended for Nancy

```typescript
// Standard MCP operations with Nancy enhancements
interface NancyMCPOperations {
  // Core MCP methods
  initialize(params: InitializeParams): InitializeResult;
  list_tools(): Tool[];
  call_tool(params: CallToolParams): CallToolResult;
  list_resources(): Resource[];
  read_resource(params: ReadResourceParams): ReadResourceResult;
  
  // Nancy-specific extensions
  ingest_content(params: IngestContentParams): NancyKnowledgePacket;
  validate_packet(packet: NancyKnowledgePacket): ValidationResult;
  get_ingestion_status(packet_id: string): IngestionStatus;
  setup_real_time_sync(params: RealTimeSyncParams): SyncConfiguration;
}
```

---

## 3. Nancy as MCP Host

### 3.1 MCP Host Implementation

Nancy Core implements a sophisticated MCP host that manages multiple client connections while maintaining high performance and reliability.

```python
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

from mcp import Client, ClientSession, StdioServerParameters
from nancy.core.knowledge_packet import NancyKnowledgePacket
from nancy.core.orchestrator import FourBrainOrchestrator

@dataclass
class MCPServerConfig:
    name: str
    executable: str
    args: List[str]
    capabilities: List[str]
    auto_start: bool
    environment: Dict[str, str]
    health_check_interval: int

class NancyMCPHost:
    """
    Nancy Core MCP Host - manages MCP client connections and orchestrates 
    knowledge packet processing through the Four-Brain architecture.
    """
    
    def __init__(self, config: NancyCoreConfig):
        self.config = config
        self.clients: Dict[str, Client] = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.orchestrator = FourBrainOrchestrator(config.brains)
        self.packet_queue = asyncio.Queue()
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger(__name__)
        
    async def start(self):
        """Initialize MCP host and start all configured servers"""
        self.logger.info("Starting Nancy MCP Host...")
        
        # Start all configured MCP servers
        for server_config in self.config.mcp_servers.enabled_servers:
            await self.start_mcp_server(server_config)
            
        # Start packet processing worker
        self.packet_processing_task = asyncio.create_task(
            self.process_packet_queue()
        )
        
        self.logger.info(f"Nancy MCP Host started with {len(self.clients)} servers")
        
    async def stop(self):
        """Gracefully shutdown MCP host and all connections"""
        self.logger.info("Stopping Nancy MCP Host...")
        
        # Stop packet processing
        if hasattr(self, 'packet_processing_task'):
            self.packet_processing_task.cancel()
            
        # Stop health checks
        for task in self.health_check_tasks.values():
            task.cancel()
            
        # Close all MCP sessions
        for session in self.sessions.values():
            await session.close()
            
        self.logger.info("Nancy MCP Host stopped")
        
    async def start_mcp_server(self, config: MCPServerConfig):
        """Start and connect to an MCP server"""
        try:
            self.logger.info(f"Starting MCP server: {config.name}")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=config.executable,
                args=config.args,
                env=config.environment
            )
            
            # Create client and session
            client = Client(server_params)
            session = await client.connect()
            
            # Initialize server
            init_result = await session.initialize()
            self.logger.info(f"Server {config.name} initialized: {init_result}")
            
            # Store client and session
            self.clients[config.name] = client
            self.sessions[config.name] = session
            
            # Start health checking if configured
            if config.health_check_interval > 0:
                self.health_check_tasks[config.name] = asyncio.create_task(
                    self.health_check_server(config.name, config.health_check_interval)
                )
                
        except Exception as e:
            self.logger.error(f"Failed to start MCP server {config.name}: {e}")
            raise
            
    async def health_check_server(self, server_name: str, interval: int):
        """Periodically health check an MCP server"""
        while True:
            try:
                await asyncio.sleep(interval)
                session = self.sessions.get(server_name)
                if session:
                    # Ping server with list_tools request
                    tools = await session.list_tools()
                    self.logger.debug(f"Health check OK for {server_name}: {len(tools)} tools")
                else:
                    self.logger.warning(f"No session for health check: {server_name}")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check failed for {server_name}: {e}")
                # Could implement automatic restart logic here
                
    async def ingest_content(self, server_name: str, source_path: str, 
                           metadata: Dict[str, Any]) -> str:
        """
        Request content ingestion from a specific MCP server
        Returns packet_id for tracking
        """
        session = self.sessions.get(server_name)
        if not session:
            raise ValueError(f"MCP server not available: {server_name}")
            
        try:
            # Call ingest_content tool on the server
            result = await session.call_tool("ingest_content", {
                "source_path": source_path,
                "metadata": metadata,
                "packet_schema": "nancy-knowledge-packet-v1.0"
            })
            
            # Parse the Nancy Knowledge Packet from result
            packet_data = json.loads(result.content[0].text)
            packet = NancyKnowledgePacket.from_dict(packet_data)
            
            # Validate packet schema
            validation_result = self.validate_knowledge_packet(packet)
            if not validation_result.is_valid:
                raise ValueError(f"Invalid knowledge packet: {validation_result.errors}")
            
            # Queue packet for processing
            await self.packet_queue.put(packet)
            
            self.logger.info(f"Queued knowledge packet {packet.packet_id} from {server_name}")
            return packet.packet_id
            
        except Exception as e:
            self.logger.error(f"Content ingestion failed for {server_name}: {e}")
            raise
            
    async def process_packet_queue(self):
        """Process knowledge packets from the queue through Four-Brain architecture"""
        while True:
            try:
                # Get next packet from queue
                packet = await self.packet_queue.get()
                
                # Create processing task for this packet
                task_id = str(uuid.uuid4())
                self.processing_tasks[task_id] = asyncio.create_task(
                    self.process_knowledge_packet(packet)
                )
                
                # Clean up completed tasks
                completed_tasks = [
                    task_id for task_id, task in self.processing_tasks.items()
                    if task.done()
                ]
                for task_id in completed_tasks:
                    del self.processing_tasks[task_id]
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in packet processing queue: {e}")
                
    async def process_knowledge_packet(self, packet: NancyKnowledgePacket):
        """Process a knowledge packet through the Four-Brain architecture"""
        try:
            self.logger.info(f"Processing knowledge packet {packet.packet_id}")
            
            # Route packet content to appropriate brains
            await self.route_packet_to_brains(packet)
            
            # Update ingestion metrics
            self.update_ingestion_metrics(packet)
            
            self.logger.info(f"Successfully processed packet {packet.packet_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to process packet {packet.packet_id}: {e}")
            # Could implement retry logic or dead letter queue here
            
    async def route_packet_to_brains(self, packet: NancyKnowledgePacket):
        """Route packet content to appropriate brains for storage"""
        
        # Vector Brain: Store semantic content
        if packet.content.vector_data:
            await self.store_vector_content(packet)
            
        # Analytical Brain: Store structured data  
        if packet.content.analytical_data:
            await self.store_analytical_content(packet)
            
        # Graph Brain: Store relationships
        if packet.content.graph_data:
            await self.store_graph_content(packet)
            
    async def store_vector_content(self, packet: NancyKnowledgePacket):
        """Store vector content in the Vector Brain"""
        try:
            vector_data = packet.content.vector_data
            
            # Prepare documents for vector storage
            documents = []
            metadatas = []
            ids = []
            
            for chunk in vector_data.chunks:
                documents.append(chunk.text)
                metadatas.append({
                    "packet_id": packet.packet_id,
                    "source": packet.metadata.title,
                    "author": packet.metadata.author,
                    "chunk_id": chunk.chunk_id,
                    **chunk.chunk_metadata
                })
                ids.append(f"{packet.packet_id}_{chunk.chunk_id}")
                
            # Store in vector brain
            await self.orchestrator.vector_brain.add_documents(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.debug(f"Stored {len(documents)} chunks in Vector Brain")
            
        except Exception as e:
            self.logger.error(f"Vector storage failed for packet {packet.packet_id}: {e}")
            raise
            
    async def store_analytical_content(self, packet: NancyKnowledgePacket):
        """Store analytical content in the Analytical Brain"""
        try:
            analytical_data = packet.content.analytical_data
            
            # Store structured fields
            if analytical_data.structured_fields:
                await self.orchestrator.analytical_brain.insert_structured_data(
                    packet_id=packet.packet_id,
                    data=analytical_data.structured_fields,
                    metadata=packet.metadata
                )
                
            # Store table data
            if analytical_data.table_data:
                for table in analytical_data.table_data:
                    await self.orchestrator.analytical_brain.insert_table_data(
                        packet_id=packet.packet_id,
                        table_name=table.table_name,
                        columns=table.columns,
                        rows=table.rows,
                        metadata=packet.metadata
                    )
                    
            self.logger.debug(f"Stored analytical data for packet {packet.packet_id}")
            
        except Exception as e:
            self.logger.error(f"Analytical storage failed for packet {packet.packet_id}: {e}")
            raise
            
    async def store_graph_content(self, packet: NancyKnowledgePacket):
        """Store graph content in the Graph Brain"""
        try:
            graph_data = packet.content.graph_data
            
            # Store entities
            if graph_data.entities:
                for entity in graph_data.entities:
                    await self.orchestrator.graph_brain.add_entity(
                        entity_type=entity.type,
                        entity_name=entity.name,
                        properties=entity.properties,
                        packet_id=packet.packet_id
                    )
                    
            # Store relationships
            if graph_data.relationships:
                for relationship in graph_data.relationships:
                    await self.orchestrator.graph_brain.add_relationship(
                        source_type=relationship.source.type,
                        source_name=relationship.source.name,
                        relationship_type=relationship.relationship,
                        target_type=relationship.target.type,
                        target_name=relationship.target.name,
                        properties=relationship.properties,
                        packet_id=packet.packet_id
                    )
                    
            self.logger.debug(f"Stored graph data for packet {packet.packet_id}")
            
        except Exception as e:
            self.logger.error(f"Graph storage failed for packet {packet.packet_id}: {e}")
            raise
    
    def validate_knowledge_packet(self, packet: NancyKnowledgePacket) -> ValidationResult:
        """Validate Nancy Knowledge Packet against schema"""
        # Implementation would validate against the JSON schema
        # This is a placeholder for the validation logic
        return ValidationResult(is_valid=True, errors=[])
        
    def update_ingestion_metrics(self, packet: NancyKnowledgePacket):
        """Update metrics for ingestion monitoring"""
        # Implementation would update metrics for monitoring
        pass
```

### 3.2 Client Pool Management

```python
class MCPClientPool:
    """Manages connection pooling and load balancing for MCP clients"""
    
    def __init__(self, max_connections_per_server: int = 5):
        self.max_connections = max_connections_per_server
        self.client_pools: Dict[str, List[ClientSession]] = {}
        self.connection_counts: Dict[str, int] = {}
        self.lock = asyncio.Lock()
        
    async def get_session(self, server_name: str) -> ClientSession:
        """Get an available session for the specified server"""
        async with self.lock:
            if server_name not in self.client_pools:
                self.client_pools[server_name] = []
                self.connection_counts[server_name] = 0
                
            # Try to get an existing session
            pool = self.client_pools[server_name]
            for session in pool:
                if not session.is_busy():
                    return session
                    
            # Create new session if under limit
            if self.connection_counts[server_name] < self.max_connections:
                session = await self.create_new_session(server_name)
                pool.append(session)
                self.connection_counts[server_name] += 1
                return session
                
            # Wait for available session
            return await self.wait_for_available_session(server_name)
            
    async def create_new_session(self, server_name: str) -> ClientSession:
        """Create a new MCP client session"""
        # Implementation depends on server configuration
        pass
        
    async def wait_for_available_session(self, server_name: str) -> ClientSession:
        """Wait for an available session when pool is full"""
        # Implementation would wait for session availability
        pass
```

---

## 4. MCP Server Standards

### 4.1 Standard Nancy MCP Server Interface

All Nancy MCP servers must implement the following interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio
import json
from mcp import Server
from nancy.schemas.knowledge_packet import NancyKnowledgePacket

class NancyMCPServer(ABC):
    """
    Abstract base class for Nancy MCP servers.
    All Nancy MCP servers must implement this interface.
    """
    
    def __init__(self, server_name: str, version: str):
        self.server_name = server_name
        self.version = version
        self.server = Server(server_name)
        self.capabilities: List[str] = []
        self.supported_file_types: List[str] = []
        self.setup_server()
        
    @abstractmethod
    def get_server_name(self) -> str:
        """Return unique server name (e.g., 'nancy-spreadsheet-server')"""
        pass
        
    @abstractmethod
    def get_version(self) -> str:
        """Return server version (e.g., '1.2.0')"""
        pass
        
    @abstractmethod  
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        pass
        
    @abstractmethod
    def get_supported_file_types(self) -> List[str]:
        """Return list of supported file extensions"""
        pass
        
    @abstractmethod
    async def ingest_content(self, source_path: str, 
                           metadata: Dict[str, Any]) -> NancyKnowledgePacket:
        """
        Main ingestion method - convert source content to Nancy Knowledge Packet
        
        Args:
            source_path: Path to content to ingest
            metadata: Additional metadata (author, project, etc.)
            
        Returns:
            NancyKnowledgePacket: Standardized packet for Nancy Core processing
        """
        pass
        
    @abstractmethod
    async def validate_source(self, source_path: str) -> bool:
        """Validate that source can be processed by this server"""
        pass
        
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Return server health status"""
        pass
        
    # Standard MCP server setup
    def setup_server(self):
        """Set up standard MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools():
            """List available tools"""
            return [
                {
                    "name": "ingest_content",
                    "description": f"Ingest content using {self.server_name}",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "source_path": {"type": "string"},
                            "metadata": {"type": "object"}
                        },
                        "required": ["source_path"]
                    }
                },
                {
                    "name": "validate_source", 
                    "description": "Validate source compatibility",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "source_path": {"type": "string"}
                        },
                        "required": ["source_path"]
                    }
                },
                {
                    "name": "health_check",
                    "description": "Check server health",
                    "inputSchema": {"type": "object", "properties": {}}
                }
            ]
            
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]):
            """Handle tool calls"""
            if name == "ingest_content":
                packet = await self.ingest_content(
                    arguments["source_path"],
                    arguments.get("metadata", {})
                )
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(packet.to_dict())
                        }
                    ]
                }
            elif name == "validate_source":
                is_valid = await self.validate_source(arguments["source_path"])
                return {
                    "content": [
                        {
                            "type": "text", 
                            "text": json.dumps({"valid": is_valid})
                        }
                    ]
                }
            elif name == "health_check":
                health = await self.health_check()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(health)
                        }
                    ]
                }
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        @self.server.list_resources()
        async def list_resources():
            """List available resources"""
            return []  # Override in subclasses if needed
            
    async def run(self):
        """Run the MCP server"""
        async with self.server.run() as ctx:
            await ctx.request_loop()
            
    # Optional: Real-time capabilities
    async def setup_real_time_sync(self, watch_path: str) -> bool:
        """Set up real-time file watching if supported"""
        return False
        
    async def handle_file_change(self, file_path: str, change_type: str):
        """Handle real-time file changes if supported"""
        pass
        
    # Utility methods
    def generate_packet_id(self, source_path: str, content: bytes) -> str:
        """Generate unique packet ID"""
        import hashlib
        return hashlib.sha256(source_path.encode() + content).hexdigest()
        
    def create_base_metadata(self, source_path: str, 
                           additional_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create base metadata for Nancy Knowledge Packet"""
        import os
        from datetime import datetime
        
        base_metadata = {
            "title": os.path.basename(source_path),
            "created_at": datetime.now().isoformat(),
            "file_size": os.path.getsize(source_path) if os.path.exists(source_path) else 0,
            "source_server": self.server_name,
            "server_version": self.version
        }
        
        # Merge with additional metadata
        base_metadata.update(additional_metadata)
        return base_metadata
```

### 4.2 Example Implementation: Document MCP Server

```python
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Any
import aiofiles
from nancy.mcp.base_server import NancyMCPServer
from nancy.schemas.knowledge_packet import NancyKnowledgePacket, VectorData, AnalyticalData

class DocumentMCPServer(NancyMCPServer):
    """MCP server for document ingestion (PDF, DOCX, TXT, MD)"""
    
    def __init__(self):
        super().__init__("nancy-document-server", "1.0.0")
        
    def get_server_name(self) -> str:
        return "nancy-document-server"
        
    def get_version(self) -> str:
        return "1.0.0"
        
    def get_capabilities(self) -> List[str]:
        return ["file_upload", "text_extraction", "metadata_extraction"]
        
    def get_supported_file_types(self) -> List[str]:
        return [".pdf", ".docx", ".txt", ".md", ".rtf"]
        
    async def validate_source(self, source_path: str) -> bool:
        """Validate that file can be processed"""
        if not os.path.exists(source_path):
            return False
            
        file_ext = Path(source_path).suffix.lower()
        return file_ext in self.get_supported_file_types()
        
    async def ingest_content(self, source_path: str, 
                           metadata: Dict[str, Any]) -> NancyKnowledgePacket:
        """Ingest document content into Nancy Knowledge Packet"""
        
        # Read file content
        async with aiofiles.open(source_path, 'rb') as f:
            content_bytes = await f.read()
            
        # Extract text based on file type
        text_content = await self.extract_text(source_path, content_bytes)
        
        # Generate packet ID
        packet_id = self.generate_packet_id(source_path, content_bytes)
        
        # Create metadata
        packet_metadata = self.create_base_metadata(source_path, metadata)
        packet_metadata["content_hash"] = hashlib.sha256(content_bytes).hexdigest()
        
        # Chunk text for vector storage
        chunks = self.chunk_text(text_content, chunk_size=512, overlap=50)
        
        # Create vector data
        vector_data = VectorData(
            chunks=[
                {
                    "chunk_id": f"chunk_{i}",
                    "text": chunk,
                    "chunk_metadata": {"chunk_index": i}
                }
                for i, chunk in enumerate(chunks)
            ],
            embedding_model="BAAI/bge-small-en-v1.5",
            chunk_strategy="semantic_paragraphs"
        )
        
        # Create analytical data
        analytical_data = AnalyticalData(
            structured_fields={
                "file_type": Path(source_path).suffix.lower(),
                "file_size": len(content_bytes),
                "chunk_count": len(chunks),
                "word_count": len(text_content.split()),
                "char_count": len(text_content)
            }
        )
        
        # Create knowledge packet
        packet = NancyKnowledgePacket(
            packet_version="1.0",
            packet_id=packet_id,
            timestamp=datetime.now().isoformat(),
            source={
                "mcp_server": self.server_name,
                "server_version": self.version,
                "original_location": source_path,
                "content_type": "document",
                "extraction_method": "document_parser"
            },
            metadata=packet_metadata,
            content={
                "vector_data": vector_data,
                "analytical_data": analytical_data
            },
            processing_hints={
                "priority_brain": "vector",
                "semantic_weight": 0.9,
                "relationship_importance": 0.3,
                "content_classification": "technical"
            },
            quality_metrics={
                "extraction_confidence": 0.95,
                "content_completeness": 0.9,
                "text_quality_score": 0.95
            }
        )
        
        return packet
        
    async def extract_text(self, file_path: str, content_bytes: bytes) -> str:
        """Extract text from different file types"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == ".txt" or file_ext == ".md":
            return content_bytes.decode('utf-8', errors='ignore')
        elif file_ext == ".pdf":
            return await self.extract_pdf_text(content_bytes)
        elif file_ext == ".docx":
            return await self.extract_docx_text(content_bytes)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
            
    async def extract_pdf_text(self, content_bytes: bytes) -> str:
        """Extract text from PDF using PyPDF2 or similar"""
        # Implementation would use PyPDF2, pdfplumber, or similar
        pass
        
    async def extract_docx_text(self, content_bytes: bytes) -> str:
        """Extract text from DOCX using python-docx"""
        # Implementation would use python-docx
        pass
        
    def chunk_text(self, text: str, chunk_size: int = 512, 
                   overlap: int = 50) -> List[str]:
        """Chunk text into overlapping segments"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size // 2:
                    end = start + last_period + 1
                    chunk = text[start:end]
                    
            chunks.append(chunk.strip())
            start = end - overlap
            
        return chunks
        
    async def health_check(self) -> Dict[str, Any]:
        """Return server health status"""
        return {
            "status": "healthy",
            "server_name": self.server_name,
            "version": self.version,
            "supported_types": self.get_supported_file_types(),
            "capabilities": self.get_capabilities(),
            "timestamp": datetime.now().isoformat()
        }

# Entry point for MCP server
async def main():
    server = DocumentMCPServer()
    await server.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## 5. Communication Patterns

### 5.1 Synchronous vs Asynchronous Patterns

Nancy supports both synchronous and asynchronous communication patterns depending on use case requirements.

#### Synchronous Pattern (Small Files, Immediate Processing)
```python
# Client requests immediate ingestion and waits for completion
async def sync_ingest_pattern(host: NancyMCPHost, server_name: str, 
                             file_path: str, metadata: Dict[str, Any]) -> str:
    """Synchronous ingestion pattern for small files"""
    
    # Request ingestion (blocks until packet is generated)
    packet_id = await host.ingest_content(server_name, file_path, metadata)
    
    # Wait for processing completion (optional)
    await host.wait_for_processing_completion(packet_id, timeout=30)
    
    return packet_id
```

#### Asynchronous Pattern (Large Files, Background Processing)
```python
# Client submits for processing and checks status later
async def async_ingest_pattern(host: NancyMCPHost, server_name: str,
                              file_path: str, metadata: Dict[str, Any]) -> str:
    """Asynchronous ingestion pattern for large files"""
    
    # Submit for processing (non-blocking)
    packet_id = await host.submit_for_ingestion(server_name, file_path, metadata)
    
    # Return immediately with packet_id for status checking
    return packet_id

async def check_ingestion_status(host: NancyMCPHost, packet_id: str) -> Dict[str, Any]:
    """Check processing status"""
    return await host.get_ingestion_status(packet_id)
```

#### Streaming Pattern (Real-time Data)
```python
# Continuous streaming of data updates
async def streaming_pattern(host: NancyMCPHost, server_name: str):
    """Streaming pattern for real-time data"""
    
    # Set up real-time sync
    stream = await host.setup_real_time_stream(server_name)
    
    async for packet in stream:
        # Process packets as they arrive
        await host.process_packet_immediately(packet)
```

### 5.2 Batch Processing Patterns

```python
class BatchProcessor:
    """Handles batch processing of multiple files"""
    
    def __init__(self, host: NancyMCPHost, batch_size: int = 10):
        self.host = host
        self.batch_size = batch_size
        
    async def process_batch(self, file_requests: List[Dict[str, Any]]) -> List[str]:
        """Process multiple files in batches"""
        packet_ids = []
        
        # Process in batches to avoid overwhelming the system
        for i in range(0, len(file_requests), self.batch_size):
            batch = file_requests[i:i + self.batch_size]
            
            # Submit batch for processing
            batch_tasks = [
                self.host.ingest_content(
                    request["server_name"],
                    request["file_path"], 
                    request["metadata"]
                )
                for request in batch
            ]
            
            # Wait for batch completion
            batch_packet_ids = await asyncio.gather(*batch_tasks)
            packet_ids.extend(batch_packet_ids)
            
            # Optional: Add delay between batches
            await asyncio.sleep(1)
            
        return packet_ids
```

### 5.3 Priority Processing

```python
class PriorityQueue:
    """Priority queue for processing high-importance content first"""
    
    def __init__(self):
        self.high_priority = asyncio.Queue()
        self.normal_priority = asyncio.Queue()
        self.low_priority = asyncio.Queue()
        
    async def enqueue(self, packet: NancyKnowledgePacket, priority: str = "normal"):
        """Add packet to appropriate priority queue"""
        if priority == "high":
            await self.high_priority.put(packet)
        elif priority == "low":
            await self.low_priority.put(packet)
        else:
            await self.normal_priority.put(packet)
            
    async def dequeue(self) -> NancyKnowledgePacket:
        """Get next packet based on priority"""
        # Check high priority first
        if not self.high_priority.empty():
            return await self.high_priority.get()
        
        # Then normal priority
        if not self.normal_priority.empty():
            return await self.normal_priority.get()
            
        # Finally low priority
        return await self.low_priority.get()
```

---

## 6. Authentication and Security

### 6.1 MCP Security Architecture

```python
import jwt
import bcrypt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class MCPSecurityManager:
    """Manages authentication and authorization for MCP connections"""
    
    def __init__(self, config: SecurityConfig):
        self.auth_enabled = config.authentication.enabled
        self.auth_method = config.authentication.method
        self.api_key_header = config.authentication.api_key_header
        self.jwt_secret = config.jwt_secret
        self.valid_api_keys: Dict[str, Dict[str, Any]] = {}
        
    async def authenticate_request(self, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Authenticate incoming request"""
        if not self.auth_enabled:
            return {"authenticated": True, "user": "anonymous"}
            
        if self.auth_method == "api_key":
            return await self.authenticate_api_key(headers)
        elif self.auth_method == "jwt":
            return await self.authenticate_jwt(headers)
        else:
            raise ValueError(f"Unsupported auth method: {self.auth_method}")
            
    async def authenticate_api_key(self, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Authenticate using API key"""
        api_key = headers.get(self.api_key_header)
        if not api_key:
            return None
            
        # Validate API key
        user_info = self.valid_api_keys.get(api_key)
        if user_info:
            return {
                "authenticated": True,
                "user": user_info["user"],
                "permissions": user_info.get("permissions", [])
            }
        return None
        
    async def authenticate_jwt(self, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Authenticate using JWT token"""
        auth_header = headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return {
                "authenticated": True,
                "user": payload.get("user"),
                "permissions": payload.get("permissions", [])
            }
        except jwt.InvalidTokenError:
            return None
            
    def generate_api_key(self, user: str, permissions: List[str]) -> str:
        """Generate new API key for user"""
        import secrets
        api_key = secrets.token_urlsafe(32)
        
        self.valid_api_keys[api_key] = {
            "user": user,
            "permissions": permissions,
            "created_at": datetime.now().isoformat()
        }
        
        return api_key
        
    def generate_jwt_token(self, user: str, permissions: List[str], 
                          expires_hours: int = 24) -> str:
        """Generate JWT token for user"""
        payload = {
            "user": user,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=expires_hours),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
```

### 6.2 File Security and Sandboxing

```python
import os
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class FileSecurity:
    """Handles file security validation and sandboxing"""
    
    def __init__(self, config: MCPSecurityConfig):
        self.sandbox_enabled = config.sandbox_mode
        self.allowed_extensions = config.allowed_file_extensions
        self.max_file_size = config.max_file_size_mb * 1024 * 1024
        self.quarantine_dir = Path("./quarantine")
        self.quarantine_dir.mkdir(exist_ok=True)
        
    async def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive file validation"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "quarantined": False
        }
        
        # Check file existence
        if not os.path.exists(file_path):
            validation_result["valid"] = False
            validation_result["errors"].append("File does not exist")
            return validation_result
            
        # Check file extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.allowed_extensions:
            validation_result["valid"] = False
            validation_result["errors"].append(f"File extension not allowed: {file_ext}")
            
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            validation_result["valid"] = False
            validation_result["errors"].append(f"File too large: {file_size} bytes")
            
        # Virus scanning if enabled
        if self.sandbox_enabled:
            scan_result = await self.scan_for_threats(file_path)
            if scan_result["threats_found"]:
                validation_result["valid"] = False
                validation_result["errors"].extend(scan_result["threats"])
                validation_result["quarantined"] = True
                await self.quarantine_file(file_path)
                
        return validation_result
        
    async def scan_for_threats(self, file_path: str) -> Dict[str, Any]:
        """Scan file for security threats"""
        scan_result = {
            "threats_found": False,
            "threats": [],
            "scan_engine": "clamav"  # Example: could use ClamAV
        }
        
        try:
            # Example using ClamAV (would need to be installed)
            result = subprocess.run([
                "clamscan", "--no-summary", file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                scan_result["threats_found"] = True
                scan_result["threats"].append("Virus or malware detected")
                
        except FileNotFoundError:
            # ClamAV not installed, use basic heuristics
            scan_result = await self.basic_threat_detection(file_path)
        except subprocess.TimeoutExpired:
            scan_result["threats"].append("Scan timeout - file may be suspicious")
            
        return scan_result
        
    async def basic_threat_detection(self, file_path: str) -> Dict[str, Any]:
        """Basic threat detection without external tools"""
        scan_result = {
            "threats_found": False,
            "threats": [],
            "scan_engine": "basic_heuristics"
        }
        
        # Check for suspicious file patterns
        with open(file_path, 'rb') as f:
            file_header = f.read(1024)  # Read first 1KB
            
        # Basic heuristics for common threats
        suspicious_patterns = [
            b'javascript:',  # JavaScript execution
            b'vbscript:',    # VBScript execution
            b'data:',        # Data URLs
            b'<script',      # HTML script tags
        ]
        
        for pattern in suspicious_patterns:
            if pattern in file_header.lower():
                scan_result["threats_found"] = True
                scan_result["threats"].append(f"Suspicious pattern detected: {pattern.decode('utf-8', errors='ignore')}")
                
        return scan_result
        
    async def quarantine_file(self, file_path: str):
        """Move suspicious file to quarantine"""
        import shutil
        import uuid
        
        quarantine_name = f"{uuid.uuid4()}_{Path(file_path).name}"
        quarantine_path = self.quarantine_dir / quarantine_name
        
        shutil.move(file_path, quarantine_path)
        
        # Log quarantine action
        with open(self.quarantine_dir / "quarantine.log", "a") as log_file:
            log_file.write(f"{datetime.now().isoformat()}: Quarantined {file_path} as {quarantine_name}\n")
```

---

## 7. Error Handling and Retry Logic

### 7.1 Comprehensive Error Handling

```python
import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class MCPError:
    error_type: str
    message: str
    severity: ErrorSeverity
    server_name: Optional[str] = None
    packet_id: Optional[str] = None
    timestamp: str = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class MCPErrorHandler:
    """Handles errors and implements retry logic for MCP operations"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.error_log: List[MCPError] = []
        self.logger = logging.getLogger(__name__)
        
    async def execute_with_retry(self, 
                                operation: Callable,
                                *args,
                                error_context: Dict[str, Any] = None,
                                **kwargs) -> Any:
        """Execute operation with exponential backoff retry"""
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await operation(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Classify error
                error = self.classify_error(e, error_context)
                error.retry_count = attempt
                self.error_log.append(error)
                
                # Log error
                self.logger.warning(f"Attempt {attempt + 1} failed: {error.message}")
                
                # Check if we should retry
                if attempt >= self.max_retries or not self.is_retryable_error(error):
                    break
                    
                # Calculate delay with exponential backoff
                delay = self.base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
                
        # All retries exhausted
        final_error = self.classify_error(last_exception, error_context)
        final_error.retry_count = self.max_retries
        self.error_log.append(final_error)
        
        self.logger.error(f"Operation failed after {self.max_retries} retries: {final_error.message}")
        raise last_exception
        
    def classify_error(self, exception: Exception, 
                      context: Dict[str, Any] = None) -> MCPError:
        """Classify exception into MCPError with appropriate severity"""
        
        context = context or {}
        
        if isinstance(exception, ConnectionError):
            return MCPError(
                error_type="connection_error",
                message=f"Connection failed: {str(exception)}",
                severity=ErrorSeverity.HIGH,
                server_name=context.get("server_name")
            )
        elif isinstance(exception, TimeoutError):
            return MCPError(
                error_type="timeout_error",
                message=f"Operation timed out: {str(exception)}",
                severity=ErrorSeverity.MEDIUM,
                server_name=context.get("server_name")
            )
        elif isinstance(exception, FileNotFoundError):
            return MCPError(
                error_type="file_not_found",
                message=f"File not found: {str(exception)}",
                severity=ErrorSeverity.MEDIUM,
                packet_id=context.get("packet_id")
            )
        elif isinstance(exception, PermissionError):
            return MCPError(
                error_type="permission_error",
                message=f"Permission denied: {str(exception)}",
                severity=ErrorSeverity.HIGH,
                server_name=context.get("server_name")
            )
        else:
            return MCPError(
                error_type="unknown_error",
                message=f"Unknown error: {str(exception)}",
                severity=ErrorSeverity.MEDIUM,
                server_name=context.get("server_name"),
                packet_id=context.get("packet_id")
            )
            
    def is_retryable_error(self, error: MCPError) -> bool:
        """Determine if error is retryable"""
        non_retryable_types = [
            "file_not_found",
            "permission_error", 
            "validation_error",
            "authentication_error"
        ]
        
        return error.error_type not in non_retryable_types and error.severity != ErrorSeverity.CRITICAL
        
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get statistics about errors encountered"""
        if not self.error_log:
            return {"total_errors": 0}
            
        error_counts = {}
        severity_counts = {}
        
        for error in self.error_log:
            error_counts[error.error_type] = error_counts.get(error.error_type, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
            
        return {
            "total_errors": len(self.error_log),
            "error_types": error_counts,
            "severity_breakdown": severity_counts,
            "recent_errors": [
                {
                    "type": error.error_type,
                    "message": error.message,
                    "severity": error.severity.value,
                    "timestamp": error.timestamp
                }
                for error in self.error_log[-10:]  # Last 10 errors
            ]
        }
```

### 7.2 Dead Letter Queue Implementation

```python
class DeadLetterQueue:
    """Handles packets that couldn't be processed after retries"""
    
    def __init__(self, storage_path: str = "./dead_letter_queue"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    async def enqueue_failed_packet(self, packet: NancyKnowledgePacket, 
                                   error: MCPError):
        """Add failed packet to dead letter queue"""
        
        dlq_entry = {
            "packet_id": packet.packet_id,
            "packet": packet.to_dict(),
            "error": {
                "type": error.error_type,
                "message": error.message,
                "severity": error.severity.value,
                "retry_count": error.retry_count,
                "timestamp": error.timestamp
            },
            "enqueued_at": datetime.now().isoformat()
        }
        
        # Store in file
        dlq_file = self.storage_path / f"dlq_{packet.packet_id}.json"
        async with aiofiles.open(dlq_file, 'w') as f:
            await f.write(json.dumps(dlq_entry, indent=2))
            
        self.logger.error(f"Packet {packet.packet_id} added to dead letter queue: {error.message}")
        
    async def get_failed_packets(self) -> List[Dict[str, Any]]:
        """Get all packets in dead letter queue"""
        failed_packets = []
        
        for dlq_file in self.storage_path.glob("dlq_*.json"):
            async with aiofiles.open(dlq_file, 'r') as f:
                content = await f.read()
                failed_packets.append(json.loads(content))
                
        return failed_packets
        
    async def retry_failed_packet(self, packet_id: str, 
                                 host: 'NancyMCPHost') -> bool:
        """Attempt to retry a failed packet"""
        
        dlq_file = self.storage_path / f"dlq_{packet_id}.json"
        if not dlq_file.exists():
            return False
            
        # Load packet from dead letter queue
        async with aiofiles.open(dlq_file, 'r') as f:
            dlq_entry = json.loads(await f.read())
            
        packet = NancyKnowledgePacket.from_dict(dlq_entry["packet"])
        
        try:
            # Attempt to reprocess
            await host.process_knowledge_packet(packet)
            
            # Remove from dead letter queue on success
            dlq_file.unlink()
            self.logger.info(f"Successfully reprocessed packet {packet_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Retry failed for packet {packet_id}: {e}")
            return False
```

---

## 8. Performance and Monitoring

### 8.1 Performance Metrics Collection

```python
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any
from collections import defaultdict, deque

@dataclass
class PerformanceMetrics:
    """Performance metrics for MCP operations"""
    
    # Processing metrics
    packets_processed: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    
    # Server metrics
    server_response_times: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    server_error_rates: Dict[str, int] = field(default_factory=dict)
    
    # Brain metrics
    brain_storage_times: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    brain_query_times: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    
    # Throughput metrics
    packets_per_second: deque = field(default_factory=lambda: deque(maxlen=100))
    
class PerformanceMonitor:
    """Monitors and collects performance metrics for Nancy MCP operations"""
    
    def __init__(self, window_size: int = 1000):
        self.metrics = PerformanceMetrics()
        self.window_size = window_size
        self.operation_timings: deque = deque(maxlen=window_size)
        
    def start_operation(self, operation_id: str) -> str:
        """Start timing an operation"""
        start_time = time.time()
        self.active_operations[operation_id] = start_time
        return operation_id
        
    def end_operation(self, operation_id: str, 
                     operation_type: str = "packet_processing",
                     server_name: str = None):
        """End timing an operation and record metrics"""
        
        if operation_id not in self.active_operations:
            return
            
        start_time = self.active_operations.pop(operation_id)
        duration = time.time() - start_time
        
        # Record general metrics
        self.operation_timings.append(duration)
        self.metrics.packets_processed += 1
        self.metrics.total_processing_time += duration
        self.metrics.average_processing_time = (
            self.metrics.total_processing_time / self.metrics.packets_processed
        )
        
        # Record server-specific metrics
        if server_name:
            self.metrics.server_response_times[server_name].append(duration)
            
        # Record throughput
        current_time = time.time()
        self.metrics.packets_per_second.append(current_time)
        
    def record_error(self, server_name: str):
        """Record an error for a specific server"""
        self.metrics.server_error_rates[server_name] = (
            self.metrics.server_error_rates.get(server_name, 0) + 1
        )
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        
        # Calculate current throughput
        now = time.time()
        recent_packets = [t for t in self.metrics.packets_per_second if now - t <= 60]
        current_throughput = len(recent_packets) / 60.0  # packets per second
        
        # Calculate percentiles for response times
        all_times = list(self.operation_timings)
        all_times.sort()
        
        def percentile(data, p):
            if not data:
                return 0
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = k - f
            if f + 1 < len(data):
                return data[f] * (1 - c) + data[f + 1] * c
            return data[f]
            
        summary = {
            "overview": {
                "total_packets_processed": self.metrics.packets_processed,
                "average_processing_time": self.metrics.average_processing_time,
                "current_throughput": current_throughput,
                "total_uptime": time.time() - self.start_time if hasattr(self, 'start_time') else 0
            },
            "response_times": {
                "p50": percentile(all_times, 50),
                "p95": percentile(all_times, 95),
                "p99": percentile(all_times, 99),
                "max": max(all_times) if all_times else 0
            },
            "server_performance": {
                server: {
                    "avg_response_time": sum(times) / len(times) if times else 0,
                    "total_requests": len(times),
                    "error_count": self.metrics.server_error_rates.get(server, 0)
                }
                for server, times in self.metrics.server_response_times.items()
            },
            "brain_performance": {
                "storage_times": {
                    brain: sum(times) / len(times) if times else 0
                    for brain, times in self.metrics.brain_storage_times.items()
                },
                "query_times": {
                    brain: sum(times) / len(times) if times else 0
                    for brain, times in self.metrics.brain_query_times.items()
                }
            }
        }
        
        return summary
```

### 8.2 Health Monitoring

```python
class HealthMonitor:
    """Monitors health of Nancy MCP system components"""
    
    def __init__(self, host: NancyMCPHost):
        self.host = host
        self.health_history: deque = deque(maxlen=100)
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% error rate
            "response_time": 5.0,  # 5 second response time
            "memory_usage": 0.8,  # 80% memory usage
            "disk_usage": 0.9   # 90% disk usage
        }
        
    async def check_system_health(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {},
            "alerts": []
        }
        
        # Check Nancy Core
        health_report["components"]["nancy_core"] = await self.check_nancy_core()
        
        # Check each MCP server
        for server_name in self.host.sessions.keys():
            health_report["components"][server_name] = await self.check_mcp_server(server_name)
            
        # Check Four-Brain architecture
        brain_health = await self.check_brain_health()
        health_report["components"]["brains"] = brain_health
        
        # Check system resources
        resource_health = await self.check_system_resources()
        health_report["components"]["system_resources"] = resource_health
        
        # Determine overall status
        component_statuses = [
            comp["status"] for comp in health_report["components"].values()
        ]
        
        if "critical" in component_statuses:
            health_report["overall_status"] = "critical"
        elif "degraded" in component_statuses:
            health_report["overall_status"] = "degraded"
        elif "unhealthy" in component_statuses:
            health_report["overall_status"] = "unhealthy"
            
        # Generate alerts
        health_report["alerts"] = await self.generate_alerts(health_report)
        
        # Store in history
        self.health_history.append(health_report)
        
        return health_report
        
    async def check_nancy_core(self) -> Dict[str, Any]:
        """Check Nancy Core health"""
        try:
            # Check orchestrator
            orchestrator_health = await self.host.orchestrator.health_check()
            
            # Check packet queue
            queue_size = self.host.packet_queue.qsize()
            
            # Check active processing tasks
            active_tasks = len([t for t in self.host.processing_tasks.values() if not t.done()])
            
            status = "healthy"
            if queue_size > 100:
                status = "degraded"
            if queue_size > 500:
                status = "unhealthy"
                
            return {
                "status": status,
                "orchestrator": orchestrator_health,
                "packet_queue_size": queue_size,
                "active_processing_tasks": active_tasks
            }
            
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e)
            }
            
    async def check_mcp_server(self, server_name: str) -> Dict[str, Any]:
        """Check individual MCP server health"""
        try:
            session = self.host.sessions.get(server_name)
            if not session:
                return {"status": "critical", "error": "No session available"}
                
            # Call health check tool
            result = await session.call_tool("health_check", {})
            health_data = json.loads(result.content[0].text)
            
            return {
                "status": "healthy",
                "server_health": health_data
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
            
    async def check_brain_health(self) -> Dict[str, Any]:
        """Check Four-Brain architecture health"""
        brain_health = {}
        overall_status = "healthy"
        
        # Check each brain
        for brain_name in ["vector", "analytical", "graph", "linguistic"]:
            try:
                brain = getattr(self.host.orchestrator, f"{brain_name}_brain")
                health = await brain.health_check()
                brain_health[brain_name] = health
                
                if health.get("status") != "healthy":
                    overall_status = "degraded"
                    
            except Exception as e:
                brain_health[brain_name] = {
                    "status": "critical",
                    "error": str(e)
                }
                overall_status = "critical"
                
        return {
            "status": overall_status,
            "brains": brain_health
        }
        
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        import psutil
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent / 100
        
        # Disk usage
        disk = psutil.disk_usage('.')
        disk_percent = disk.percent / 100
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1) / 100
        
        status = "healthy"
        if memory_percent > self.alert_thresholds["memory_usage"]:
            status = "degraded"
        if disk_percent > self.alert_thresholds["disk_usage"]:
            status = "unhealthy"
            
        return {
            "status": status,
            "memory": {
                "used_percent": memory_percent,
                "available_gb": memory.available / (1024**3)
            },
            "disk": {
                "used_percent": disk_percent,
                "free_gb": disk.free / (1024**3)
            },
            "cpu": {
                "used_percent": cpu_percent
            }
        }
        
    async def generate_alerts(self, health_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on health check results"""
        alerts = []
        
        # Check for critical components
        for component_name, component_health in health_report["components"].items():
            if component_health["status"] == "critical":
                alerts.append({
                    "level": "critical",
                    "component": component_name,
                    "message": f"{component_name} is in critical state",
                    "details": component_health.get("error", "")
                })
                
        # Check system resources
        resources = health_report["components"].get("system_resources", {})
        if resources.get("memory", {}).get("used_percent", 0) > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "level": "warning",
                "component": "system_resources",
                "message": "High memory usage detected",
                "details": f"Memory usage: {resources['memory']['used_percent']:.1%}"
            })
            
        return alerts
```

---

## 9. Development Guidelines

### 9.1 MCP Server Development Standards

```python
# Template for new Nancy MCP servers
from nancy.mcp.base_server import NancyMCPServer
from nancy.schemas.knowledge_packet import NancyKnowledgePacket

class ExampleMCPServer(NancyMCPServer):
    """
    Example MCP Server Implementation
    
    Follows Nancy MCP development standards:
    1. Inherit from NancyMCPServer
    2. Implement all abstract methods
    3. Follow naming conventions
    4. Include comprehensive error handling
    5. Support health checking
    6. Include logging and metrics
    """
    
    def __init__(self):
        super().__init__("nancy-example-server", "1.0.0")
        self.logger = logging.getLogger(__name__)
        
    def get_server_name(self) -> str:
        return "nancy-example-server"
        
    def get_version(self) -> str:
        return "1.0.0"
        
    def get_capabilities(self) -> List[str]:
        return ["file_upload", "batch_processing"]
        
    def get_supported_file_types(self) -> List[str]:
        return [".example", ".test"]
        
    async def validate_source(self, source_path: str) -> bool:
        """Validate source with comprehensive checking"""
        try:
            # Check file existence
            if not os.path.exists(source_path):
                self.logger.warning(f"File not found: {source_path}")
                return False
                
            # Check file extension
            file_ext = Path(source_path).suffix.lower()
            if file_ext not in self.get_supported_file_types():
                self.logger.warning(f"Unsupported file type: {file_ext}")
                return False
                
            # Add custom validation logic here
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error for {source_path}: {e}")
            return False
            
    async def ingest_content(self, source_path: str, 
                           metadata: Dict[str, Any]) -> NancyKnowledgePacket:
        """Ingest content with comprehensive error handling"""
        try:
            self.logger.info(f"Starting ingestion: {source_path}")
            
            # Validate source
            if not await self.validate_source(source_path):
                raise ValueError(f"Invalid source: {source_path}")
                
            # Extract content (implement specific logic)
            extracted_data = await self.extract_content(source_path)
            
            # Create knowledge packet
            packet = await self.create_knowledge_packet(
                source_path, extracted_data, metadata
            )
            
            self.logger.info(f"Ingestion completed: {packet.packet_id}")
            return packet
            
        except Exception as e:
            self.logger.error(f"Ingestion failed for {source_path}: {e}")
            raise
            
    async def extract_content(self, source_path: str) -> Dict[str, Any]:
        """Extract content from source (implement in subclass)"""
        # Implement specific extraction logic
        pass
        
    async def create_knowledge_packet(self, source_path: str, 
                                    extracted_data: Dict[str, Any],
                                    metadata: Dict[str, Any]) -> NancyKnowledgePacket:
        """Create standardized knowledge packet"""
        # Implement packet creation logic
        pass
        
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        return {
            "status": "healthy",
            "server_name": self.server_name,
            "version": self.version,
            "supported_types": self.get_supported_file_types(),
            "capabilities": self.get_capabilities(),
            "uptime": self.get_uptime(),
            "processed_files": self.get_processed_count(),
            "timestamp": datetime.now().isoformat()
        }
```

### 9.2 Code Quality Standards

```python
# Example of comprehensive docstring standards
class DocumentationExample:
    """
    Example class showing Nancy MCP documentation standards.
    
    This class demonstrates the expected documentation format for Nancy MCP
    components, including type hints, comprehensive docstrings, and examples.
    
    Attributes:
        config: Configuration object for the component
        logger: Logger instance for the component
        metrics: Performance metrics collector
        
    Example:
        ```python
        component = DocumentationExample(config)
        result = await component.process_data(data)
        ```
    """
    
    def __init__(self, config: ComponentConfig):
        """
        Initialize the component.
        
        Args:
            config: Configuration object containing component settings
            
        Raises:
            ValueError: If config is invalid
            ConnectionError: If unable to establish required connections
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def process_data(self, data: Dict[str, Any], 
                          options: Optional[ProcessingOptions] = None) -> ProcessingResult:
        """
        Process data according to configuration.
        
        This method processes input data and returns structured results.
        It handles various data types and applies configured transformations.
        
        Args:
            data: Input data to process. Must contain 'content' key.
            options: Optional processing options. If None, uses defaults.
            
        Returns:
            ProcessingResult containing:
                - success: Boolean indicating processing success
                - result: Processed data if successful
                - error: Error message if unsuccessful
                - metrics: Processing performance metrics
                
        Raises:
            ValueError: If data format is invalid
            ProcessingError: If processing fails due to business logic
            TimeoutError: If processing exceeds configured timeout
            
        Example:
            ```python
            data = {"content": "example text", "type": "document"}
            options = ProcessingOptions(timeout=30)
            result = await component.process_data(data, options)
            
            if result.success:
                print(f"Processed: {result.result}")
            else:
                print(f"Error: {result.error}")
            ```
        """
        try:
            # Implementation with comprehensive error handling
            pass
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            raise
```

### 9.3 Testing Standards

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from nancy.mcp.servers.document import DocumentMCPServer
from nancy.schemas.knowledge_packet import NancyKnowledgePacket

class TestDocumentMCPServer:
    """
    Comprehensive test suite for Document MCP Server.
    
    Tests follow Nancy MCP testing standards:
    1. Test all public methods
    2. Test error conditions
    3. Test edge cases
    4. Include integration tests
    5. Mock external dependencies
    """
    
    @pytest.fixture
    async def server(self):
        """Create test server instance"""
        return DocumentMCPServer()
        
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create sample test file"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Sample content for testing")
        return str(test_file)
        
    async def test_validate_source_valid_file(self, server, sample_file):
        """Test source validation with valid file"""
        result = await server.validate_source(sample_file)
        assert result is True
        
    async def test_validate_source_missing_file(self, server):
        """Test source validation with missing file"""
        result = await server.validate_source("/nonexistent/file.txt")
        assert result is False
        
    async def test_validate_source_unsupported_type(self, server, tmp_path):
        """Test source validation with unsupported file type"""
        unsupported_file = tmp_path / "test.xyz"
        unsupported_file.write_text("content")
        
        result = await server.validate_source(str(unsupported_file))
        assert result is False
        
    async def test_ingest_content_success(self, server, sample_file):
        """Test successful content ingestion"""
        metadata = {"author": "Test User", "project": "Test Project"}
        
        packet = await server.ingest_content(sample_file, metadata)
        
        assert isinstance(packet, NancyKnowledgePacket)
        assert packet.packet_id is not None
        assert packet.metadata["author"] == "Test User"
        assert packet.content.vector_data is not None
        
    async def test_ingest_content_invalid_file(self, server):
        """Test ingestion with invalid file"""
        metadata = {"author": "Test User"}
        
        with pytest.raises(ValueError):
            await server.ingest_content("/nonexistent/file.txt", metadata)
            
    async def test_health_check(self, server):
        """Test health check functionality"""
        health = await server.health_check()
        
        assert health["status"] == "healthy"
        assert health["server_name"] == "nancy-document-server"
        assert "version" in health
        assert "capabilities" in health
        
    @pytest.mark.integration
    async def test_full_ingestion_workflow(self, server, tmp_path):
        """Integration test for complete ingestion workflow"""
        # Create test file
        test_file = tmp_path / "integration_test.md"
        test_content = """
        # Test Document
        
        This is a test document for integration testing.
        It contains multiple paragraphs and sections.
        
        ## Section 1
        Content for section 1.
        
        ## Section 2  
        Content for section 2.
        """
        test_file.write_text(test_content)
        
        # Perform ingestion
        metadata = {
            "author": "Integration Test",
            "project": "Test Suite",
            "tags": ["test", "integration"]
        }
        
        packet = await server.ingest_content(str(test_file), metadata)
        
        # Validate packet structure
        assert packet.packet_version == "1.0"
        assert packet.source.mcp_server == "nancy-document-server"
        assert packet.metadata.author == "Integration Test"
        assert len(packet.content.vector_data.chunks) > 0
        assert packet.content.analytical_data.structured_fields["word_count"] > 0
        assert packet.quality_metrics.extraction_confidence > 0.8

    @pytest.mark.performance  
    async def test_large_file_processing(self, server, tmp_path):
        """Performance test for large file processing"""
        # Create large test file
        large_file = tmp_path / "large_test.txt"
        large_content = "This is test content. " * 10000  # ~200KB
        large_file.write_text(large_content)
        
        # Measure processing time
        start_time = asyncio.get_event_loop().time()
        
        packet = await server.ingest_content(str(large_file), {})
        
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        
        # Verify performance requirements
        assert processing_time < 10.0  # Should process within 10 seconds
        assert packet is not None
        assert len(packet.content.vector_data.chunks) > 10  # Should be chunked
        
    async def test_concurrent_processing(self, server, tmp_path):
        """Test concurrent file processing"""
        # Create multiple test files
        test_files = []
        for i in range(5):
            test_file = tmp_path / f"concurrent_test_{i}.txt"
            test_file.write_text(f"Content for file {i}")
            test_files.append(str(test_file))
            
        # Process files concurrently
        tasks = [
            server.ingest_content(file_path, {"file_index": i})
            for i, file_path in enumerate(test_files)
        ]
        
        packets = await asyncio.gather(*tasks)
        
        # Validate all packets
        assert len(packets) == 5
        for i, packet in enumerate(packets):
            assert packet.metadata.file_index == i
            assert packet.packet_id is not None
```

---

## 10. Testing and Validation

### 10.1 Comprehensive Test Strategy

```python
import pytest
import asyncio
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch

class MCPIntegrationTestSuite:
    """
    Comprehensive test suite for Nancy MCP integration.
    
    Tests the entire MCP ecosystem including:
    - Nancy Core MCP Host functionality
    - MCP Server implementations  
    - End-to-end data flow
    - Error handling and recovery
    - Performance under load
    """
    
    @pytest.fixture
    async def nancy_host(self, test_config):
        """Create Nancy MCP Host for testing"""
        host = NancyMCPHost(test_config)
        await host.start()
        yield host
        await host.stop()
        
    @pytest.fixture
    def mock_mcp_server(self):
        """Create mock MCP server for testing"""
        server = Mock()
        server.ingest_content = AsyncMock()
        server.health_check = AsyncMock(return_value={"status": "healthy"})
        return server
        
    async def test_mcp_host_startup(self, nancy_host):
        """Test Nancy MCP Host startup process"""
        assert len(nancy_host.clients) > 0
        assert len(nancy_host.sessions) > 0
        
        # Verify all configured servers are started
        for server_config in nancy_host.config.mcp_servers.enabled_servers:
            assert server_config.name in nancy_host.sessions
            
    async def test_knowledge_packet_flow(self, nancy_host, sample_document):
        """Test end-to-end knowledge packet flow"""
        
        # Submit content for ingestion
        packet_id = await nancy_host.ingest_content(
            "nancy-document-server",
            sample_document,
            {"author": "Test User"}
        )
        
        # Wait for processing to complete
        await asyncio.sleep(1)  # Allow processing time
        
        # Verify packet was processed
        assert packet_id is not None
        
        # Verify content was stored in brains
        vector_results = await nancy_host.orchestrator.vector_brain.query(
            ["test content"], 1
        )
        assert len(vector_results["documents"][0]) > 0
        
    async def test_multi_server_coordination(self, nancy_host, test_files):
        """Test coordination between multiple MCP servers"""
        
        # Submit files to different servers
        tasks = []
        for file_path, server_name in test_files:
            task = nancy_host.ingest_content(server_name, file_path, {})
            tasks.append(task)
            
        # Wait for all to complete
        packet_ids = await asyncio.gather(*tasks)
        
        # Verify all packets were processed
        assert len(packet_ids) == len(test_files)
        assert all(pid is not None for pid in packet_ids)
        
    async def test_error_recovery(self, nancy_host):
        """Test error handling and recovery mechanisms"""
        
        # Test with invalid file
        with pytest.raises(Exception):
            await nancy_host.ingest_content(
                "nancy-document-server",
                "/nonexistent/file.txt",
                {}
            )
            
        # Verify system is still functional
        health = await nancy_host.check_system_health()
        assert health["overall_status"] in ["healthy", "degraded"]
        
    @pytest.mark.performance
    async def test_throughput_performance(self, nancy_host, large_dataset):
        """Test system throughput with large dataset"""
        
        start_time = asyncio.get_event_loop().time()
        
        # Process large number of files
        batch_size = 50
        for i in range(0, len(large_dataset), batch_size):
            batch = large_dataset[i:i + batch_size]
            tasks = [
                nancy_host.ingest_content(
                    file_info["server"],
                    file_info["path"],
                    file_info["metadata"]
                )
                for file_info in batch
            ]
            await asyncio.gather(*tasks)
            
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        throughput = len(large_dataset) / total_time
        
        # Verify performance requirements
        assert throughput > 5.0  # Should process at least 5 files per second
        
    async def test_concurrent_query_processing(self, nancy_host):
        """Test concurrent query processing while ingesting"""
        
        # Start ingestion tasks
        ingestion_tasks = [
            nancy_host.ingest_content(
                "nancy-document-server",
                f"/path/to/file_{i}.txt",
                {"index": i}
            )
            for i in range(10)
        ]
        
        # Start query tasks concurrently
        query_tasks = [
            nancy_host.orchestrator.query(f"test query {i}")
            for i in range(5)
        ]
        
        # Wait for all to complete
        ingestion_results = await asyncio.gather(*ingestion_tasks, return_exceptions=True)
        query_results = await asyncio.gather(*query_tasks, return_exceptions=True)
        
        # Verify no deadlocks or failures
        assert not any(isinstance(r, Exception) for r in query_results)
```

### 10.2 Validation Framework

```python
class NancyMCPValidator:
    """
    Validation framework for Nancy MCP components.
    
    Provides comprehensive validation for:
    - Configuration correctness
    - Knowledge packet schema compliance
    - MCP server implementation standards
    - Performance requirements
    """
    
    def __init__(self):
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
        
    async def validate_configuration(self, config: NancyCoreConfig) -> bool:
        """Validate Nancy Core configuration"""
        
        # Reset validation state
        self.validation_errors.clear()
        self.validation_warnings.clear()
        
        # Validate basic structure
        if not config.nancy_core:
            self.validation_errors.append("Missing nancy_core configuration")
            
        if not config.brains:
            self.validation_errors.append("Missing brains configuration")
            
        # Validate brain configurations
        await self._validate_brain_configs(config.brains)
        
        # Validate MCP server configurations
        await self._validate_mcp_server_configs(config.mcp_servers)
        
        # Validate security configuration
        if config.security:
            await self._validate_security_config(config.security)
            
        return len(self.validation_errors) == 0
        
    async def _validate_brain_configs(self, brains: Dict[str, Any]):
        """Validate brain configurations"""
        
        required_brains = ["vector", "analytical", "graph", "linguistic"]
        
        for brain_name in required_brains:
            if brain_name not in brains:
                self.validation_errors.append(f"Missing {brain_name} brain configuration")
                continue
                
            brain_config = brains[brain_name]
            
            # Validate backend selection
            if "backend" not in brain_config:
                self.validation_errors.append(f"{brain_name} brain missing backend specification")
                
            # Validate connection configuration
            if "connection" not in brain_config:
                self.validation_errors.append(f"{brain_name} brain missing connection configuration")
                
    async def _validate_mcp_server_configs(self, mcp_servers: Dict[str, Any]):
        """Validate MCP server configurations"""
        
        if "enabled_servers" not in mcp_servers:
            self.validation_errors.append("Missing enabled_servers in mcp_servers configuration")
            return
            
        for server_config in mcp_servers["enabled_servers"]:
            # Validate required fields
            if "name" not in server_config:
                self.validation_errors.append("MCP server missing name")
                
            if "executable" not in server_config:
                self.validation_errors.append("MCP server missing executable")
                
            # Validate name format
            if "name" in server_config and not server_config["name"].startswith("nancy-"):
                self.validation_warnings.append(f"MCP server name should start with 'nancy-': {server_config['name']}")
                
    async def validate_knowledge_packet(self, packet: NancyKnowledgePacket) -> bool:
        """Validate knowledge packet against schema"""
        
        validation_errors = []
        
        # Validate required fields
        required_fields = ["packet_version", "packet_id", "timestamp", "source", "metadata", "content"]
        
        for field in required_fields:
            if not hasattr(packet, field) or getattr(packet, field) is None:
                validation_errors.append(f"Missing required field: {field}")
                
        # Validate packet_id format (should be SHA256 hash)
        if hasattr(packet, "packet_id") and packet.packet_id:
            if len(packet.packet_id) != 64 or not all(c in "0123456789abcdef" for c in packet.packet_id):
                validation_errors.append("Invalid packet_id format (should be SHA256 hash)")
                
        # Validate content structure
        if hasattr(packet, "content") and packet.content:
            if not any([
                packet.content.vector_data,
                packet.content.analytical_data,
                packet.content.graph_data
            ]):
                validation_errors.append("Packet content must include at least one data type")
                
        self.validation_errors.extend(validation_errors)
        return len(validation_errors) == 0
        
    async def validate_mcp_server_implementation(self, server_class: type) -> bool:
        """Validate MCP server implementation against standards"""
        
        validation_errors = []
        
        # Check inheritance
        if not issubclass(server_class, NancyMCPServer):
            validation_errors.append("Server must inherit from NancyMCPServer")
            
        # Check required methods
        required_methods = [
            "get_server_name", "get_version", "get_capabilities",
            "get_supported_file_types", "validate_source", 
            "ingest_content", "health_check"
        ]
        
        for method_name in required_methods:
            if not hasattr(server_class, method_name):
                validation_errors.append(f"Missing required method: {method_name}")
                
        # Check method signatures
        import inspect
        
        if hasattr(server_class, "ingest_content"):
            sig = inspect.signature(server_class.ingest_content)
            if len(sig.parameters) < 3:  # self, source_path, metadata
                validation_errors.append("ingest_content method has incorrect signature")
                
        self.validation_errors.extend(validation_errors)
        return len(validation_errors) == 0
        
    def get_validation_report(self) -> Dict[str, Any]:
        """Get comprehensive validation report"""
        return {
            "validation_passed": len(self.validation_errors) == 0,
            "error_count": len(self.validation_errors),
            "warning_count": len(self.validation_warnings),
            "errors": self.validation_errors,
            "warnings": self.validation_warnings,
            "timestamp": datetime.now().isoformat()
        }
```

---

## Conclusion

This MCP Integration Specification provides a comprehensive framework for transforming Nancy from a monolithic system to a configurable MCP orchestration platform. The specification covers all aspects of integration including:

- **Host Implementation**: Nancy Core as sophisticated MCP host
- **Server Standards**: Standardized interfaces for MCP servers
- **Communication Patterns**: Synchronous, asynchronous, and streaming patterns
- **Security Framework**: Authentication, authorization, and sandboxing
- **Error Handling**: Comprehensive retry logic and dead letter queues
- **Performance Monitoring**: Metrics collection and health monitoring
- **Development Guidelines**: Standards for consistent implementation
- **Testing Framework**: Comprehensive validation and testing strategies

The specification ensures that Nancy maintains its Four-Brain intelligence advantages while gaining enterprise-grade configurability and extensibility through the MCP ecosystem. This positions Nancy as a composable intelligence platform suitable for diverse enterprise deployments while preserving its core analytical capabilities.

Next steps involve implementing the initial MCP host framework and creating the first production MCP servers following these specifications.