#!/usr/bin/env python3
"""
Test script for nancy-memory MCP server integration with Nancy's four-brain architecture
"""

import sys
import os
import asyncio
import json
import logging

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp-servers', 'nancy-memory'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

from server import NancyMemoryMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_nancy_memory_integration():
    """Test nancy-memory MCP server integration with Nancy's API"""
    
    print("=" * 60)
    print("Nancy Memory MCP Server Integration Test")
    print("=" * 60)
    
    try:
        print("Creating MCP server instance...")
        mcp_server = NancyMemoryMCP()
        
        # Test 1: Ingestion - Call the function directly
        print("\n1. Testing Ingestion")
        print("-" * 30)
        
        # Get the ingest function from the MCP server
        ingest_func = None
        for tool_func in mcp_server.mcp._tools:
            if hasattr(tool_func, '__name__') and tool_func.__name__ == 'ingest_information':
                ingest_func = tool_func
                break
        
        if not ingest_func:
            print("Could not find ingest_information function")
            return False
        
        result = ingest_func(
            content='This is a test memory entry from MCP integration test. It contains information about the Nancy four-brain architecture and MCP orchestration.',
            content_type='test_document',
            author='Integration Test User', 
            filename='nancy_integration_test.txt',
            metadata={'project': 'nancy_integration_test', 'priority': 'high', 'test_case': 'memory_integration'}
        )
        
        print("Ingestion result:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'success':
            print("+ Ingestion successful")
        else:
            print("- Ingestion failed")
            return False
        
        # Wait a moment for processing
        print("\nWaiting for Nancy to process the content...")
        await asyncio.sleep(2)
        
        # Test 2: Query
        print("\n2. Testing Query")
        print("-" * 30)
        
        # Get the query function
        query_func = None
        for tool_func in mcp_server.mcp._tools:
            if hasattr(tool_func, '__name__') and tool_func.__name__ == 'query_memory':
                query_func = tool_func
                break
        
        if not query_func:
            print("Could not find query_memory function")
            return False
            
        query_result = query_func(
            question='nancy four-brain architecture integration test',
            n_results=5
        )
        
        print("Query result:")
        print(json.dumps(query_result, indent=2))
        
        if query_result.get('status') == 'success':
            print("+ Query successful")
            response = query_result.get('response', '')
            if 'integration test' in response.lower() or 'nancy' in response.lower():
                print("+ Query returned relevant content")
            else:
                print("~ Query response may not contain the ingested content")
        else:
            print("- Query failed")
        
        # Test 3: Check Nancy's ingestion status
        print("\n3. Checking Nancy's Ingestion Status")
        print("-" * 30)
        import requests
        try:
            ingest_status = requests.get("http://localhost:8000/api/ingest/status", timeout=10)
            if ingest_status.status_code == 200:
                status_data = ingest_status.json()
                print("Nancy ingestion status:")
                print(json.dumps(status_data, indent=2))
                
                # Check if packets were processed
                mcp_metrics = status_data.get('mcp_metrics', {})
                packets_processed = mcp_metrics.get('packets_processed', 0)
                print(f"\nPackets processed by Nancy: {packets_processed}")
                
                if packets_processed > 0:
                    print("+ Nancy processed MCP packets successfully")
                else:
                    print("~ Nancy has not processed any MCP packets yet")
            else:
                print(f"Failed to get Nancy status: {ingest_status.status_code}")
        except Exception as e:
            print(f"Error checking Nancy status: {e}")
        
        # Test 4: Author attribution test
        print("\n4. Testing Author Attribution")
        print("-" * 30)
        
        # Get the author attribution function
        author_func = None
        for tool_func in mcp_server.mcp._tools:
            if hasattr(tool_func, '__name__') and tool_func.__name__ == 'find_author_contributions':
                author_func = tool_func
                break
        
        if not author_func:
            print("Could not find find_author_contributions function")
            return False
            
        author_result = author_func(
            author_name='Integration Test User'
        )
        
        print("Author attribution result:")
        print(json.dumps(author_result, indent=2))
        
        if author_result.get('status') == 'success':
            contributions = author_result.get('contributions', [])
            print(f"Found {len(contributions)} contributions for author")
            if len(contributions) > 0:
                print("+ Author attribution working")
            else:
                print("~ No contributions found for author")
        else:
            print("- Author attribution failed")
        
        # Test 5: Project overview
        print("\n5. Testing Project Overview")
        print("-" * 30)
        
        # Get the project overview function
        overview_func = None
        for tool_func in mcp_server.mcp._tools:
            if hasattr(tool_func, '__name__') and tool_func.__name__ == 'get_project_overview':
                overview_func = tool_func
                break
        
        if not overview_func:
            print("Could not find get_project_overview function")
            return False
            
        overview_result = overview_func()
        
        print("Project overview result:")
        print(json.dumps(overview_result, indent=2))
        
        if overview_result.get('status') == 'success':
            print("+ Project overview successful")
        else:
            print("- Project overview failed")
        
        print("\n" + "=" * 60)
        print("Integration Test Complete")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        print(f"\n- Integration test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_nancy_memory_integration())
    exit(0 if success else 1)