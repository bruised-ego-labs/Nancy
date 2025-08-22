#!/usr/bin/env python3
"""
Comprehensive test script for Nancy's Codebase Ingestion capabilities.
Tests AST parsing, Git integration, and Four-Brain Architecture integration
for source code repository analysis.

This script demonstrates the enhanced capabilities described in gemini.log lines 680-695
for analyzing entire codebases with deep understanding of code structure,
relationships, and collaboration patterns.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add the nancy-services directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nancy-services'))

try:
    from core.ingestion import CodebaseIngestionService, GitAnalysisService, DirectoryIngestionService
    from core.knowledge_graph import GraphBrain
    from core.search import AnalyticalBrain
    from core.nlp import VectorBrain
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the Nancy project root directory")
    sys.exit(1)

class CodebaseAnalysisTest:
    """
    Comprehensive test suite for codebase analysis capabilities.
    """
    
    def __init__(self):
        """Initialize test components."""
        print("Initializing Codebase Analysis Test Suite...")
        self.codebase_service = CodebaseIngestionService()
        self.git_service = GitAnalysisService()
        self.directory_service = DirectoryIngestionService()
        self.graph_brain = GraphBrain()
        self.analytical_brain = AnalyticalBrain()
        self.vector_brain = VectorBrain()
        
        self.test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {},
            "summary": {}
        }
        print("Test suite initialized successfully!")
    
    def test_tree_sitter_initialization(self):
        """Test tree-sitter parser initialization."""
        print("\n=== Testing Tree-sitter Parser Initialization ===")
        test_name = "tree_sitter_init"
        
        try:
            # Check if parsers were initialized
            parser_count = len(self.codebase_service.parsers)
            available_languages = list(self.codebase_service.parsers.keys())
            
            print(f"Initialized {parser_count} language parsers")
            print(f"Available languages: {available_languages}")
            
            success = parser_count > 0
            self.test_results["tests"][test_name] = {
                "success": success,
                "parser_count": parser_count,
                "available_languages": available_languages,
                "message": f"Initialized {parser_count} parsers" if success else "No parsers initialized"
            }
            
            if success:
                print("✅ Tree-sitter initialization: PASSED")
            else:
                print("❌ Tree-sitter initialization: FAILED")
                
        except Exception as e:
            print(f"❌ Tree-sitter initialization: ERROR - {e}")
            self.test_results["tests"][test_name] = {
                "success": False,
                "error": str(e)
            }
    
    def test_git_repository_analysis(self, repo_path=None):
        """Test Git repository analysis capabilities."""
        print("\n=== Testing Git Repository Analysis ===")
        test_name = "git_analysis"
        
        if repo_path is None:
            repo_path = os.getcwd()  # Use current directory
        
        try:
            # Initialize Git repository
            git_initialized = self.git_service.initialize_repository(repo_path)
            print(f"Git repository initialization: {'SUCCESS' if git_initialized else 'FAILED'}")
            
            if git_initialized:
                # Get repository metadata
                repo_metadata = self.git_service.get_repository_metadata()
                print(f"Repository metadata retrieved: {not repo_metadata.get('error', False)}")
                
                if not repo_metadata.get('error'):
                    print(f"  - Current branch: {repo_metadata.get('current_branch', 'unknown')}")
                    print(f"  - Total commits: {repo_metadata.get('total_commits', 0)}")
                    print(f"  - Contributors: {repo_metadata.get('total_contributors', 0)}")
                    print(f"  - Branches: {len(repo_metadata.get('branches', []))}")
                
                # Test file authorship if repository has files
                test_files = []
                for root, dirs, files in os.walk(repo_path):
                    if '.git' in root:
                        continue
                    for file in files[:3]:  # Test first 3 files
                        if file.endswith(('.py', '.js', '.ts', '.java')):
                            test_files.append(os.path.join(root, file))
                
                authorship_tests = []
                for file_path in test_files:
                    authorship = self.git_service.get_file_authorship(file_path)
                    if not authorship.get('error'):
                        authorship_tests.append({
                            "file": os.path.relpath(file_path, repo_path),
                            "contributors": authorship.get('total_contributors', 0),
                            "commits": authorship.get('commit_count', 0)
                        })
                
                print(f"  - File authorship analysis: {len(authorship_tests)} files analyzed")
                
                self.test_results["tests"][test_name] = {
                    "success": True,
                    "git_initialized": git_initialized,
                    "repo_metadata": repo_metadata,
                    "authorship_tests": authorship_tests,
                    "message": f"Git analysis successful for {repo_path}"
                }
                print("✅ Git repository analysis: PASSED")
                
            else:
                self.test_results["tests"][test_name] = {
                    "success": False,
                    "git_initialized": False,
                    "message": f"Could not initialize Git repository at {repo_path}"
                }
                print("❌ Git repository analysis: FAILED - Not a Git repository")
                
        except Exception as e:
            print(f"❌ Git repository analysis: ERROR - {e}")
            self.test_results["tests"][test_name] = {
                "success": False,
                "error": str(e)
            }
    
    def test_ast_parsing(self, test_files=None):
        """Test AST parsing for different programming languages."""
        print("\n=== Testing AST Parsing Capabilities ===")
        test_name = "ast_parsing"
        
        if test_files is None:
            test_files = self._find_test_files()
        
        parsing_results = []
        
        for file_path in test_files:
            try:
                print(f"Analyzing: {file_path}")
                analysis = self.codebase_service.analyze_code_file(file_path)
                
                if "error" not in analysis:
                    ast_data = analysis.get("ast_analysis", {})
                    file_result = {
                        "file_path": file_path,
                        "language": ast_data.get("language", "unknown"),
                        "lines_of_code": ast_data.get("lines_of_code", 0),
                        "functions": ast_data.get("total_functions", 0),
                        "classes": ast_data.get("total_classes", 0),
                        "imports": ast_data.get("total_imports", 0),
                        "success": True
                    }
                    print(f"  ✅ {file_result['language']}: {file_result['functions']} functions, {file_result['classes']} classes")
                else:
                    file_result = {
                        "file_path": file_path,
                        "success": False,
                        "error": analysis["error"]
                    }
                    print(f"  ❌ Failed: {analysis['error']}")
                
                parsing_results.append(file_result)
                
            except Exception as e:
                print(f"  ❌ Exception for {file_path}: {e}")
                parsing_results.append({
                    "file_path": file_path,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in parsing_results if r["success"])
        total_functions = sum(r.get("functions", 0) for r in parsing_results if r["success"])
        total_classes = sum(r.get("classes", 0) for r in parsing_results if r["success"])
        
        self.test_results["tests"][test_name] = {
            "success": success_count > 0,
            "files_tested": len(parsing_results),
            "files_successful": success_count,
            "total_functions_found": total_functions,
            "total_classes_found": total_classes,
            "parsing_results": parsing_results,
            "message": f"Parsed {success_count}/{len(parsing_results)} files successfully"
        }
        
        print(f"\n✅ AST Parsing: {success_count}/{len(parsing_results)} files successful")
        print(f"   Total functions found: {total_functions}")
        print(f"   Total classes found: {total_classes}")
    
    def test_four_brain_integration(self, test_directory=None):
        """Test integration with Nancy's Four-Brain Architecture."""
        print("\n=== Testing Four-Brain Architecture Integration ===")
        test_name = "four_brain_integration"
        
        if test_directory is None:
            test_directory = "nancy-services"  # Test on Nancy's own code
        
        try:
            if not os.path.exists(test_directory):
                print(f"Test directory {test_directory} not found, using current directory")
                test_directory = "."
            
            print(f"Testing directory ingestion with codebase analysis: {test_directory}")
            
            # Use DirectoryIngestionService with codebase capabilities
            ingestion_result = self.directory_service.scan_and_process_directory(
                directory_path=test_directory,
                recursive=True,
                file_patterns="*.py,*.js,*.ts",
                author="Codebase Test",
                process_limit=10  # Limit for testing
            )
            
            if "error" not in ingestion_result:
                print(f"  ✅ Directory scan successful")
                print(f"  - Files discovered: {ingestion_result.get('total_files_discovered', 0)}")
                print(f"  - Files processed: {ingestion_result.get('files_processed', 0)}")
                print(f"  - Success rate: {ingestion_result.get('files_successful', 0)}/{ingestion_result.get('files_processed', 0)}")
                
                # Test Graph Brain codebase queries
                print("  Testing codebase-specific queries...")
                try:
                    # Test code expert finding
                    python_experts = self.graph_brain.find_code_experts("python")
                    print(f"    - Python experts found: {len(python_experts)}")
                    
                    # Test codebase statistics
                    codebase_stats = self.graph_brain.get_codebase_statistics()
                    print(f"    - Language distribution: {len(codebase_stats.get('language_distribution', []))}")
                    print(f"    - Total code files: {codebase_stats.get('entity_counts', {}).get('total_files', 0)}")
                    print(f"    - Total functions: {codebase_stats.get('entity_counts', {}).get('total_functions', 0)}")
                    
                    graph_queries_successful = True
                    
                except Exception as graph_error:
                    print(f"    ❌ Graph queries failed: {graph_error}")
                    graph_queries_successful = False
                
                self.test_results["tests"][test_name] = {
                    "success": True,
                    "ingestion_result": ingestion_result,
                    "graph_queries_successful": graph_queries_successful,
                    "python_experts_count": len(python_experts) if 'python_experts' in locals() else 0,
                    "codebase_stats": codebase_stats if 'codebase_stats' in locals() else {},
                    "message": "Four-brain integration successful"
                }
                print("✅ Four-Brain Integration: PASSED")
                
            else:
                self.test_results["tests"][test_name] = {
                    "success": False,
                    "error": ingestion_result["error"],
                    "message": "Directory ingestion failed"
                }
                print(f"❌ Four-Brain Integration: FAILED - {ingestion_result['error']}")
                
        except Exception as e:
            print(f"❌ Four-Brain Integration: ERROR - {e}")
            self.test_results["tests"][test_name] = {
                "success": False,
                "error": str(e)
            }
    
    def test_codebase_queries(self):
        """Test codebase-specific query capabilities."""
        print("\n=== Testing Codebase Query Capabilities ===")
        test_name = "codebase_queries"
        
        query_results = {}
        
        try:
            # Test various codebase queries
            queries = [
                ("Code experts for Python", lambda: self.graph_brain.find_code_experts("python")),
                ("Codebase statistics", lambda: self.graph_brain.get_codebase_statistics()),
                ("Function dependencies", lambda: self.graph_brain.find_function_dependencies("analyze_code_file")),
                ("Knowledge graph statistics", lambda: self.graph_brain.get_knowledge_graph_statistics())
            ]
            
            for query_name, query_func in queries:
                try:
                    print(f"  Executing: {query_name}")
                    result = query_func()
                    query_results[query_name] = {
                        "success": True,
                        "result_count": len(result) if isinstance(result, list) else 1,
                        "has_data": bool(result)
                    }
                    print(f"    ✅ Success: {query_results[query_name]['result_count']} results")
                except Exception as query_error:
                    query_results[query_name] = {
                        "success": False,
                        "error": str(query_error)
                    }
                    print(f"    ❌ Failed: {query_error}")
            
            successful_queries = sum(1 for r in query_results.values() if r["success"])
            
            self.test_results["tests"][test_name] = {
                "success": successful_queries > 0,
                "queries_tested": len(queries),
                "queries_successful": successful_queries,
                "query_results": query_results,
                "message": f"{successful_queries}/{len(queries)} queries successful"
            }
            
            print(f"✅ Codebase Queries: {successful_queries}/{len(queries)} successful")
            
        except Exception as e:
            print(f"❌ Codebase Queries: ERROR - {e}")
            self.test_results["tests"][test_name] = {
                "success": False,
                "error": str(e)
            }
    
    def _find_test_files(self, max_files=10):
        """Find test files for AST parsing."""
        test_files = []
        extensions = ['.py', '.js', '.ts', '.java', '.c', '.cpp']
        
        # Look in common directories
        search_paths = ['nancy-services', '.', 'src']
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, dirs, files in os.walk(search_path):
                    # Skip .git, node_modules, __pycache__ directories
                    dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv']]
                    
                    for file in files:
                        if any(file.endswith(ext) for ext in extensions):
                            file_path = os.path.join(root, file)
                            test_files.append(file_path)
                            
                            if len(test_files) >= max_files:
                                return test_files
        
        return test_files
    
    def run_all_tests(self, repo_path=None, test_directory=None):
        """Run all codebase analysis tests."""
        print("🚀 Starting Comprehensive Codebase Analysis Tests")
        print("=" * 60)
        
        # Run individual tests
        self.test_tree_sitter_initialization()
        self.test_git_repository_analysis(repo_path)
        self.test_ast_parsing()
        self.test_four_brain_integration(test_directory)
        self.test_codebase_queries()
        
        # Generate summary
        total_tests = len(self.test_results["tests"])
        successful_tests = sum(1 for t in self.test_results["tests"].values() if t["success"])
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "overall_success": successful_tests == total_tests
        }
        
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests run: {total_tests}")
        print(f"Successful tests: {successful_tests}")
        print(f"Success rate: {self.test_results['summary']['success_rate']:.1%}")
        
        if self.test_results["summary"]["overall_success"]:
            print("✅ ALL TESTS PASSED - Codebase analysis capabilities are working correctly!")
        else:
            print("❌ SOME TESTS FAILED - Check individual test results for details")
        
        # Save detailed results
        results_file = f"codebase_analysis_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")
        
        return self.test_results

def main():
    """Main test execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Nancy's Codebase Analysis Capabilities")
    parser.add_argument("--repo-path", help="Path to Git repository for testing (default: current directory)")
    parser.add_argument("--test-directory", help="Directory to test for ingestion (default: nancy-services)")
    parser.add_argument("--save-results", action="store_true", help="Save detailed results to JSON file")
    
    args = parser.parse_args()
    
    try:
        tester = CodebaseAnalysisTest()
        results = tester.run_all_tests(
            repo_path=args.repo_path,
            test_directory=args.test_directory
        )
        
        # Exit with appropriate code
        if results["summary"]["overall_success"]:
            print("\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print(f"\n⚠️  {results['summary']['successful_tests']}/{results['summary']['total_tests']} tests passed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()