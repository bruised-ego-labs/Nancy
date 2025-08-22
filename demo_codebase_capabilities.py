#!/usr/bin/env python3
"""
Demonstration script for Nancy's Enhanced Codebase Ingestion Capabilities.
Showcases the AST parsing, Git integration, and Four-Brain Architecture features
implemented to meet the requirements from gemini.log lines 680-695.

This demo shows how Nancy can now understand and analyze entire source code
repositories with deep insights into code structure and collaboration patterns.
"""

import os
import sys
from pathlib import Path

# Add nancy-services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nancy-services'))

try:
    from core.ingestion import CodebaseIngestionService, GitAnalysisService
    from core.knowledge_graph import GraphBrain
except ImportError as e:
    print(f"Import error: {e}")
    print("Please run this from the Nancy project root directory")
    sys.exit(1)

def demo_header():
    """Print demonstration header."""
    print("🎯 NANCY CODEBASE ANALYSIS CAPABILITIES DEMO")
    print("=" * 55)
    print("This demo showcases Nancy's new ability to understand")
    print("and analyze entire source code repositories with:")
    print("")
    print("✨ AST parsing for multiple programming languages")
    print("🔍 Git integration for authorship and collaboration")
    print("🧠 Four-Brain Architecture for deep code understanding")
    print("📊 Advanced relationship extraction and queries")
    print("")
    print("=" * 55)
    print("")

def demo_ast_parsing():
    """Demonstrate AST parsing capabilities."""
    print("🌳 AST PARSING DEMONSTRATION")
    print("-" * 30)
    
    codebase_service = CodebaseIngestionService()
    
    # Show initialized parsers
    print(f"Initialized tree-sitter parsers: {list(codebase_service.parsers.keys())}")
    print("")
    
    # Find a Python file to analyze
    python_files = []
    for root, dirs, files in os.walk("nancy-services"):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
                if len(python_files) >= 2:
                    break
        if len(python_files) >= 2:
            break
    
    if python_files:
        for file_path in python_files[:2]:
            print(f"📄 Analyzing: {file_path}")
            try:
                analysis = codebase_service.analyze_code_file(file_path)
                if "error" not in analysis:
                    ast_data = analysis.get("ast_analysis", {})
                    print(f"  Language: {ast_data.get('language', 'unknown')}")
                    print(f"  Lines of code: {ast_data.get('lines_of_code', 0)}")
                    print(f"  Functions: {ast_data.get('total_functions', 0)}")
                    print(f"  Classes: {ast_data.get('total_classes', 0)}")
                    print(f"  Imports: {ast_data.get('total_imports', 0)}")
                    
                    # Show some function names
                    functions = ast_data.get('functions', [])
                    if functions:
                        print(f"  Sample functions: {', '.join(f['name'] for f in functions[:3])}")
                    print("")
                else:
                    print(f"  ❌ Analysis failed: {analysis['error']}")
                    print("")
            except Exception as e:
                print(f"  ❌ Exception: {e}")
                print("")
    else:
        print("No Python files found for demonstration")
        print("")

def demo_git_integration():
    """Demonstrate Git integration capabilities."""
    print("🔗 GIT INTEGRATION DEMONSTRATION") 
    print("-" * 33)
    
    git_service = GitAnalysisService()
    
    # Try to initialize repository
    if git_service.initialize_repository("."):
        print("✅ Git repository detected and initialized")
        
        # Get repository metadata
        repo_metadata = git_service.get_repository_metadata()
        if not repo_metadata.get('error'):
            print(f"📊 Repository Statistics:")
            print(f"  Current branch: {repo_metadata.get('current_branch', 'unknown')}")
            print(f"  Total commits: {repo_metadata.get('total_commits', 0)}")
            print(f"  Total contributors: {repo_metadata.get('total_contributors', 0)}")
            print(f"  Remote branches: {len(repo_metadata.get('branches', []))}")
            
            # Show top contributors
            contributors = repo_metadata.get('contributors', [])
            if contributors:
                print(f"  Top contributors:")
                for i, contributor in enumerate(contributors[:3]):
                    print(f"    {i+1}. {contributor.get('name', 'Unknown')} ({contributor.get('commits', 0)} commits)")
            print("")
        else:
            print(f"❌ Could not get repository metadata: {repo_metadata.get('error')}")
            print("")
    else:
        print("❌ Not a Git repository or Git not available")
        print("")

