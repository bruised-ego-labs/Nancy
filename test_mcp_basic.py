#!/usr/bin/env python3
"""
Basic test script for Nancy Core MCP Phase 1 implementation.
Tests core components without external dependencies.
"""

import sys
import os
import json
import tempfile
import logging
from datetime import datetime
from pathlib import Path

# Add nancy-services to path
sys.path.append('./nancy-services')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_knowledge_packet_schema():
    """Test Knowledge Packet schema validation."""
    logger.info("Testing Knowledge Packet schema validation...")
    
    try:
        from schemas.knowledge_packet import NancyKnowledgePacket, KnowledgePacketValidator
        
        validator = KnowledgePacketValidator()
        
        # Test valid Knowledge Packet
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
                    "chunk_strategy": "semantic_paragraphs"
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
        assert packet.get_priority_brain() == "vector"
        
        logger.info("✅ Knowledge Packet schema validation test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Knowledge Packet schema validation test failed: {e}")
        return False


def test_configuration_manager():
    """Test configuration management."""
    logger.info("Testing configuration management...")
    
    try:
        from core.config_manager import ConfigurationManager
        
        config_manager = ConfigurationManager()
        
        # Create default config if it doesn't exist
        if not os.path.exists("nancy-config.yaml"):
            config_manager.create_default_config()
        
        # Load configuration
        config = config_manager.load_config("nancy-config.yaml")
        
        # Validate configuration structure
        assert config.nancy_core.version == "2.0.0"
        assert config.orchestration.mode.value == "four_brain"
        assert len(config.mcp_servers.enabled_servers) > 0
        
        # Test brain configurations
        assert config.brains.vector.backend.value == "chromadb"
        assert config.brains.analytical.backend.value == "duckdb"
        assert config.brains.graph.backend.value == "neo4j"
        
        logger.info("✅ Configuration management test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration management test failed: {e}")
        return False


def test_document_server():
    """Test Document MCP Server."""
    logger.info("Testing Document MCP Server...")
    
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
This document tests the Knowledge Packet generation.

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
            from schemas.knowledge_packet import KnowledgePacketValidator
            validator = KnowledgePacketValidator()
            validator.validate(knowledge_packet)
            
            # Check packet structure
            assert knowledge_packet["source"]["mcp_server"] == "nancy-document-server"
            assert knowledge_packet["metadata"]["author"] == "Test User"
            assert "vector_data" in knowledge_packet["content"]
            assert "analytical_data" in knowledge_packet["content"]
            assert "graph_data" in knowledge_packet["content"]
            
            # Check vector data
            vector_data = knowledge_packet["content"]["vector_data"]
            assert len(vector_data["chunks"]) > 0
            assert vector_data["embedding_model"] == "BAAI/bge-small-en-v1.5"
            
            # Check analytical data
            analytical_data = knowledge_packet["content"]["analytical_data"]
            assert "structured_fields" in analytical_data
            assert analytical_data["structured_fields"]["word_count"] > 0
            
            # Check graph data
            graph_data = knowledge_packet["content"]["graph_data"]
            assert len(graph_data["entities"]) > 0
            assert len(graph_data["relationships"]) > 0
            
            logger.info("✅ Document MCP Server test passed")
            return True
            
        finally:
            # Clean up test file
            os.unlink(test_file_path)
            
    except Exception as e:
        logger.error(f"❌ Document MCP Server test failed: {e}")
        return False


def test_migration_manager():
    """Test migration manager."""
    logger.info("Testing migration manager...")
    
    try:
        from core.legacy_adapter import MigrationManager
        
        migration_manager = MigrationManager()
        
        # Test mode switching
        original_mode = migration_manager.migration_mode
        
        for mode in ["legacy", "hybrid", "mcp"]:
            migration_manager.set_migration_mode(mode)
            assert migration_manager.migration_mode == mode
        
        # Restore original mode
        migration_manager.set_migration_mode(original_mode)
        
        # Test migration readiness check
        readiness = migration_manager.check_migration_readiness()
        assert "current_mode" in readiness
        assert "configuration_valid" in readiness
        
        logger.info("✅ Migration manager test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration manager test failed: {e}")
        return False


def main():
    """Run basic tests."""
    print("="*80)
    print("NANCY CORE MCP PHASE 1 BASIC TESTS")
    print("="*80)
    
    tests = [
        ("Knowledge Packet Schema", test_knowledge_packet_schema),
        ("Configuration Manager", test_configuration_manager),
        ("Document MCP Server", test_document_server),
        ("Migration Manager", test_migration_manager)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            failed += 1
    
    print("-"*80)
    print(f"TOTAL: {passed + failed} tests, {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL BASIC TESTS PASSED! Nancy Core MCP Phase 1 core components are working.")
    else:
        print(f"⚠️  {failed} test(s) failed. Please review the implementation.")
    
    print("="*80)
    
    # Test document server in demo mode
    print("\nTesting Document Server Demo Mode:")
    try:
        os.system('python mcp-servers/document/server.py --demo')
    except Exception as e:
        print(f"Demo mode test failed: {e}")


if __name__ == "__main__":
    main()