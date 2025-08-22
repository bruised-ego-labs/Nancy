#!/usr/bin/env python3
"""
Nancy Document MCP Server
A simple MCP server for document ingestion that demonstrates the Nancy MCP architecture.
"""

import asyncio
import json
import logging
import sys
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentMCPServer:
    """
    Simple MCP server for document processing.
    Converts documents to Nancy Knowledge Packets.
    """
    
    def __init__(self):
        self.server_name = "nancy-document-server"
        self.server_version = "1.0.0"
        self.capabilities = ["file_upload"]
        
        # Supported file types
        self.supported_extensions = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.log': 'text/plain',
            '.py': 'text/x-python',
            '.js': 'text/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.json': 'application/json'
        }
    
    async def start(self):
        """Start the MCP server."""
        logger.info(f"Starting {self.server_name} v{self.server_version}")
        
        # Start main event loop
        await self._handle_requests()
    
    async def _handle_requests(self):
        """Handle incoming MCP requests."""
        # For this demo, we'll simulate MCP protocol handling
        # In a real implementation, this would handle JSON-RPC over stdio/transport
        
        logger.info("Document MCP server ready for requests")
        
        # Keep server running
        while True:
            await asyncio.sleep(1)
    
    def ingest_file(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main ingestion method - convert file to Nancy Knowledge Packet.
        
        Args:
            file_path: Path to file to ingest
            metadata: Additional metadata
            
        Returns:
            Nancy Knowledge Packet as dictionary
        """
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_path_obj = Path(file_path)
            file_ext = file_path_obj.suffix.lower()
            
            # Check if file type is supported
            if file_ext not in self.supported_extensions:
                logger.warning(f"Unsupported file type: {file_ext}")
                # Still process as text for demo
                content_type = "document"
            else:
                content_type = "document"
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try binary read for non-text files
                with open(file_path, 'rb') as f:
                    raw_content = f.read()
                    content = f"Binary file ({len(raw_content)} bytes)"
            
            # Generate packet ID
            packet_id = hashlib.sha256(f"{file_path}{content}".encode()).hexdigest()
            
            # Create Knowledge Packet
            knowledge_packet = self._create_knowledge_packet(
                packet_id=packet_id,
                file_path=file_path,
                content=content,
                content_type=content_type,
                metadata=metadata
            )
            
            logger.info(f"Created Knowledge Packet {packet_id} for {file_path}")
            return knowledge_packet
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            raise
    
    def _create_knowledge_packet(self, packet_id: str, file_path: str, 
                                content: str, content_type: str, 
                                metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Nancy Knowledge Packet from file content."""
        
        file_path_obj = Path(file_path)
        file_stats = file_path_obj.stat()
        
        # Extract basic metadata
        title = metadata.get("title", file_path_obj.stem)
        author = metadata.get("author", "Unknown")
        
        # Create vector data by chunking content
        chunks = self._chunk_content(content, file_path)
        
        # Create analytical data
        analytical_data = self._extract_analytical_data(content, file_path_obj)
        
        # Create graph data (basic entity extraction)
        graph_data = self._extract_graph_data(content, title, author)
        
        # Build metadata with optional fields
        packet_metadata = {
            "title": title,
            "author": author,
            "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat() + "Z",
            "modified_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat() + "Z",
            "file_size": file_stats.st_size,
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            "tags": metadata.get("tags", []),
            "language": "en"
        }
        
        # Add optional metadata fields if they exist
        if metadata.get("department"):
            packet_metadata["department"] = metadata["department"]
        if metadata.get("project"):
            packet_metadata["project"] = metadata["project"]
        
        # Create knowledge packet
        packet = {
            "packet_version": "1.0",
            "packet_id": packet_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": {
                "mcp_server": self.server_name,
                "server_version": self.server_version,
                "original_location": str(file_path),
                "content_type": content_type,
                "extraction_method": "text_parser"
            },
            "metadata": packet_metadata,
            "content": {
                "vector_data": {
                    "chunks": chunks,
                    "embedding_model": "BAAI/bge-small-en-v1.5",
                    "chunk_strategy": "semantic_paragraphs",
                    "chunk_size": 512,
                    "chunk_overlap": 50
                },
                "analytical_data": analytical_data,
                "graph_data": graph_data
            },
            "processing_hints": {
                "priority_brain": "vector",
                "semantic_weight": 0.8,
                "relationship_importance": 0.6,
                "requires_expert_routing": False,
                "content_classification": "technical",
                "indexing_priority": "medium"
            },
            "quality_metrics": {
                "extraction_confidence": 0.9,
                "content_completeness": 0.95,
                "relationship_accuracy": 0.8,
                "text_quality_score": 0.95,
                "metadata_richness": 0.7
            }
        }
        
        return packet
    
    def _chunk_content(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Chunk content for vector storage."""
        chunks = []
        
        # Simple paragraph-based chunking
        paragraphs = content.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                chunk = {
                    "chunk_id": f"paragraph_{i}",
                    "text": paragraph.strip(),
                    "chunk_metadata": {
                        "paragraph": i + 1,
                        "file": Path(file_path).name,
                        "chunk_type": "paragraph"
                    }
                }
                chunks.append(chunk)
        
        # If no paragraphs, create single chunk
        if not chunks:
            chunks.append({
                "chunk_id": "full_content",
                "text": content,
                "chunk_metadata": {
                    "file": Path(file_path).name,
                    "chunk_type": "full_document"
                }
            })
        
        return chunks
    
    def _extract_analytical_data(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract analytical data from content."""
        
        # Basic text statistics
        lines = content.split('\n')
        words = content.split()
        
        structured_fields = {
            "word_count": len(words),
            "line_count": len(lines),
            "character_count": len(content),
            "file_extension": file_path.suffix.lower(),
            "estimated_reading_time_minutes": len(words) / 200  # Assume 200 WPM
        }
        
        # Simple table data for file statistics
        table_data = [{
            "table_name": "file_statistics",
            "columns": ["metric", "value"],
            "rows": [
                ["word_count", len(words)],
                ["line_count", len(lines)],
                ["character_count", len(content)]
            ],
            "column_types": ["string", "integer"]
        }]
        
        return {
            "structured_fields": structured_fields,
            "table_data": table_data,
            "statistics": {
                "row_count": len(lines),
                "column_count": 1,
                "null_values": 0,
                "data_quality_score": 0.9
            }
        }
    
    def _extract_graph_data(self, content: str, title: str, author: str) -> Dict[str, Any]:
        """Extract basic graph data from content."""
        
        entities = []
        relationships = []
        
        # Create document entity
        entities.append({
            "type": "Document",
            "name": title,
            "properties": {
                "content_type": "text",
                "extraction_method": "text_parser"
            },
            "confidence": 1.0
        })
        
        # Create author entity if provided
        if author and author != "Unknown":
            entities.append({
                "type": "Person",
                "name": author,
                "properties": {
                    "role": "author"
                },
                "confidence": 0.9
            })
            
            # Create authorship relationship
            relationships.append({
                "source": {"type": "Person", "name": author},
                "relationship": "AUTHORED",
                "target": {"type": "Document", "name": title},
                "properties": {
                    "relationship_type": "authorship"
                },
                "confidence": 0.95
            })
        
        # Simple keyword extraction for technical concepts
        technical_keywords = [
            "algorithm", "system", "architecture", "design", "implementation",
            "performance", "security", "database", "network", "protocol",
            "framework", "library", "api", "interface", "module", "component"
        ]
        
        content_lower = content.lower()
        for keyword in technical_keywords:
            if keyword in content_lower:
                # Create technical concept entity
                concept_name = keyword.title()
                entities.append({
                    "type": "TechnicalConcept",
                    "name": concept_name,
                    "properties": {
                        "category": "technical",
                        "extraction_confidence": 0.7
                    },
                    "confidence": 0.7
                })
                
                # Create relationship with document
                relationships.append({
                    "source": {"type": "Document", "name": title},
                    "relationship": "DISCUSSES",
                    "target": {"type": "TechnicalConcept", "name": concept_name},
                    "properties": {
                        "context": "content_analysis"
                    },
                    "confidence": 0.6
                })
        
        return {
            "entities": entities,
            "relationships": relationships,
            "context": {
                "extraction_method": "keyword_based",
                "document_section": "full_document"
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Return server health status."""
        return {
            "status": "healthy",
            "server_name": self.server_name,
            "server_version": self.server_version,
            "capabilities": self.capabilities,
            "supported_extensions": list(self.supported_extensions.keys()),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


def main():
    """Main entry point for the document MCP server."""
    try:
        # Handle command line arguments for demo purposes
        if len(sys.argv) > 1 and sys.argv[1] == "--demo":
            # Demo mode - process a test file
            server = DocumentMCPServer()
            
            # Create a test file if it doesn't exist
            test_file = "./test_document.txt"
            if not os.path.exists(test_file):
                with open(test_file, 'w') as f:
                    f.write("""# Test Document
This is a test document for the Nancy Document MCP Server.

## Introduction
This document demonstrates the Nancy Knowledge Packet format.
It includes multiple paragraphs and technical concepts.

## Technical Details
The system architecture uses a four-brain approach:
- Vector brain for semantic search
- Analytical brain for structured data
- Graph brain for relationships
- Linguistic brain for query processing

The implementation includes algorithms for performance optimization
and security protocols for data protection.""")
            
            # Process the test file
            metadata = {
                "author": "Test User",
                "title": "Test Document",
                "tags": ["test", "demo", "nancy"],
                "department": "Engineering"
            }
            
            result = server.ingest_file(test_file, metadata)
            
            # Output the Knowledge Packet
            print(json.dumps(result, indent=2))
            
        else:
            # Normal MCP server mode
            server = DocumentMCPServer()
            asyncio.run(server.start())
            
    except KeyboardInterrupt:
        logger.info("Document MCP server stopped")
    except Exception as e:
        logger.error(f"Document MCP server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()