#!/usr/bin/env python3
"""
Nancy Spreadsheet MCP Server
Provides comprehensive spreadsheet processing capabilities for Nancy's Four-Brain architecture.
Generates standardized Nancy Knowledge Packets for seamless integration.
"""

import asyncio
import json
import sys
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add parent directory to path to import processor
sys.path.append(str(Path(__file__).parent))
from processor import SpreadsheetProcessor

# MCP protocol imports (simplified for standalone operation)
class MCPRequest:
    """Represents an MCP request."""
    def __init__(self, data: Dict[str, Any]):
        self.jsonrpc = data.get("jsonrpc", "2.0")
        self.id = data.get("id")
        self.method = data.get("method")
        self.params = data.get("params", {})

class MCPResponse:
    """Represents an MCP response."""
    def __init__(self, request_id: Any, result: Any = None, error: Any = None):
        self.jsonrpc = "2.0"
        self.id = request_id
        self.result = result
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        response = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        if self.error:
            response["error"] = self.error
        else:
            response["result"] = self.result
        return response


class NancyKnowledgePacket:
    """Nancy Knowledge Packet for standardized data submission."""
    
    @classmethod
    def create_from_spreadsheet_data(cls, 
                                   filename: str,
                                   processed_data: Dict[str, Any],
                                   server_version: str = "1.0.0",
                                   author: str = None,
                                   creation_timestamp: str = None) -> Dict[str, Any]:
        """
        Create a Nancy Knowledge Packet from processed spreadsheet data with enhanced temporal support.
        
        Args:
            filename: Original filename
            processed_data: Output from SpreadsheetProcessor
            server_version: Version of this MCP server
            author: Document author (for temporal tracking)
            creation_timestamp: Original document creation timestamp
            
        Returns:
            Dictionary representing a valid Nancy Knowledge Packet with temporal metadata
        """
        # Generate packet ID from content
        content_str = json.dumps(processed_data.get("content", {}), sort_keys=True)
        packet_id = hashlib.sha256(content_str.encode()).hexdigest()
        
        # Extract temporal information from filename if available
        temporal_info = cls._extract_temporal_info_from_filename(filename)
        
        # Build the Knowledge Packet with enhanced temporal metadata
        packet = {
            "packet_version": "1.1",  # Updated for temporal support
            "packet_id": packet_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": {
                "mcp_server": "nancy-spreadsheet-server",
                "server_version": server_version,
                "original_location": filename,
                "content_type": "spreadsheet",
                "extraction_method": "pandas_openpyxl"
            },
            "metadata": {
                "title": Path(filename).stem,
                "author": author or processed_data.get("author", "Unknown"),
                "file_size": 0,  # Will be updated by caller
                "created_at": creation_timestamp or datetime.utcnow().isoformat() + "Z",
                "processed_at": datetime.utcnow().isoformat() + "Z"
            },
            "temporal_metadata": {
                "document_era": temporal_info.get("era"),
                "time_period": temporal_info.get("time_period"),
                "sequence_indicators": temporal_info.get("sequence_indicators", []),
                "version_info": temporal_info.get("version_info"),
                "temporal_keywords": temporal_info.get("temporal_keywords", [])
            },
            "content": processed_data.get("content", {}),
            "processing_hints": processed_data.get("processing_hints", {
                "priority_brain": "analytical",
                "semantic_weight": 0.7,
                "relationship_importance": 0.8,
                "content_classification": "technical",
                "temporal_importance": 0.6  # New: temporal relationship weight
            }),
            "quality_metrics": processed_data.get("quality_metrics", {
                "extraction_confidence": 0.95,
                "content_completeness": 1.0
            })
        }
        
        # Add spreadsheet-specific metadata
        if "sheets_processed" in processed_data:
            packet["metadata"].update({
                "spreadsheet_type": processed_data.get("file_type", "unknown"),
                "sheets_count": len(processed_data["sheets_processed"]),
                "total_rows": processed_data.get("total_rows", 0),
                "total_columns": processed_data.get("total_columns", 0),
                "sheet_names": processed_data["sheets_processed"]
            })
        
        return packet
    
    @classmethod
    def _extract_temporal_info_from_filename(cls, filename: str) -> Dict[str, Any]:
        """
        Extract temporal information from filename patterns.
        Enhanced for Phase 2 temporal brain support.
        """
        import re
        
        temporal_info = {
            "era": None,
            "time_period": None,
            "sequence_indicators": [],
            "version_info": None,
            "temporal_keywords": []
        }
        
        filename_lower = filename.lower()
        
        # Era detection patterns
        era_patterns = {
            "requirements": ["req", "requirement", "spec", "specification"],
            "design": ["design", "arch", "architecture", "blueprint"],
            "implementation": ["impl", "implementation", "dev", "development"],
            "testing": ["test", "qa", "validation", "verification"],
            "release": ["release", "deploy", "production", "final"]
        }
        
        for era, keywords in era_patterns.items():
            if any(keyword in filename_lower for keyword in keywords):
                temporal_info["era"] = era
                temporal_info["temporal_keywords"].extend([kw for kw in keywords if kw in filename_lower])
                break
        
        # Time period extraction (dates, quarters, versions)
        # Date patterns: YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD
        date_patterns = [
            r'(\d{4}[-_]?\d{2}[-_]?\d{2})',  # Date formats
            r'(q[1-4][-_]?\d{4})',          # Quarter formats
            r'(\d{4}[-_]?q[1-4])',          # Year-Quarter formats
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[-_]?\d{4}',  # Month-Year
            r'(\d{4}[-_]?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec))'  # Year-Month
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename_lower)
            if match:
                temporal_info["time_period"] = match.group(1)
                temporal_info["temporal_keywords"].append(match.group(1))
                break
        
        # Version detection
        version_patterns = [
            r'v(\d+\.?\d*\.?\d*)',  # v1.0, v2.1.3
            r'version[-_]?(\d+\.?\d*\.?\d*)',  # version1.0
            r'rev[-_]?(\d+)',       # rev1, rev_2
            r'draft[-_]?(\d+)',     # draft1, draft_2
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, filename_lower)
            if match:
                temporal_info["version_info"] = match.group(1)
                temporal_info["temporal_keywords"].append(f"version_{match.group(1)}")
                break
        
        # Sequence indicators
        sequence_patterns = [
            r'(part[-_]?\d+)',      # part1, part_2
            r'(step[-_]?\d+)',      # step1, step_2  
            r'(phase[-_]?\d+)',     # phase1, phase_2
            r'(stage[-_]?\d+)',     # stage1, stage_2
            r'(\d+[-_]?of[-_]?\d+)', # 1of3, 2_of_5
        ]
        
        for pattern in sequence_patterns:
            matches = re.findall(pattern, filename_lower)
            if matches:
                temporal_info["sequence_indicators"].extend(matches)
                temporal_info["temporal_keywords"].extend(matches)
        
        # Additional temporal keywords
        temporal_keywords = [
            "initial", "final", "preliminary", "draft", "revised", "updated",
            "baseline", "milestone", "checkpoint", "review", "approved",
            "current", "latest", "old", "new", "before", "after",
            "pre", "post", "interim", "temporary", "permanent"
        ]
        
        for keyword in temporal_keywords:
            if keyword in filename_lower:
                temporal_info["temporal_keywords"].append(keyword)
        
        # Clean up duplicates
        temporal_info["temporal_keywords"] = list(set(temporal_info["temporal_keywords"]))
        temporal_info["sequence_indicators"] = list(set(temporal_info["sequence_indicators"]))
        
        return temporal_info


