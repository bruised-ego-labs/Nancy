#!/usr/bin/env python3
"""
Test script for Nancy Core MCP Phase 1 implementation.
Validates the basic MCP architecture functionality and backwards compatibility.
"""

import asyncio
import json
import os
import sys
import tempfile
import logging
from pathlib import Path

# Add nancy-services to path
sys.path.append('./nancy-services')

from core.config_manager import ConfigurationManager, get_config_manager
from core.mcp_host import NancyMCPHost
from core.legacy_adapter import LegacyNancyAdapter, MigrationManager
from schemas.knowledge_packet import NancyKnowledgePacket, KnowledgePacketValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPPhase1Tester:
    """Test suite for Nancy Core MCP Phase 1 implementation."""
    
    def __init__(self):
        self.config_manager = None
        self.config = None
        self.mcp_host = None
        self.adapter = None
        self.test_results = []
    
    async def run_all_tests(self):
        """Run the complete test suite."""
        logger.info("Starting Nancy Core MCP Phase 1 Test Suite")
        
        try:
            await self.test_configuration_management()
            await self.test_knowledge_packet_validation()
            await self.test_mcp_host_initialization()
            await self.test_document_server_integration()
            await self.test_backwards_compatibility()
            await self.test_migration_modes()
            
            # Print test results
            self.print_test_summary()
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def test_configuration_management(self):
        """Test configuration loading and validation."""
        logger.info("Testing configuration management...")
        
        try:
            # Test 1: Load configuration
            self.config_manager = get_config_manager()
            
            # Create default config if it doesn't exist
            if not os.path.exists("nancy-config.yaml"):
                self.config_manager.create_default_config()
            
            self.config = self.config_manager.load_config("nancy-config.yaml")
            
            # Validate configuration structure
            assert self.config.nancy_core.version == "2.0.0"
            assert self.config.orchestration.mode.value == "four_brain"
            assert len(self.config.mcp_servers.enabled_servers) > 0
            
            self.test_results.append(("Configuration Management", "PASS", "Successfully loaded and validated configuration"))
            logger.info("✅ Configuration management test passed")
            
        except Exception as e:
            self.test_results.append(("Configuration Management", "FAIL", str(e)))
            logger.error(f"❌ Configuration management test failed: {e}")
            raise
    
    async def test_knowledge_packet_validation(self):
        """Test Knowledge Packet schema validation."""
        logger.info("Testing Knowledge Packet validation...")
        
        try:
            validator = KnowledgePacketValidator()
            
            # Test 1: Valid Knowledge Packet
            valid_packet_data = {
                "packet_version": "1.0",
                "packet_id": "a" * 64,  # 64-char hex string
                "timestamp": "2025-08-15T10:30:00Z",
                "source": {
                    "mcp_server": "nancy-document-server",
                    "server_version": "1.0.0",
                    "original_location": "/test/file.txt",
                    "content_type": "document"
                },
                "metadata": {
                    "title": "Test Document"
                },
                "content": {
                    "vector_data": {
                        "chunks": [
                            {
                                "chunk_id": "chunk_1",
                                "text": "Test content"
                            }
                        ],
                        "embedding_model": "BAAI/bge-small-en-v1.5",
                        "chunk_strategy": "paragraph_boundary"
                    }
                }
            }
            
            # Validate packet
            validator.validate(valid_packet_data)
            packet = NancyKnowledgePacket(valid_packet_data)
            
            assert packet.packet_id == "a" * 64
            assert packet.has_vector_data()
            assert not packet.has_analytical_data()
            assert not packet.has_graph_data()
            
            # Test 2: Invalid packet (missing required fields)
            invalid_packet_data = {
                "packet_version": "1.0"
                # Missing required fields
            }
            
            try:
                validator.validate(invalid_packet_data)
                assert False, "Should have failed validation"
            except ValueError:
                pass  # Expected
            
            self.test_results.append(("Knowledge Packet Validation", "PASS", "Schema validation working correctly"))
            logger.info("✅ Knowledge Packet validation test passed")
            
        except Exception as e:
            self.test_results.append(("Knowledge Packet Validation", "FAIL", str(e)))
            logger.error(f"❌ Knowledge Packet validation test failed: {e}")
            raise
    
    async def test_mcp_host_initialization(self):
        """Test MCP Host initialization and basic functionality."""
        logger.info("Testing MCP Host initialization...")
        
        try:
            # Initialize MCP Host
            self.mcp_host = NancyMCPHost(self.config)
            
            # Note: We can't fully start the MCP host in test mode without actual MCP servers
            # So we'll test the initialization and configuration
            
            assert self.mcp_host.config == self.config
            assert self.mcp_host.packet_validator is not None
            assert hasattr(self.mcp_host, 'vector_brain')
            assert hasattr(self.mcp_host, 'analytical_brain')
            assert hasattr(self.mcp_host, 'graph_brain')
            
            # Test health check (should work even without started servers)
            health = await self.mcp_host.health_check()
            assert "nancy_mcp_host" in health
            assert "mcp_servers" in health
            
            # Test metrics
            metrics = self.mcp_host.get_metrics()
            assert "packets_processed" in metrics
            assert "uptime_seconds" in metrics
            
            self.test_results.append(("MCP Host Initialization", "PASS", "MCP Host initialized successfully"))
            logger.info("✅ MCP Host initialization test passed")
            
        except Exception as e:
            self.test_results.append(("MCP Host Initialization", "FAIL", str(e)))
            logger.error(f"❌ MCP Host initialization test failed: {e}")
            raise
    
    async def test_document_server_integration(self):
        """Test Document MCP Server integration."""
        logger.info("Testing Document Server integration...")
        
        try:
            # Import and test document server
            sys.path.append('./mcp-servers/document')
            from server import DocumentMCPServer
            
            # Create document server
            doc_server = DocumentMCPServer()
            
            # Test health check
            health = doc_server.health_check()
            assert health["status"] == "healthy"
            assert health["server_name"] == "nancy-document-server"
            
            # Create a test file
            test_content = """# Test Document
This is a test document for Nancy MCP architecture.

## Introduction
This document tests the Knowledge Packet generation from the Document MCP Server.

## Technical Details
The system processes documents through the four-brain architecture:
- Vector brain for semantic search
- Analytical brain for structured data
- Graph brain for relationships
- Linguistic brain for query processing
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(test_content)
                test_file_path = f.name
            
            try:
                # Test file ingestion
                metadata = {
                    "author": "Test User",
                    "title": "Test Document",
                    "tags": ["test", "mcp", "nancy"],
                    "department": "Engineering"
                }
                
                knowledge_packet = doc_server.ingest_file(test_file_path, metadata)
                
                # Validate the generated Knowledge Packet
                validator = KnowledgePacketValidator()
                validator.validate(knowledge_packet)
                
                packet = NancyKnowledgePacket(knowledge_packet)
                
                assert packet.source["mcp_server"] == "nancy-document-server"
                assert packet.metadata["author"] == "Test User"
                assert packet.has_vector_data()
                assert packet.has_analytical_data()
                assert packet.has_graph_data()
                
                # Check vector data structure
                vector_data = packet.content["vector_data"]
                assert len(vector_data["chunks"]) > 0
                assert vector_data["embedding_model"] == "BAAI/bge-small-en-v1.5"
                
                # Check analytical data
                analytical_data = packet.content["analytical_data"]
                assert "structured_fields" in analytical_data
                assert analytical_data["structured_fields"]["word_count"] > 0
                
                # Check graph data
                graph_data = packet.content["graph_data"]
                assert len(graph_data["entities"]) > 0
                assert len(graph_data["relationships"]) > 0
                
                self.test_results.append(("Document Server Integration", "PASS", "Knowledge Packet generated successfully"))
                logger.info("✅ Document Server integration test passed")
                
            finally:
                # Clean up test file
                os.unlink(test_file_path)
            
        except Exception as e:
            self.test_results.append(("Document Server Integration", "FAIL", str(e)))
            logger.error(f"❌ Document Server integration test failed: {e}")
            raise
    
    async def test_backwards_compatibility(self):
        """Test backwards compatibility with legacy API."""
        logger.info("Testing backwards compatibility...")
        
        try:
            # Test Legacy Adapter in different modes
            migration_manager = MigrationManager()
            
            # Test MCP mode (default)
            migration_manager.set_migration_mode("mcp")
            adapter = migration_manager.get_orchestrator()
            
            assert adapter.migration_mode == "mcp"
            assert hasattr(adapter, 'config')
            
            # Test migration readiness check
            readiness = migration_manager.check_migration_readiness()
            assert "current_mode" in readiness
            assert "configuration_valid" in readiness
            
            # Test legacy interface methods exist
            assert hasattr(adapter, 'ingest_file')
            assert hasattr(adapter, 'query')
            assert hasattr(adapter, 'health_check')
            
            # Test health check
            health = adapter.health_check()
            assert "migration_mode" in health
            assert "systems" in health
            
            self.test_results.append(("Backwards Compatibility", "PASS", "Legacy adapter working correctly"))
            logger.info("✅ Backwards compatibility test passed")
            
        except Exception as e:
            self.test_results.append(("Backwards Compatibility", "FAIL", str(e)))
            logger.error(f"❌ Backwards compatibility test failed: {e}")
            raise
    
    async def test_migration_modes(self):
        """Test different migration modes."""
        logger.info("Testing migration modes...")
        
        try:
            migration_manager = MigrationManager()
            
            # Test mode switching
            original_mode = migration_manager.migration_mode
            
            for mode in ["legacy", "hybrid", "mcp"]:
                migration_manager.set_migration_mode(mode)
                assert migration_manager.migration_mode == mode
                
                # Create adapter for each mode
                adapter = migration_manager.get_orchestrator()
                assert adapter.migration_mode == mode
            
            # Restore original mode
            migration_manager.set_migration_mode(original_mode)
            
            # Test invalid mode
            try:
                migration_manager.set_migration_mode("invalid")
                assert False, "Should have failed"
            except ValueError:
                pass  # Expected
            
            self.test_results.append(("Migration Modes", "PASS", "Mode switching working correctly"))
            logger.info("✅ Migration modes test passed")
            
        except Exception as e:
            self.test_results.append(("Migration Modes", "FAIL", str(e)))
            logger.error(f"❌ Migration modes test failed: {e}")
            raise
    
    async def cleanup(self):
        """Clean up test resources."""
        if self.mcp_host:
            try:
                await self.mcp_host.stop()
            except:
                pass
    
    def print_test_summary(self):
        """Print a summary of test results."""
        print("\n" + "="*80)
        print("NANCY CORE MCP PHASE 1 TEST RESULTS")
        print("="*80)
        
        passed = 0
        failed = 0
        
        for test_name, status, message in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌"
            print(f"{status_icon} {test_name:<30} {status:<6} {message}")
            
            if status == "PASS":
                passed += 1
            else:
                failed += 1
        
        print("-"*80)
        print(f"TOTAL: {passed + failed} tests, {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Nancy Core MCP Phase 1 implementation is working correctly.")
        else:
            print(f"⚠️  {failed} test(s) failed. Please review the implementation.")
        
        print("="*80)


async def main():
    """Main test execution."""
    tester = MCPPhase1Tester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())