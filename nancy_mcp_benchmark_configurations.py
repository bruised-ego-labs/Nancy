#!/usr/bin/env python3
"""
Nancy MCP Configuration Management for Comprehensive Benchmarking

This script manages different Nancy configurations for testing various MCP
architecture scenarios against baseline RAG systems.

Configuration Variants:
1. Nancy MCP Full Stack - All servers enabled
2. Nancy MCP Spreadsheet Only - Incremental adoption testing  
3. Nancy MCP Development Focus - Code and document servers
4. Nancy MCP Selective - Custom server combinations
5. Baseline RAG Enhanced - Improved baseline for fair comparison

Author: Strategic Technical Architect
Purpose: Validate Nancy's MCP architecture benefits and optimization opportunities
"""

import os
import yaml
import json
import shutil
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import time

class NancyMCPConfigurationManager:
    def __init__(self, base_dir: str = "C:\\Users\\scott\\Documents\\Nancy"):
        self.base_dir = base_dir
        self.config_dir = os.path.join(base_dir, "benchmark_configurations")
        self.nancy_config_path = os.path.join(base_dir, "nancy-config.yaml")
        self.backup_config_path = os.path.join(self.config_dir, "nancy-config-backup.yaml")
        
        # Create configuration directory
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Service endpoints
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"
        
        # Configuration definitions
        self.configurations = self._define_configurations()
    
    def _define_configurations(self) -> Dict[str, Dict]:
        """Define all Nancy MCP configuration variants"""
        return {
            "nancy_mcp_full": {
                "name": "Nancy MCP Full Stack",
                "description": "All MCP servers enabled - complete architecture demonstration",
                "strategic_value": "Maximum capability showcase",
                "use_cases": ["Enterprise deployment", "Full feature demonstration", "Complex engineering workflows"],
                "config": {
                    "mcp_servers": {
                        "enabled": True,
                        "enabled_servers": [
                            {
                                "name": "nancy-spreadsheet-server",
                                "executable": "python",
                                "args": ["./mcp-servers/spreadsheet/server.py"],
                                "auto_start": True,
                                "capabilities": ["nancy/ingest", "nancy/health_check"],
                                "supported_extensions": [".xlsx", ".xls", ".csv"]
                            },
                            {
                                "name": "nancy-codebase-server", 
                                "executable": "python",
                                "args": ["./mcp-servers/codebase/server.py"],
                                "auto_start": True,
                                "capabilities": ["nancy/analyze", "nancy/health_check"],
                                "supported_extensions": [".py", ".js", ".md", ".json", ".yaml", ".yml"]
                            },
                            {
                                "name": "nancy-document-server",
                                "executable": "python", 
                                "args": ["./mcp-servers/document/server.py"],
                                "auto_start": True,
                                "capabilities": ["nancy/ingest", "nancy/health_check"],
                                "supported_extensions": [".txt", ".pdf", ".docx"]
                            }
                        ]
                    },
                    "orchestration": {
                        "strategy": "langchain_router",
                        "four_brain_enabled": True,
                        "multi_step_processing": True,
                        "relationship_extraction": True
                    },
                    "performance": {
                        "query_timeout": 180,
                        "mcp_timeout": 30,
                        "concurrent_servers": 3,
                        "memory_limit_mb": 2048
                    }
                }
            },
            
            "nancy_mcp_spreadsheet_only": {
                "name": "Nancy MCP Spreadsheet Only",
                "description": "Only spreadsheet MCP server enabled - incremental adoption scenario",
                "strategic_value": "Migration path demonstration",
                "use_cases": ["Incremental MCP adoption", "Data-heavy workflows", "Structured data focus"],
                "config": {
                    "mcp_servers": {
                        "enabled": True,
                        "enabled_servers": [
                            {
                                "name": "nancy-spreadsheet-server",
                                "executable": "python",
                                "args": ["./mcp-servers/spreadsheet/server.py"],
                                "auto_start": True,
                                "capabilities": ["nancy/ingest", "nancy/health_check"],
                                "supported_extensions": [".xlsx", ".xls", ".csv"]
                            }
                        ]
                    },
                    "orchestration": {
                        "strategy": "langchain_router",
                        "four_brain_enabled": True,
                        "multi_step_processing": True,
                        "relationship_extraction": True
                    },
                    "performance": {
                        "query_timeout": 120,
                        "mcp_timeout": 30,
                        "concurrent_servers": 1,
                        "memory_limit_mb": 1024
                    }
                }
            },
            
            "nancy_mcp_development_focus": {
                "name": "Nancy MCP Development Focus", 
                "description": "Codebase and document servers - development team workflow",
                "strategic_value": "Developer productivity showcase",
                "use_cases": ["Software development teams", "Code analysis workflows", "Documentation management"],
                "config": {
                    "mcp_servers": {
                        "enabled": True,
                        "enabled_servers": [
                            {
                                "name": "nancy-codebase-server",
                                "executable": "python", 
                                "args": ["./mcp-servers/codebase/server.py"],
                                "auto_start": True,
                                "capabilities": ["nancy/analyze", "nancy/health_check"],
                                "supported_extensions": [".py", ".js", ".md", ".json", ".yaml", ".yml"]
                            },
                            {
                                "name": "nancy-document-server",
                                "executable": "python",
                                "args": ["./mcp-servers/document/server.py"], 
                                "auto_start": True,
                                "capabilities": ["nancy/ingest", "nancy/health_check"],
                                "supported_extensions": [".txt", ".pdf", ".docx"]
                            }
                        ]
                    },
                    "orchestration": {
                        "strategy": "langchain_router",
                        "four_brain_enabled": True,
                        "multi_step_processing": True,
                        "relationship_extraction": True
                    },
                    "performance": {
                        "query_timeout": 150,
                        "mcp_timeout": 30,
                        "concurrent_servers": 2,
                        "memory_limit_mb": 1536
                    }
                }
            },
            
            "nancy_mcp_disabled": {
                "name": "Nancy MCP Disabled (Legacy Mode)",
                "description": "MCP servers disabled - monolithic processing for comparison",
                "strategic_value": "Performance baseline comparison",
                "use_cases": ["Legacy system comparison", "Performance benchmarking", "Migration analysis"],
                "config": {
                    "mcp_servers": {
                        "enabled": False,
                        "enabled_servers": []
                    },
                    "orchestration": {
                        "strategy": "langchain_router",
                        "four_brain_enabled": True,
                        "multi_step_processing": True,
                        "relationship_extraction": True
                    },
                    "performance": {
                        "query_timeout": 120,
                        "mcp_timeout": 0,
                        "concurrent_servers": 0,
                        "memory_limit_mb": 1024
                    }
                }
            }
        }
    
    def backup_current_configuration(self) -> bool:
        """Backup current Nancy configuration"""
        try:
            if os.path.exists(self.nancy_config_path):
                shutil.copy2(self.nancy_config_path, self.backup_config_path)
                print(f"✅ Backed up current configuration to {self.backup_config_path}")
                return True
            else:
                print(f"⚠️  No existing configuration found at {self.nancy_config_path}")
                return False
        except Exception as e:
            print(f"❌ Failed to backup configuration: {e}")
            return False
    
    def apply_configuration(self, config_name: str) -> bool:
        """Apply a specific Nancy configuration"""
        if config_name not in self.configurations:
            print(f"❌ Unknown configuration: {config_name}")
            return False
        
        config_def = self.configurations[config_name]
        print(f"🔧 Applying configuration: {config_def['name']}")
        print(f"   Description: {config_def['description']}")
        
        try:
            # Create full configuration structure
            full_config = {
                "configuration_name": config_name,
                "applied_timestamp": datetime.now().isoformat(),
                "strategic_value": config_def["strategic_value"],
                "use_cases": config_def["use_cases"]
            }
            
            # Merge with configuration settings
            full_config.update(config_def["config"])
            
            # Write configuration file
            with open(self.nancy_config_path, 'w') as f:
                yaml.dump(full_config, f, default_flow_style=False, indent=2)
            
            print(f"✅ Configuration applied successfully")
            print(f"   MCP Servers: {'Enabled' if config_def['config']['mcp_servers']['enabled'] else 'Disabled'}")
            
            if config_def['config']['mcp_servers']['enabled']:
                server_count = len(config_def['config']['mcp_servers']['enabled_servers'])
                print(f"   Active Servers: {server_count}")
                for server in config_def['config']['mcp_servers']['enabled_servers']:
                    print(f"     - {server['name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply configuration: {e}")
            return False
    
    def restore_backup_configuration(self) -> bool:
        """Restore the backed up configuration"""
        try:
            if os.path.exists(self.backup_config_path):
                shutil.copy2(self.backup_config_path, self.nancy_config_path)
                print(f"✅ Restored configuration from backup")
                return True
            else:
                print(f"❌ No backup configuration found")
                return False
        except Exception as e:
            print(f"❌ Failed to restore configuration: {e}")
            return False
    
    def validate_configuration(self, config_name: str) -> Dict[str, Any]:
        """Validate a configuration by testing system health"""
        print(f"🔍 Validating configuration: {config_name}")
        
        validation_result = {
            "configuration": config_name,
            "timestamp": datetime.now().isoformat(),
            "health_checks": {},
            "performance_tests": {},
            "overall_status": "unknown"
        }
        
        try:
            # Test Nancy health endpoint
            print("   → Testing Nancy health...")
            nancy_response = requests.get(f"{self.nancy_url}/health", timeout=30)
            validation_result["health_checks"]["nancy"] = {
                "status_code": nancy_response.status_code,
                "healthy": nancy_response.status_code == 200,
                "response_time": nancy_response.elapsed.total_seconds()
            }
            
            if nancy_response.status_code == 200:
                health_data = nancy_response.json()
                validation_result["health_checks"]["nancy"]["details"] = health_data
                print(f"     ✅ Nancy healthy (response: {nancy_response.elapsed.total_seconds():.2f}s)")
            else:
                print(f"     ❌ Nancy unhealthy (HTTP {nancy_response.status_code})")
            
        except Exception as e:
            validation_result["health_checks"]["nancy"] = {
                "healthy": False,
                "error": str(e)
            }
            print(f"     ❌ Nancy health check failed: {e}")
        
        # Test basic query performance
        try:
            print("   → Testing basic query performance...")
            test_query = {"query": "What is the system status?"}
            
            query_start = time.time()
            query_response = requests.post(
                f"{self.nancy_url}/api/query",
                json=test_query,
                timeout=60
            )
            query_time = time.time() - query_start
            
            validation_result["performance_tests"]["basic_query"] = {
                "status_code": query_response.status_code,
                "successful": query_response.status_code == 200,
                "response_time": query_time,
                "timeout": False
            }
            
            if query_response.status_code == 200:
                response_data = query_response.json()
                validation_result["performance_tests"]["basic_query"]["response_length"] = len(response_data.get("response", ""))
                print(f"     ✅ Query successful ({query_time:.2f}s)")
            else:
                print(f"     ❌ Query failed (HTTP {query_response.status_code})")
            
        except requests.exceptions.Timeout:
            validation_result["performance_tests"]["basic_query"] = {
                "successful": False,
                "timeout": True,
                "response_time": 60.0
            }
            print(f"     ⏰ Query timed out")
        except Exception as e:
            validation_result["performance_tests"]["basic_query"] = {
                "successful": False,
                "error": str(e)
            }
            print(f"     ❌ Query test failed: {e}")
        
        # Overall status assessment
        nancy_healthy = validation_result["health_checks"].get("nancy", {}).get("healthy", False)
        query_successful = validation_result["performance_tests"].get("basic_query", {}).get("successful", False)
        
        if nancy_healthy and query_successful:
            validation_result["overall_status"] = "healthy"
            print("   ✅ Configuration validation PASSED")
        elif nancy_healthy:
            validation_result["overall_status"] = "functional"
            print("   ⚠️  Configuration partially functional (health OK, query issues)")
        else:
            validation_result["overall_status"] = "unhealthy"
            print("   ❌ Configuration validation FAILED")
        
        return validation_result
    
    def run_configuration_benchmark(self, config_name: str, test_queries: List[str]) -> Dict[str, Any]:
        """Run performance benchmark for a specific configuration"""
        print(f"🏃 Running benchmark for configuration: {config_name}")
        
        benchmark_result = {
            "configuration": config_name,
            "timestamp": datetime.now().isoformat(),
            "test_queries": len(test_queries),
            "query_results": [],
            "performance_summary": {}
        }
        
        successful_queries = 0
        total_response_time = 0
        response_lengths = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"   → Query {i}/{len(test_queries)}: {query[:60]}{'...' if len(query) > 60 else ''}")
            
            try:
                query_start = time.time()
                response = requests.post(
                    f"{self.nancy_url}/api/query",
                    json={"query": query},
                    timeout=120
                )
                query_time = time.time() - query_start
                
                query_result = {
                    "query_id": i,
                    "query": query,
                    "status_code": response.status_code,
                    "successful": response.status_code == 200,
                    "response_time": query_time
                }
                
                if response.status_code == 200:
                    response_data = response.json()
                    query_result["response"] = response_data.get("response", "")
                    query_result["sources"] = response_data.get("sources", [])
                    query_result["response_length"] = len(response_data.get("response", ""))
                    query_result["source_count"] = len(response_data.get("sources", []))
                    
                    successful_queries += 1
                    total_response_time += query_time
                    response_lengths.append(query_result["response_length"])
                    
                    print(f"     ✅ Success ({query_time:.1f}s, {query_result['response_length']} chars)")
                else:
                    query_result["error"] = response.text
                    print(f"     ❌ Failed (HTTP {response.status_code})")
                
                benchmark_result["query_results"].append(query_result)
                
            except requests.exceptions.Timeout:
                query_result = {
                    "query_id": i,
                    "query": query,
                    "successful": False,
                    "timeout": True,
                    "response_time": 120.0
                }
                benchmark_result["query_results"].append(query_result)
                print(f"     ⏰ Timeout (120s)")
                
            except Exception as e:
                query_result = {
                    "query_id": i,
                    "query": query,
                    "successful": False,
                    "error": str(e)
                }
                benchmark_result["query_results"].append(query_result)
                print(f"     ❌ Error: {e}")
        
        # Calculate performance summary
        benchmark_result["performance_summary"] = {
            "success_rate": successful_queries / len(test_queries) if test_queries else 0,
            "average_response_time": total_response_time / successful_queries if successful_queries > 0 else 0,
            "total_queries": len(test_queries),
            "successful_queries": successful_queries,
            "failed_queries": len(test_queries) - successful_queries,
            "average_response_length": sum(response_lengths) / len(response_lengths) if response_lengths else 0
        }
        
        print(f"   📊 Benchmark complete:")
        print(f"     Success Rate: {benchmark_result['performance_summary']['success_rate']:.1%}")
        print(f"     Avg Response Time: {benchmark_result['performance_summary']['average_response_time']:.2f}s")
        print(f"     Avg Response Length: {benchmark_result['performance_summary']['average_response_length']:.0f} chars")
        
        return benchmark_result
    
    def generate_configuration_comparison_report(self, benchmark_results: List[Dict]) -> Dict[str, Any]:
        """Generate comparison report across configurations"""
        print("📈 Generating configuration comparison report...")
        
        comparison_report = {
            "timestamp": datetime.now().isoformat(),
            "configurations_tested": len(benchmark_results),
            "comparative_analysis": {},
            "recommendations": []
        }
        
        # Extract performance metrics for comparison
        config_performance = {}
        for result in benchmark_results:
            config_name = result["configuration"]
            perf = result["performance_summary"]
            config_performance[config_name] = {
                "success_rate": perf["success_rate"],
                "avg_response_time": perf["average_response_time"],
                "avg_response_length": perf["average_response_length"],
                "configuration_details": self.configurations.get(config_name, {})
            }
        
        comparison_report["comparative_analysis"] = config_performance
        
        # Generate recommendations
        if len(config_performance) >= 2:
            # Find best performing configuration
            best_success_rate = max(config_performance.values(), key=lambda x: x["success_rate"])
            fastest_response = min(config_performance.values(), key=lambda x: x["avg_response_time"])
            
            for config_name, perf in config_performance.items():
                if perf["success_rate"] == best_success_rate["success_rate"]:
                    comparison_report["recommendations"].append(f"Highest success rate: {config_name} ({perf['success_rate']:.1%})")
                if perf["avg_response_time"] == fastest_response["avg_response_time"]:
                    comparison_report["recommendations"].append(f"Fastest response: {config_name} ({perf['avg_response_time']:.2f}s)")
            
            # Strategic recommendations
            if "nancy_mcp_full" in config_performance:
                full_perf = config_performance["nancy_mcp_full"]
                comparison_report["recommendations"].append(f"Full MCP stack performance: {full_perf['success_rate']:.1%} success, {full_perf['avg_response_time']:.2f}s avg")
            
            if "nancy_mcp_disabled" in config_performance:
                disabled_perf = config_performance["nancy_mcp_disabled"]
                comparison_report["recommendations"].append(f"Legacy mode performance: {disabled_perf['success_rate']:.1%} success, {disabled_perf['avg_response_time']:.2f}s avg")
        
        return comparison_report
    
    def list_configurations(self) -> None:
        """List all available configurations"""
        print("🔧 Available Nancy MCP Configurations:")
        print("=" * 50)
        
        for config_name, config_def in self.configurations.items():
            print(f"\\n📋 {config_def['name']}")
            print(f"   ID: {config_name}")
            print(f"   Description: {config_def['description']}")
            print(f"   Strategic Value: {config_def['strategic_value']}")
            print(f"   Use Cases: {', '.join(config_def['use_cases'])}")
            
            mcp_enabled = config_def['config']['mcp_servers']['enabled']
            if mcp_enabled:
                server_count = len(config_def['config']['mcp_servers']['enabled_servers'])
                print(f"   MCP Servers: {server_count} enabled")
            else:
                print(f"   MCP Servers: Disabled (Legacy mode)")
    
    def save_configuration_to_file(self, config_name: str, filename: Optional[str] = None) -> str:
        """Save a configuration to a standalone file"""
        if config_name not in self.configurations:
            raise ValueError(f"Unknown configuration: {config_name}")
        
        if filename is None:
            filename = f"nancy-config-{config_name}.yaml"
        
        filepath = os.path.join(self.config_dir, filename)
        config_def = self.configurations[config_name]
        
        # Create full configuration
        full_config = {
            "configuration_name": config_name,
            "created_timestamp": datetime.now().isoformat(),
            "strategic_value": config_def["strategic_value"],
            "use_cases": config_def["use_cases"]
        }
        full_config.update(config_def["config"])
        
        with open(filepath, 'w') as f:
            yaml.dump(full_config, f, default_flow_style=False, indent=2)
        
        return filepath

def main():
    """Demo configuration management capabilities"""
    manager = NancyMCPConfigurationManager()
    
    print("🚀 Nancy MCP Configuration Management System")
    print("=" * 50)
    
    # List available configurations
    manager.list_configurations()
    
    # Save all configurations to files
    print("\\n💾 Saving configuration files...")
    for config_name in manager.configurations.keys():
        filepath = manager.save_configuration_to_file(config_name)
        print(f"   ✅ {config_name} → {filepath}")
    
    print(f"\\n📁 Configuration files saved to: {manager.config_dir}")
    print(f"🔧 Use apply_configuration(config_name) to activate a configuration")
    print(f"🔍 Use validate_configuration(config_name) to test a configuration")
    print(f"🏃 Use run_configuration_benchmark(config_name, queries) for performance testing")

if __name__ == "__main__":
    main()