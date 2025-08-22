#!/usr/bin/env python3
"""
Debug script to test knowledge packet validation
"""

import json
import sys
import os
from datetime import datetime
import hashlib

# Add nancy-services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'nancy-services'))

# Import Nancy schema
from schemas.knowledge_packet import NancyKnowledgePacket, KnowledgePacketValidator

def test_knowledge_packet_creation():
    """Test creating a knowledge packet that matches what nancy-memory MCP server creates"""
    
    # Content similar to what nancy-memory server creates
    content = "This is a test message to validate the knowledge packet schema."
    filename = "test_validation.txt"
    author = "Test Engineer"
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    # Build content for different brains
    packet_content = {
        "vector_data": {
            "chunks": [{
                "chunk_id": f"{filename}_chunk_0",
                "text": content,
                "chunk_metadata": {
                    "chunk_index": 0,
                    "source_file": filename
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
            "original_location": filename,
            "content_type": "document",
            "extraction_method": "mcp_direct_ingestion"
        },
        "metadata": {
            "title": filename,
            "author": author,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "content_hash": content_hash,
            "file_size": len(content.encode('utf-8')),
            "tags": ["test", "mcp_ingested"],
            "classification": "internal",
            "language": "en"
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
    
    print("Testing packet data:")
    print(json.dumps(packet_data, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test validation
    try:
        validator = KnowledgePacketValidator()
        print("1. Testing manual validation...")
        validator.validate(packet_data)
        print("PASS: Manual validation passed!")
        
        print("2. Testing NancyKnowledgePacket creation...")
        packet = NancyKnowledgePacket(packet_data)
        print("PASS: NancyKnowledgePacket creation passed!")
        
        print("3. Testing packet properties...")
        print(f"   Packet ID: {packet.packet_id}")
        print(f"   Source: {packet.source}")
        print(f"   Has vector data: {packet.has_vector_data()}")
        print(f"   Priority brain: {packet.get_priority_brain()}")
        
        return packet_data
        
    except Exception as e:
        print(f"FAIL: Validation failed: {e}")
        
        # Get detailed validation errors
        errors = validator.get_validation_errors(packet_data)
        if errors:
            print("\nDetailed validation errors:")
            for error in errors:
                print(f"  - {error}")
        
        return None

def test_minimal_packet():
    """Test the absolute minimal required packet"""
    
    content = "Test content"
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    minimal_packet = {
        "packet_version": "1.0",
        "packet_id": content_hash,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": {
            "mcp_server": "nancy-memory",
            "server_version": "1.0.0",
            "original_location": "test.txt",
            "content_type": "document"
        },
        "metadata": {
            "title": "Test Document"
        },
        "content": {}
    }
    
    print("\n" + "="*50)
    print("Testing minimal packet:")
    print(json.dumps(minimal_packet, indent=2))
    print("\n")
    
    try:
        validator = KnowledgePacketValidator()
        validator.validate(minimal_packet)
        print("PASS: Minimal packet validation passed!")
        return minimal_packet
    except Exception as e:
        print(f"FAIL: Minimal packet validation failed: {e}")
        errors = validator.get_validation_errors(minimal_packet)
        if errors:
            print("\nDetailed validation errors:")
            for error in errors:
                print(f"  - {error}")
        return None

if __name__ == "__main__":
    print("Knowledge Packet Validation Debug\n")
    
    # Test minimal packet first
    minimal_result = test_minimal_packet()
    
    # Test full packet
    full_result = test_knowledge_packet_creation()
    
    print("\n" + "="*50)
    print("Summary:")
    print(f"Minimal packet: {'PASSED' if minimal_result else 'FAILED'}")
    print(f"Full packet: {'PASSED' if full_result else 'FAILED'}")