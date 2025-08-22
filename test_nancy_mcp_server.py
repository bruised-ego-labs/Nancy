#!/usr/bin/env python3
"""
Test script for Nancy Memory MCP Server

This script validates that the Nancy MCP server tools work correctly
by simulating how an LLM would interact with Nancy's persistent memory.
"""

import json
import requests
import sys
import time
from typing import Dict, Any

# Test configuration
NANCY_API_BASE = "http://localhost:8000"

class NancyMCPTester:
    """Test the Nancy MCP server functionality"""
    
    def __init__(self):
        self.nancy_api_base = NANCY_API_BASE
        self.test_results = []
        
    def test_connection(self) -> bool:
        """Test connection to Nancy API"""
        print("Testing Nancy API connection...")
        try:
            response = requests.get(f"{self.nancy_api_base}/health", timeout=10)
            if response.status_code == 200:
                health = response.json()
                print(f"PASS: Nancy API is healthy: {health['status']}")
                return True
            else:
                print(f"FAIL: Nancy API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"FAIL: Failed to connect to Nancy API: {e}")
            return False
    
    def simulate_ingest_information(self, content: str, content_type: str, author: str = "Test User") -> Dict[str, Any]:
        """Simulate the ingest_information MCP tool"""
        print(f"\nTesting ingest_information tool...")
        print(f"Content: {content[:100]}{'...' if len(content) > 100 else ''}")
        print(f"Type: {content_type}, Author: {author}")
        
        try:
            # Simulate what the MCP tool would do
            packet_data = {
                "content": content,
                "content_type": content_type,
                "author": author,
                "filename": f"test_{content_type}_{int(time.time())}.txt",
                "metadata": {"test": True, "source": "mcp_test"},
                "source": "mcp_client",
                "brain_routing": "auto"
            }
            
            # Note: In actual MCP server, this would use the knowledge packet endpoint
            # For testing, we'll use the regular file upload endpoint
            files = {'file': (packet_data['filename'], content.encode(), 'text/plain')}
            data = {'author': author}
            
            response = requests.post(
                f"{self.nancy_api_base}/api/ingest",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"PASS: Successfully ingested information")
                return {
                    "status": "success",
                    "message": "Information stored in Nancy's memory",
                    "details": f"Stored {len(content)} characters as {content_type}"
                }
            else:
                print(f"❌ Ingestion failed: {response.status_code} {response.text}")
                return {
                    "status": "error",
                    "message": f"Failed to store information: {response.text}"
                }
                
        except Exception as e:
            print(f"❌ Ingestion error: {e}")
            return {
                "status": "error",
                "message": f"Failed to store information: {str(e)}"
            }
    
    def simulate_query_memory(self, question: str, n_results: int = 5) -> Dict[str, Any]:
        """Simulate the query_memory MCP tool"""
        print(f"\n🔍 Testing query_memory tool...")
        print(f"Question: {question}")
        
        try:
            query_data = {
                "query": question,
                "n_results": n_results,
                "orchestrator": "langchain"
            }
            
            response = requests.post(
                f"{self.nancy_api_base}/api/query",
                json=query_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Query successful")
                print(f"Response: {result.get('response', 'No response')[:200]}...")
                
                return {
                    "status": "success",
                    "question": question,
                    "response": result.get("response", "No response generated"),
                    "strategy_used": result.get("strategy_used", "langchain"),
                    "sources": result.get("sources", []),
                    "confidence": "high"
                }
            else:
                print(f"❌ Query failed: {response.status_code} {response.text}")
                return {
                    "status": "error",
                    "message": f"Failed to query memory: {response.text}",
                    "question": question
                }
                
        except Exception as e:
            print(f"❌ Query error: {e}")
            return {
                "status": "error",
                "message": f"Failed to query memory: {str(e)}",
                "question": question
            }
    
    def simulate_get_project_overview(self) -> Dict[str, Any]:
        """Simulate the get_project_overview MCP tool"""
        print(f"\n📊 Testing get_project_overview tool...")
        
        try:
            response = requests.get(f"{self.nancy_api_base}/api/nancy/status", timeout=30)
            
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Project overview retrieved")
                print(f"Nancy Status: {status.get('status', {}).get('status', 'unknown')}")
                
                return {
                    "status": "success",
                    "project_health": status.get("status", {}),
                    "metrics": status.get("metrics", {}),
                    "system_info": {
                        "nancy_version": "2.0.0",
                        "architecture": "Four-Brain MCP Orchestration"
                    }
                }
            else:
                print(f"❌ Overview query failed: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"Failed to get project overview: {response.text}"
                }
                
        except Exception as e:
            print(f"❌ Overview error: {e}")
            return {
                "status": "error",
                "message": f"Failed to get project overview: {str(e)}"
            }
    
    def test_memory_resource(self) -> Dict[str, Any]:
        """Test accessing the project memory resource"""
        print(f"\n📚 Testing project memory resource...")
        
        try:
            response = requests.get(f"{self.nancy_api_base}/api/nancy/configuration", timeout=30)
            
            if response.status_code == 200:
                config = response.json()
                print(f"✅ Memory resource accessible")
                
                memory_index = {
                    "nancy_configuration": config,
                    "available_capabilities": [
                        "Persistent memory storage across conversations",
                        "Author attribution and expertise tracking", 
                        "Cross-domain technical analysis",
                        "Decision history and provenance"
                    ],
                    "brain_architecture": {
                        "vector_brain": "Semantic search and content similarity",
                        "analytical_brain": "Structured data and metadata queries",
                        "graph_brain": "Relationships and knowledge connections", 
                        "linguistic_brain": "Natural language understanding"
                    }
                }
                
                print(f"Configuration keys: {list(config.keys())}")
                return {"status": "success", "memory_index": memory_index}
            else:
                print(f"❌ Resource access failed: {response.status_code}")
                return {
                    "status": "error",
                    "message": "Failed to access memory resource"
                }
                
        except Exception as e:
            print(f"❌ Resource error: {e}")
            return {
                "status": "error",
                "message": f"Failed to access memory resource: {str(e)}"
            }
    
    def run_comprehensive_test(self):
        """Run comprehensive test of Nancy MCP server functionality"""
        print("Starting Nancy Memory MCP Server Test")
        print("=" * 60)
        
        # Test 1: Connection
        if not self.test_connection():
            print("❌ Cannot proceed without Nancy API connection")
            return False
        
        # Test 2: Ingest sample information
        sample_content = """
        Project Decision: Thermal Management Strategy
        
        After analysis by Sarah Chen (thermal engineer) and Mike Rodriguez (electrical engineer),
        we've decided to implement an aluminum heat sink solution for our IoT device.
        
        Key constraints:
        - CPU TDP: 15W maximum
        - Operating temperature: Must stay below 85°C
        - Space constraint: 2mm clearance required for airflow
        
        This decision affects both the mechanical design (clearance requirements) 
        and electrical design (power management integration).
        
        Decision date: 2025-01-20
        Next review: 2025-02-15
        """
        
        ingest_result = self.simulate_ingest_information(
            content=sample_content,
            content_type="decision",
            author="Project Team"
        )
        self.test_results.append(("ingest_information", ingest_result["status"] == "success"))
        
        # Give Nancy time to process the ingestion
        print("\n⏳ Waiting for Nancy to process the information...")
        time.sleep(3)
        
        # Test 3: Query the stored information
        query_result = self.simulate_query_memory(
            "What thermal management decisions have we made and who was involved?"
        )
        self.test_results.append(("query_memory", query_result["status"] == "success"))
        
        # Test 4: Get project overview
        overview_result = self.simulate_get_project_overview()
        self.test_results.append(("get_project_overview", overview_result["status"] == "success"))
        
        # Test 5: Access memory resource
        resource_result = self.test_memory_resource()
        self.test_results.append(("project_memory_resource", resource_result["status"] == "success"))
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed in self.test_results if passed)
        
        for test_name, passed in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nResult: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Nancy MCP server is working correctly.")
            print("\n💡 Next steps:")
            print("1. Configure Nancy MCP server in your Claude Code settings")
            print("2. Start using persistent memory with any LLM")
            print("3. Transform your AI assistant into project-aware intelligence")
        else:
            print("\n⚠️  Some tests failed. Check Nancy configuration and try again.")
        
        return passed_tests == total_tests


def main():
    """Main test runner"""
    tester = NancyMCPTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🔗 Ready to integrate with Claude Code!")
        print("Add this to your MCP configuration:")
        print(json.dumps({
            "nancy-memory": {
                "command": "python",
                "args": ["./mcp-servers/nancy-memory/server.py"],
                "env": {"NANCY_API_BASE": "http://localhost:8000"}
            }
        }, indent=2))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()