class SpreadsheetMCPServer:
    """
    Nancy Spreadsheet MCP Server
    Provides comprehensive spreadsheet processing with Knowledge Packet generation.
    """
    
    def __init__(self):
        self.server_version = "1.0.0"
        self.processor = SpreadsheetProcessor()
        self.logger = self._setup_logging()
        self.capabilities = [
            "nancy/ingest",
            "nancy/health_check",
            "nancy/capabilities"
        ]
        self.is_running = False
        self.start_time = None
        self.requests_processed = 0
        self.requests_failed = 0
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the MCP server."""
        logger = logging.getLogger("nancy-spreadsheet-server")
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = Path(__file__).parent / "server.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    async def start(self):
        """Start the MCP server."""
        self.is_running = True
        self.start_time = datetime.utcnow()
        self.logger.info(f"Nancy Spreadsheet MCP Server v{self.server_version} starting...")
        
        # Send initialization to Nancy Core
        init_response = {
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {
                "server_info": {
                    "name": "nancy-spreadsheet-server",
                    "version": self.server_version
                },
                "capabilities": {
                    "experimental": {},
                    "nancy": {
                        "ingest": {
                            "supported_types": [".xlsx", ".xls", ".csv"],
                            "capabilities": [
                                "multi_sheet_processing",
                                "engineering_domain_intelligence",
                                "column_relationship_analysis",
                                "semantic_summary_generation"
                            ]
                        }
                    }
                }
            }
        }
        
        print(json.dumps(init_response))
        self.logger.info("Server initialization complete")
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        try:
            request = MCPRequest(request_data)
            self.logger.debug(f"Received request: {request.method}")
            
            if request.method == "nancy/ingest":
                return await self._handle_ingest(request)
            elif request.method == "nancy/health_check":
                return await self._handle_health_check(request)
            elif request.method == "nancy/capabilities":
                return await self._handle_capabilities(request)
            else:
                error = {
                    "code": -32601,
                    "message": f"Method not found: {request.method}"
                }
                return MCPResponse(request.id, error=error).to_dict()
        
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            self.requests_failed += 1
            error = {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
            return MCPResponse(request_data.get("id"), error=error).to_dict()
    
    async def _handle_ingest(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle spreadsheet ingestion requests."""
        try:
            params = request.params
            file_path = params.get("file_path")
            metadata = params.get("metadata", {})
            
            if not file_path:
                error = {
                    "code": -32602,
                    "message": "Missing required parameter: file_path"
                }
                return MCPResponse(request.id, error=error).to_dict()
            
            # Read file content
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                file_size = len(content)
            except FileNotFoundError:
                error = {
                    "code": -32603,
                    "message": f"File not found: {file_path}"
                }
                return MCPResponse(request.id, error=error).to_dict()
            except Exception as e:
                error = {
                    "code": -32603,
                    "message": f"Error reading file: {str(e)}"
                }
                return MCPResponse(request.id, error=error).to_dict()
            
            # Extract filename and author
            filename = Path(file_path).name
            author = metadata.get("author", "Unknown")
            
            self.logger.info(f"Processing spreadsheet: {filename} ({file_size} bytes)")
            
            # Process spreadsheet
            processed_data = self.processor.process_spreadsheet(filename, content, author)
            
            if "error" in processed_data:
                self.logger.error(f"Processing failed: {processed_data['error']}")
                error = {
                    "code": -32603,
                    "message": f"Spreadsheet processing failed: {processed_data['error']}"
                }
                return MCPResponse(request.id, error=error).to_dict()
            
            # Create Knowledge Packet
            knowledge_packet = NancyKnowledgePacket.create_from_spreadsheet_data(
                filename, processed_data, self.server_version
            )
            
            # Update metadata with file size
            knowledge_packet["metadata"]["file_size"] = file_size
            knowledge_packet["metadata"].update(metadata)
            
            self.logger.info(f"Successfully processed {filename}: {len(processed_data.get('sheets_processed', []))} sheets")
            self.requests_processed += 1
            
            result = {
                "status": "success",
                "knowledge_packet": knowledge_packet,
                "processing_summary": {
                    "sheets_processed": processed_data.get("sheets_processed", []),
                    "total_rows": processed_data.get("total_rows", 0),
                    "total_columns": processed_data.get("total_columns", 0),
                    "file_size": file_size
                }
            }
            
            return MCPResponse(request.id, result=result).to_dict()
        
        except Exception as e:
            self.logger.error(f"Error in ingest handler: {e}")
            import traceback
            traceback.print_exc()
            
            error = {
                "code": -32603,
                "message": f"Ingestion error: {str(e)}"
            }
            return MCPResponse(request.id, error=error).to_dict()
    
    async def _handle_health_check(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle health check requests."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
        
        result = {
            "status": "healthy",
            "server_info": {
                "name": "nancy-spreadsheet-server",
                "version": self.server_version,
                "uptime_seconds": uptime,
                "requests_processed": self.requests_processed,
                "requests_failed": self.requests_failed,
                "success_rate": (
                    self.requests_processed / (self.requests_processed + self.requests_failed)
                    if (self.requests_processed + self.requests_failed) > 0 else 1.0
                )
            },
            "capabilities": {
                "supported_extensions": self.processor.supported_extensions,
                "features": [
                    "multi_sheet_excel_processing",
                    "csv_processing",
                    "engineering_domain_intelligence",
                    "column_relationship_analysis",
                    "semantic_summary_generation",
                    "knowledge_packet_generation"
                ]
            }
        }
        
        return MCPResponse(request.id, result=result).to_dict()
    
    async def _handle_capabilities(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle capabilities inquiry."""
        result = {
            "capabilities": {
                "experimental": {},
                "nancy": {
                    "ingest": {
                        "supported_types": self.processor.supported_extensions,
                        "features": [
                            "multi_sheet_processing",
                            "engineering_domain_intelligence", 
                            "column_relationship_analysis",
                            "semantic_summary_generation"
                        ]
                    },
                    "health_check": True
                }
            }
        }
        
        return MCPResponse(request.id, result=result).to_dict()
    
    async def run(self):
        """Main server loop."""
        await self.start()
        
        try:
            # Read from stdin and process requests
            while self.is_running:
                try:
                    # Read line from stdin
                    line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                    
                    if not line:
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse JSON request
                    try:
                        request_data = json.loads(line)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON: {e}")
                        continue
                    
                    # Handle request
                    response = await self.handle_request(request_data)
                    
                    # Send response
                    print(json.dumps(response))
                    sys.stdout.flush()
                
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}")
                    break
        
        except KeyboardInterrupt:
            self.logger.info("Server shutdown requested")
        
        finally:
            self.is_running = False
            self.logger.info("Nancy Spreadsheet MCP Server stopped")


async def main():
    """Entry point for the MCP server."""
    server = SpreadsheetMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())