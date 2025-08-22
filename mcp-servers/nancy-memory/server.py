#!/usr/bin/env python3
"""
Nancy Memory MCP Server

Provides "infinite memory" capabilities for other LLMs through MCP protocol.
Exposes Nancy's Four-Brain architecture as standardized MCP tools and resources.

Strategic Position: Nancy as persistent project intelligence for other AI assistants.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Optional, Any

# Add the parent directory to the path to import Nancy core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp.server.fastmcp import FastMCP
import requests
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nancy-memory-mcp")

# Nancy API configuration
NANCY_API_BASE = os.getenv("NANCY_API_BASE", "http://localhost:8000")

class NancyMemoryMCP:
    """Nancy Memory MCP Server - Infinite Memory for LLMs"""
    
    def __init__(self, nancy_api_base: str = NANCY_API_BASE):
        self.nancy_api_base = nancy_api_base
        self.mcp = FastMCP("Nancy Memory Server")
        self._setup_tools()
        self._setup_resources()
        
    def _setup_tools(self):
        """Setup MCP tools for Nancy's capabilities"""
        
        @self.mcp.tool()
        def ingest_information(
            content: str,
            content_type: str = "text",
            author: str = "AI Assistant",
            filename: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """
            Store information in Nancy's persistent memory.
            
            Use this tool when you want to remember:
            - Important decisions made during conversations
            - Key insights or analysis results  
            - User preferences or project context
            - Technical specifications or requirements
            - Meeting outcomes or action items
            
            Args:
                content: The information to store (text, code, data)
                content_type: Type of content (text, code, decision, requirement, etc.)
                author: Who created this information (defaults to "AI Assistant")
                filename: Optional filename if this represents a document
                metadata: Additional context (project_id, tags, priority, etc.)
            
            Returns:
                Status of the ingestion operation
            """
            try:
                # Debug input parameters
                logger.info(f"MCP Server: ingest_information called with:")
                logger.info(f"  content: {content[:100]}...")
                logger.info(f"  content_type: {content_type}")
                logger.info(f"  author: {author}")
                logger.info(f"  filename: {filename}")
                logger.info(f"  metadata: {metadata}")
                logger.info(f"  metadata type: {type(metadata)}")
                
                # Handle metadata parameter - MCP protocol may pass it as JSON string
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                        logger.info(f"MCP Server: Parsed metadata string to dict: {metadata}")
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"MCP Server: Failed to parse metadata string '{metadata}': {e}")
                        metadata = {}
                elif metadata is None:
                    metadata = {}
                elif not isinstance(metadata, dict):
                    logger.warning(f"MCP Server: Unexpected metadata type {type(metadata)}, using empty dict")
                    metadata = {}
                
                # Check Nancy's current mode to determine ingestion strategy
                health_response = requests.get(f"{self.nancy_api_base}/health", timeout=10)
                nancy_mode = "unknown"
                
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    nancy_mode = health_data.get("nancy_core", {}).get("migration_mode", "unknown")
                
                if nancy_mode == "mcp":
                    # Use Knowledge Packet ingestion for MCP mode
                    import hashlib
                    import json
                    from datetime import datetime
                    
                    # Create proper knowledge packet matching schema
                    filename_final = filename or f"memory_{content_type}_{len(content)}.txt"
                    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                    
                    # Build content for different brains
                    packet_content = {
                        "vector_data": {
                            "chunks": [{
                                "chunk_id": f"{filename_final}_chunk_0",
                                "text": content,
                                "chunk_metadata": {
                                    "chunk_index": 0,
                                    "source_file": filename_final
                                }
                            }],
                            "embedding_model": "BAAI/bge-small-en-v1.5",
                            "chunk_strategy": "document_structure",
                            "chunk_size": len(content),
                            "chunk_overlap": 0
                        }
                    }
                    
                    packet_data = {
                        "packet_version": "1.0",
                        "packet_id": content_hash,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "source": {
                            "mcp_server": "nancy-memory",
                            "server_version": "1.0.0",
                            "original_location": filename_final,
                            "content_type": "document",
                            "extraction_method": "mcp_direct_ingestion"
                        },
                        "metadata": {
                            "title": filename_final,
                            "author": author,
                            "created_at": datetime.utcnow().isoformat() + "Z",
                            "content_hash": content_hash,
                            "file_size": len(content.encode('utf-8')),
                            "tags": [content_type, "mcp_ingested"],
                            "classification": "internal",
                            "language": "en",
                            **(metadata or {})
                        },
                        "content": packet_content,
                        "processing_hints": {
                            "priority_brain": "vector",
                            "semantic_weight": 0.8,
                            "relationship_importance": 0.6,
                            "requires_expert_routing": False,
                            "content_classification": "technical",
                            "indexing_priority": "medium"
                        },
                        "quality_metrics": {
                            "extraction_confidence": 1.0,
                            "content_completeness": 1.0,
                            "text_quality_score": 0.9,
                            "metadata_richness": 0.8,
                            "processing_errors": []
                        }
                    }
                    
                    # Debug logging - let's see what we're actually sending
                    logger.info(f"MCP Server: About to send packet with ID: {packet_data['packet_id']}")
                    logger.info(f"MCP Server: Packet keys: {list(packet_data.keys())}")
                    logger.info(f"MCP Server: packet_version field: {packet_data.get('packet_version', 'MISSING!')}")
                    logger.info(f"MCP Server: Full packet JSON: {json.dumps(packet_data, indent=2)}")
                    
                    # Validate packet locally before sending
                    try:
                        import sys
                        import os
                        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'nancy-services'))
                        from schemas.knowledge_packet import KnowledgePacketValidator
                        
                        validator = KnowledgePacketValidator()
                        validator.validate(packet_data)
                        logger.info("MCP Server: Local packet validation PASSED")
                    except Exception as e:
                        logger.error(f"MCP Server: Local packet validation FAILED: {e}")
                        return {
                            "status": "error",
                            "message": f"Local packet validation failed: {e}",
                            "details": "Packet failed validation before sending to Nancy"
                        }
                    
                    response = requests.post(
                        f"{self.nancy_api_base}/api/ingest/knowledge-packet",
                        json=packet_data,
                        timeout=30
                    )
                else:
                    # Use legacy file ingestion for legacy/hybrid modes
                    import tempfile
                    import io
                    
                    # Create temporary file for legacy ingestion
                    filename_final = filename or f"memory_{content_type}_{len(content)}.txt"
                    
                    # Use multipart form data for legacy endpoint
                    files = {
                        'file': (filename_final, io.BytesIO(content.encode('utf-8')), 'text/plain')
                    }
                    data = {
                        'author': author
                    }
                    
                    response = requests.post(
                        f"{self.nancy_api_base}/api/ingest",
                        files=files,
                        data=data,
                        timeout=30
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully stored information: {content[:100]}...")
                    
                    # Handle different response formats
                    doc_id = result.get("packet_id") or result.get("doc_id")
                    ingestion_mode = "Knowledge Packet" if nancy_mode == "mcp" else "Legacy File"
                    
                    return {
                        "status": "success",
                        "message": f"Information stored in Nancy's persistent memory via {ingestion_mode} ingestion",
                        "doc_id": doc_id,
                        "nancy_mode": nancy_mode,
                        "details": f"Stored {len(content)} characters as {content_type}"
                    }
                else:
                    logger.error(f"Nancy ingestion failed: {response.status_code} {response.text}")
                    return {
                        "status": "error",
                        "message": f"Failed to store information: {response.text}",
                        "details": "Nancy ingestion endpoint returned an error"
                    }
                    
            except Exception as e:
                logger.error(f"Ingestion error: {e}")
                return {
                    "status": "error", 
                    "message": f"Failed to store information: {str(e)}",
                    "details": "Connection or processing error"
                }
        
        @self.mcp.tool()
        def query_memory(
            question: str,
            n_results: int = 5,
            search_strategy: str = "intelligent"
        ) -> Dict[str, Any]:
            """
            Query Nancy's persistent memory for relevant information.
            
            Use this tool to:
            - Find previous decisions or discussions about a topic
            - Retrieve technical specifications or requirements
            - Look up who worked on specific components
            - Get context about project history or evolution
            - Find related documents or code
            
            Args:
                question: What you want to know or find
                n_results: Maximum number of results to return (default: 5)
                search_strategy: How to search ("intelligent", "enhanced", "langchain")
            
            Returns:
                Relevant information from Nancy's memory with sources
            """
            try:
                # Query Nancy's intelligent query endpoint
                query_data = {
                    "query": question,
                    "n_results": n_results,
                    "orchestrator": search_strategy
                }
                
                response = requests.post(
                    f"{self.nancy_api_base}/api/query",
                    json=query_data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                    except ValueError as e:
                        logger.error(f"Failed to parse Nancy response as JSON: {e}")
                        return {
                            "status": "error",
                            "message": f"Nancy API returned invalid JSON: {response.text[:200]}...",
                            "question": question
                        }
                    
                    logger.info(f"Successfully queried memory: {question[:100]}...")
                    logger.debug(f"Raw Nancy response keys: {list(result.keys())}")
                    
                    # Validate response has basic structure
                    if not isinstance(result, dict):
                        logger.error(f"Nancy response is not a dictionary: {type(result)}")
                        return {
                            "status": "error",
                            "message": f"Nancy API returned unexpected data type: {type(result)}",
                            "question": question
                        }
                    
                    # Adaptive orchestrator detection and field mapping
                    try:
                        orchestrator_type = self._detect_orchestrator_type(result)
                        logger.info(f"Detected orchestrator type: {orchestrator_type}")
                    except Exception as e:
                        logger.error(f"Failed to detect orchestrator type: {e}")
                        orchestrator_type = "unknown"
                    
                    # Extract response data using appropriate field mapping with error handling
                    try:
                        extracted_data = self._extract_response_data(result, orchestrator_type)
                    except Exception as e:
                        logger.error(f"Failed to extract response data: {e}")
                        # Emergency fallback to return something useful
                        return {
                            "status": "partial_success",
                            "question": question,
                            "orchestrator_detected": orchestrator_type,
                            "response": str(result) if result else "No response data could be extracted",
                            "error_details": f"Data extraction failed: {str(e)}",
                            "raw_response_keys": list(result.keys()) if isinstance(result, dict) else "N/A"
                        }
                    
                    # Validate extracted data before returning
                    if not extracted_data.get("response"):
                        logger.warning("Extracted response is empty, using fallback")
                        extracted_data["response"] = f"Query processed by {orchestrator_type} orchestrator but no response content available"
                    
                    # Format the response for MCP client consumption
                    return {
                        "status": "success",
                        "question": question,
                        "orchestrator_detected": orchestrator_type,
                        "response": extracted_data["response"],
                        "strategy_used": extracted_data["strategy_used"],
                        "sources": extracted_data["sources"],
                        "brain_analysis": extracted_data["brain_analysis"],
                        "confidence": extracted_data["confidence"],
                        "brains_used": extracted_data["brains_used"],
                        "processing_timestamp": extracted_data["processing_timestamp"]
                    }
                else:
                    logger.error(f"Nancy query failed: {response.status_code} {response.text}")
                    return {
                        "status": "error",
                        "message": f"Failed to query memory: {response.text}",
                        "question": question
                    }
                    
            except Exception as e:
                logger.error(f"Query error: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to query memory: {str(e)}",
                    "question": question
                }
        
        @self.mcp.tool()
        def find_author_contributions(
            author_name: str,
            contribution_type: str = "all"
        ) -> Dict[str, Any]:
            """
            Find what a specific person contributed to the project.
            
            Use this tool to:
            - Identify who wrote specific code or documents
            - Find subject matter experts for different domains
            - Track contributions across team members
            - Understand code ownership and responsibility
            
            Args:
                author_name: Name of the person to search for
                contribution_type: Type of contributions ("all", "code", "documents", "decisions")
            
            Returns:
                List of contributions by this author with details
            """
            try:
                # Use Nancy's graph query endpoint for author attribution
                query_data = {
                    "author_name": author_name,
                    "use_enhanced": True
                }
                
                response = requests.post(
                    f"{self.nancy_api_base}/api/query/graph",
                    json=query_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Found contributions for: {author_name}")
                    
                    return {
                        "status": "success",
                        "author": author_name,
                        "contributions": result.get("authored_documents", []),
                        "expertise_areas": result.get("expertise_domains", []),
                        "collaboration_patterns": result.get("collaborations", []),
                        "contribution_count": len(result.get("authored_documents", []))
                    }
                else:
                    logger.error(f"Author query failed: {response.status_code} {response.text}")
                    return {
                        "status": "error",
                        "message": f"Failed to find author contributions: {response.text}",
                        "author": author_name
                    }
                    
            except Exception as e:
                logger.error(f"Author query error: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to find author contributions: {str(e)}",
                    "author": author_name
                }
        
        @self.mcp.tool()
        def get_project_overview(
            focus_area: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get a comprehensive overview of the project's current state.
            
            Use this tool to:
            - Understand the overall project context
            - Get metrics and statistics about stored information
            - Identify key areas of activity or concern
            - Provide context for new team members
            
            Args:
                focus_area: Optional area to focus on ("technical", "people", "decisions", "recent")
            
            Returns:
                Project overview with metrics and key information
            """
            try:
                # Get Nancy's status and metrics
                response = requests.get(
                    f"{self.nancy_api_base}/api/nancy/status",
                    timeout=30
                )
                
                if response.status_code == 200:
                    status = response.json()
                    logger.info("Retrieved project overview")
                    
                    # Get additional metrics from ingestion status
                    ingest_response = requests.get(
                        f"{self.nancy_api_base}/api/ingest/status",
                        timeout=30
                    )
                    
                    ingest_status = {}
                    if ingest_response.status_code == 200:
                        ingest_status = ingest_response.json()
                    
                    return {
                        "status": "success",
                        "project_health": status.get("status", {}),
                        "metrics": status.get("metrics", {}),
                        "system_info": {
                            "nancy_version": "2.0.0",
                            "architecture": "Four-Brain MCP Orchestration",
                            "migration_mode": status.get("migration_mode", "mcp")
                        },
                        "ingestion_metrics": ingest_status.get("metrics", {}),
                        "focus_area": focus_area,
                        "timestamp": status.get("timestamp")
                    }
                else:
                    logger.error(f"Status query failed: {response.status_code}")
                    return {
                        "status": "error",
                        "message": f"Failed to get project overview: {response.text}"
                    }
                    
            except Exception as e:
                logger.error(f"Overview error: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to get project overview: {str(e)}"
                }

    def _detect_orchestrator_type(self, result: Dict[str, Any]) -> str:
        """
        Detect which orchestrator type based on response field structure.
        
        Returns one of: 'intelligent', 'langchain', 'enhanced', 'unknown'
        """
        # Check for intelligent orchestrator fields
        if "synthesized_response" in result and "raw_results" in result and "intent_analysis" in result:
            return "intelligent"
        
        # Check for langchain orchestrator fields
        if "response" in result and "routing_info" in result and "raw_results" not in result:
            return "langchain"
        
        # Check for enhanced orchestrator fields
        if "results" in result and "strategy_used" in result and "synthesized_response" not in result:
            return "enhanced"
        
        # Check for legacy response format
        if "response" in result and "raw_results" in result:
            return "legacy"
        
        # Unknown format
        logger.warning(f"Unknown orchestrator format detected. Available keys: {list(result.keys())}")
        return "unknown"
    
    def _extract_response_data(self, result: Dict[str, Any], orchestrator_type: str) -> Dict[str, Any]:
        """
        Extract standardized response data based on orchestrator type.
        Provides fallback logic for missing fields.
        """
        try:
            if orchestrator_type == "intelligent":
                return self._extract_intelligent_data(result)
            elif orchestrator_type == "langchain":
                return self._extract_langchain_data(result)
            elif orchestrator_type == "enhanced":
                return self._extract_enhanced_data(result)
            elif orchestrator_type == "legacy":
                return self._extract_legacy_data(result)
            else:
                return self._extract_fallback_data(result)
        except Exception as e:
            logger.error(f"Error extracting data for {orchestrator_type}: {e}")
            return self._extract_fallback_data(result)
    
    def _extract_intelligent_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from intelligent orchestrator response."""
        # Convert raw_results to sources format
        sources = []
        for raw_result in result.get("raw_results", []):
            source = {
                "content": raw_result.get("text", ""),
                "metadata": raw_result.get("metadata", {}),
                "relevance_score": 1.0 - raw_result.get("distance", 0.0),
                "source_type": raw_result.get("source", "unknown"),
                "chunk_id": raw_result.get("chunk_id", "")
            }
            sources.append(source)
        
        return {
            "response": result.get("synthesized_response", "No response generated"),
            "strategy_used": result.get("strategy_used", "intelligent"),
            "sources": sources,
            "brain_analysis": result.get("intent_analysis", {}),
            "confidence": result.get("intent_analysis", {}).get("confidence", "unknown"),
            "brains_used": result.get("brains_used", []),
            "processing_timestamp": result.get("processing_timestamp", "")
        }
    
    def _extract_langchain_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from langchain orchestrator response."""
        # LangChain orchestrator has no raw_results field, create empty sources
        sources = []
        
        return {
            "response": result.get("response", "No response generated"),
            "strategy_used": result.get("strategy_used", "langchain_router"),
            "sources": sources,  # LangChain doesn't provide raw source data
            "brain_analysis": result.get("routing_info", {}),
            "confidence": result.get("routing_info", {}).get("confidence", "unknown"),
            "brains_used": [result.get("routing_info", {}).get("selected_brain", "unknown")],
            "processing_timestamp": result.get("processing_timestamp", "")
        }
    
    def _extract_enhanced_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from enhanced orchestrator response."""
        # Convert enhanced results to sources format
        sources = []
        for enhanced_result in result.get("results", []):
            source = {
                "content": enhanced_result.get("content", ""),
                "metadata": enhanced_result.get("metadata", {}),
                "relevance_score": enhanced_result.get("relevance_score", 0.5),
                "source_type": enhanced_result.get("source_type", "unknown"),
                "chunk_id": enhanced_result.get("chunk_id", "")
            }
            sources.append(source)
        
        # Generate a synthesized response if not present
        response = result.get("response", "")
        if not response and sources:
            # Create basic synthesis from sources
            response = f"Found {len(sources)} relevant sources. "
            if sources[0].get("content"):
                response += f"Key content: {sources[0]['content'][:200]}..."
        
        return {
            "response": response or "No response generated",
            "strategy_used": result.get("strategy_used", "enhanced"),
            "sources": sources,
            "brain_analysis": result.get("intent", {}),
            "confidence": result.get("intent", {}).get("confidence", "unknown"),
            "brains_used": result.get("brains_used", ["enhanced"]),
            "processing_timestamp": result.get("processing_timestamp", "")
        }
    
    def _extract_legacy_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from legacy response format."""
        # Handle legacy format with both response and raw_results
        sources = []
        for raw_result in result.get("raw_results", []):
            source = {
                "content": raw_result.get("text", raw_result.get("content", "")),
                "metadata": raw_result.get("metadata", {}),
                "relevance_score": 1.0 - raw_result.get("distance", 0.0),
                "source_type": raw_result.get("source", "unknown"),
                "chunk_id": raw_result.get("chunk_id", "")
            }
            sources.append(source)
        
        return {
            "response": result.get("response", "No response generated"),
            "strategy_used": result.get("strategy_used", "legacy"),
            "sources": sources,
            "brain_analysis": result.get("brain_analysis", {}),
            "confidence": result.get("confidence", "unknown"),
            "brains_used": result.get("brains_used", []),
            "processing_timestamp": result.get("processing_timestamp", "")
        }
    
    def _extract_fallback_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback extraction for unknown/unexpected response formats.
        Attempts to find usable data in any format.
        """
        logger.warning("Using fallback data extraction for unknown response format")
        
        # Try to find a response in various possible fields
        response_candidates = ["synthesized_response", "response", "answer", "result"]
        response = "No response generated"
        for candidate in response_candidates:
            if candidate in result and result[candidate]:
                response = str(result[candidate])
                break
        
        # Try to find sources in various formats
        sources = []
        sources_candidates = ["raw_results", "results", "sources", "documents"]
        for candidate in sources_candidates:
            if candidate in result and isinstance(result[candidate], list):
                for item in result[candidate]:
                    if isinstance(item, dict):
                        source = {
                            "content": item.get("text", item.get("content", item.get("document", ""))),
                            "metadata": item.get("metadata", {}),
                            "relevance_score": 1.0 - item.get("distance", 0.0) if "distance" in item else 0.5,
                            "source_type": item.get("source", item.get("source_type", "unknown")),
                            "chunk_id": item.get("chunk_id", item.get("id", ""))
                        }
                        sources.append(source)
                break
        
        return {
            "response": response,
            "strategy_used": result.get("strategy_used", "fallback"),
            "sources": sources,
            "brain_analysis": result.get("intent_analysis", result.get("routing_info", result.get("intent", {}))),
            "confidence": "unknown",
            "brains_used": result.get("brains_used", ["unknown"]),
            "processing_timestamp": result.get("processing_timestamp", "")
        }

    def _setup_resources(self):
        """Setup MCP resources for Nancy's data"""
        
        @self.mcp.resource("nancy://project/memory")
        def get_project_memory() -> str:
            """
            Access to the complete project memory index.
            
            This resource provides a structured view of all information
            stored in Nancy's persistent memory, organized by type and recency.
            """
            try:
                # Get comprehensive project status
                response = requests.get(
                    f"{self.nancy_api_base}/api/nancy/configuration",
                    timeout=30
                )
                
                if response.status_code == 200:
                    config = response.json()
                    
                    memory_index = {
                        "nancy_configuration": config,
                        "available_capabilities": [
                            "Persistent memory storage across conversations",
                            "Author attribution and expertise tracking", 
                            "Cross-domain technical analysis",
                            "Decision history and provenance",
                            "Code intelligence and relationship mapping"
                        ],
                        "brain_architecture": {
                            "vector_brain": "Semantic search and content similarity",
                            "analytical_brain": "Structured data and metadata queries",
                            "graph_brain": "Relationships and knowledge connections", 
                            "linguistic_brain": "Natural language understanding and synthesis"
                        },
                        "usage_guidance": {
                            "best_for": "Complex engineering projects with multiple contributors",
                            "ideal_queries": "Who worked on X? How does Y relate to Z? What decisions were made about A?",
                            "storage_strategy": "Store important decisions, technical specs, and project context"
                        }
                    }
                    
                    return json.dumps(memory_index, indent=2)
                else:
                    return json.dumps({
                        "error": "Failed to access Nancy configuration",
                        "message": "Nancy may not be running or accessible"
                    }, indent=2)
                    
            except Exception as e:
                return json.dumps({
                    "error": f"Failed to access project memory: {str(e)}",
                    "message": "Check Nancy service availability"
                }, indent=2)

    def run(self):
        """Run the Nancy Memory MCP server"""
        logger.info("Starting Nancy Memory MCP Server...")
        logger.info(f"Nancy API Base: {self.nancy_api_base}")
        
        # Test connection to Nancy
        try:
            response = requests.get(f"{self.nancy_api_base}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✓ Connected to Nancy API successfully")
            else:
                logger.warning(f"⚠ Nancy API returned status {response.status_code}")
        except Exception as e:
            logger.error(f"✗ Failed to connect to Nancy API: {e}")
            logger.error("Make sure Nancy is running with: docker-compose up -d")
        
        self.mcp.run()


def main():
    """Main entry point for the Nancy Memory MCP server"""
    # Allow configuration via environment variables
    nancy_api_base = os.getenv("NANCY_API_BASE", "http://localhost:8000")
    
    server = NancyMemoryMCP(nancy_api_base)
    server.run()


if __name__ == "__main__":
    main()