def demo_four_brain_integration():
    """Demonstrate Four-Brain Architecture integration."""
    print("🧠 FOUR-BRAIN ARCHITECTURE DEMO")
    print("-" * 32)
    
    graph_brain = GraphBrain()
    
    try:
        # Test codebase statistics
        print("📈 Testing Codebase Statistics Query...")
        stats = graph_brain.get_codebase_statistics()
        
        if stats:
            print("✅ Successfully connected to Graph Brain")
            
            # Show language distribution
            lang_dist = stats.get('language_distribution', [])
            if lang_dist:
                print("  Programming languages found:")
                for lang_info in lang_dist[:5]:  # Top 5 languages
                    lang = lang_info.get('language', 'unknown')
                    files = lang_info.get('file_count', 0)
                    lines = lang_info.get('total_lines', 0)
                    print(f"    • {lang}: {files} files, {lines} lines")
            
            # Show entity counts
            entities = stats.get('entity_counts', {})
            if entities:
                print(f"  Code entities detected:")
                print(f"    • Files: {entities.get('total_files', 0)}")
                print(f"    • Functions: {entities.get('total_functions', 0)}")
                print(f"    • Classes: {entities.get('total_classes', 0)}")
            
            print("")
        else:
            print("⚠️  No codebase data found - run ingestion first")
            print("")
            
    except Exception as e:
        print(f"❌ Error querying Graph Brain: {e}")
        print("   (This is expected if no code has been ingested yet)")
        print("")

def demo_query_capabilities():
    """Demonstrate advanced query capabilities."""
    print("🔍 ADVANCED QUERY CAPABILITIES")
    print("-" * 30)
    
    print("Nancy can now answer complex questions about codebases:")
    print("")
    
    queries = [
        "❓ 'Who wrote the authentication module?'",
        "   → Uses Git blame analysis + AST parsing to identify authors",
        "",
        "❓ 'What functions handle error logging?'", 
        "   → Searches function names, docstrings, and call graphs",
        "",
        "❓ 'Which components depend on the database layer?'",
        "   → Analyzes import relationships and dependency graphs",
        "",
        "❓ 'Show me the class hierarchy for API components'",
        "   → Maps inheritance relationships from AST analysis",
        "",
        "❓ 'Which files have the most complex functions?'",
        "   → Combines AST metrics with code complexity analysis",
        "",
        "❓ 'Who are the Python experts on the team?'",
        "   → Aggregates contribution data by language and complexity"
    ]
    
    for query in queries:
        print(query)
    
    print("")
    print("🎯 These queries work through Nancy's Four-Brain Architecture:")
    print("   • Vector Brain: Semantic search in code comments/docs")
    print("   • Analytical Brain: Code metrics and statistics")
    print("   • Graph Brain: Relationships and dependencies") 
    print("   • Linguistic Brain: Natural language query processing")
    print("")

def demo_implementation_highlights():
    """Show key implementation highlights."""
    print("⚙️  IMPLEMENTATION HIGHLIGHTS")
    print("-" * 29)
    
    highlights = [
        "🌳 Tree-sitter Integration:",
        "   • Multi-language AST parsing (Python, JS, Java, C/C++)",
        "   • Function/class extraction with line numbers and metadata",
        "   • Import/dependency relationship mapping",
        "",
        "🔗 Git Integration:",
        "   • Repository metadata extraction (branches, contributors)",
        "   • File-level authorship analysis with blame data",
        "   • Commit history and collaboration pattern tracking",
        "",
        "🧠 Graph Brain Enhancements:",
        "   • CodeFile, Function, Class, Module node types",
        "   • CONTAINS, INHERITS_FROM, CALLS, IMPORTS relationships",
        "   • Code expert identification and expertise scoring",
        "",
        "📊 Enhanced Analytics:",
        "   • Code complexity metrics and statistics",
        "   • Language distribution and contribution tracking",
        "   • Function call analysis and dependency mapping",
        "",
        "🔄 Directory Integration:",
        "   • Automatic code file detection and processing",
        "   • Fallback to text processing when AST fails",
        "   • Batch processing with progress tracking"
    ]
    
    for highlight in highlights:
        print(highlight)
    
    print("")

def main():
    """Main demonstration function."""
    demo_header()
    
    try:
        demo_ast_parsing()
        demo_git_integration()
        demo_four_brain_integration()
        demo_query_capabilities()
        demo_implementation_highlights()
        
        print("🚀 READY TO ANALYZE CODEBASES!")
        print("-" * 30)
        print("Nancy is now equipped to understand entire source code")
        print("repositories and provide intelligent insights about:")
        print("• Code structure and organization")
        print("• Developer expertise and contributions") 
        print("• Component dependencies and relationships")
        print("• Technical debt and complexity patterns")
        print("")
        print("To start analyzing a codebase:")
        print("1. Run: python test_codebase_analysis.py")
        print("2. Or use: ./test_codebase_integration.ps1")
        print("3. Or integrate with Nancy's directory ingestion API")
        print("")
        print("✨ Happy coding with Nancy's enhanced capabilities!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()