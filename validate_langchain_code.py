#!/usr/bin/env python3
"""
Code validation script for Nancy's LangChain integration.

This script validates the LangChain orchestrator code structure and dependencies
without requiring a running Docker environment. It performs static analysis
and import validation.
"""

import sys
import importlib
import inspect
from pathlib import Path

def validate_imports():
    """Validate all required imports are available"""
    print("Validating Required Imports")
    print("=" * 50)
    
    required_imports = [
        ("fastapi", "FastAPI web framework"),
        ("pydantic", "Data validation"),
        ("langchain.schema", "LangChain core"),
        ("langchain.tools", "LangChain Tools"),
        ("langchain.agents", "LangChain Agents"),
        ("langchain_ollama", "LangChain Ollama integration"),
    ]
    
    missing_imports = []
    
    for module_name, description in required_imports:
        try:
            importlib.import_module(module_name)
            print(f"OK {module_name:<25} - {description}")
        except ImportError as e:
            print(f"MISSING {module_name:<25} - {description}")
            missing_imports.append((module_name, str(e)))
    
    return len(missing_imports) == 0, missing_imports

def validate_langchain_orchestrator():
    """Validate LangChain orchestrator structure"""
    print("\n🏗️  Validating LangChain Orchestrator Structure")
    print("=" * 50)
    
    orchestrator_path = Path("nancy-services/core/langchain_orchestrator.py")
    
    if not orchestrator_path.exists():
        print("❌ LangChain orchestrator file not found")
        return False
    
    # Read and analyze the file
    with open(orchestrator_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key components
    required_components = [
        ("class VectorBrainTool", "VectorBrain LangChain Tool wrapper"),
        ("class AnalyticalBrainTool", "AnalyticalBrain LangChain Tool wrapper"),
        ("class GraphBrainTool", "GraphBrain LangChain Tool wrapper"),
        ("class LinguisticBrainTool", "LinguisticBrain LangChain Tool wrapper"),
        ("class LangChainOrchestrator", "Main LangChain orchestrator"),
        ("initialize_agent", "LangChain agent initialization"),
        ("def query(self, query_text:", "Main query method"),
        ("def health_check(self", "Health check method"),
    ]
    
    missing_components = []
    
    for component, description in required_components:
        if component in content:
            print(f"✅ {component:<35} - {description}")
        else:
            print(f"❌ {component:<35} - MISSING: {description}")
            missing_components.append(component)
    
    # Check for proper error handling
    error_handling_patterns = [
        "except Exception as e:",
        "raise HTTPException",
        "try:",
        "RuntimeError("
    ]
    
    print(f"\n📋 Error Handling Analysis:")
    for pattern in error_handling_patterns:
        count = content.count(pattern)
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {pattern:<25} - Found {count} instances")
    
    return len(missing_components) == 0

def validate_api_integration():
    """Validate API endpoint integration"""
    print("\n🔗 Validating API Integration")
    print("=" * 50)
    
    api_path = Path("nancy-services/api/endpoints/query.py")
    
    if not api_path.exists():
        print("❌ API query endpoint file not found")
        return False
    
    with open(api_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    integration_checks = [
        ("from core.langchain_orchestrator import LangChainOrchestrator", "LangChain import"),
        ("def get_langchain_orchestrator()", "LangChain factory function"),
        ('orchestrator: str = "langchain"', "Default to LangChain orchestrator"),
        ('if request.orchestrator == "langchain":', "LangChain routing logic"),
        ("get_langchain_orchestrator()", "LangChain orchestrator usage"),
    ]
    
    missing_integrations = []
    
    for check, description in integration_checks:
        if check in content:
            print(f"✅ {description:<40} - Integrated")
        else:
            print(f"❌ {description:<40} - MISSING")
            missing_integrations.append(check)
    
    return len(missing_integrations) == 0

def validate_requirements():
    """Validate requirements.txt includes LangChain"""
    print("\n📦 Validating Requirements")
    print("=" * 50)
    
    req_path = Path("nancy-services/requirements.txt")
    
    if not req_path.exists():
        print("❌ requirements.txt not found")
        return False
    
    with open(req_path, 'r', encoding='utf-8') as f:
        requirements = f.read()
    
    langchain_deps = [
        "langchain",
        "langchain-ollama", 
        "langchain-community"
    ]
    
    missing_deps = []
    
    for dep in langchain_deps:
        if dep in requirements:
            print(f"✅ {dep:<25} - Listed in requirements.txt")
        else:
            print(f"❌ {dep:<25} - MISSING from requirements.txt")
            missing_deps.append(dep)
    
    return len(missing_deps) == 0

def analyze_brain_tool_compatibility():
    """Analyze Brain to Tool conversion"""
    print("\n🧠 Analyzing Brain-to-Tool Architecture")
    print("=" * 50)
    
    orchestrator_path = Path("nancy-services/core/langchain_orchestrator.py")
    
    if not orchestrator_path.exists():
        return False
    
    with open(orchestrator_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check each brain has proper tool wrapper
    brain_mappings = [
        ("VectorBrainTool", "vector_brain", "Semantic search capabilities"),
        ("AnalyticalBrainTool", "analytical_brain", "Metadata and analytical queries"),
        ("GraphBrainTool", "graph_brain", "Relationship and author queries"),
        ("LinguisticBrainTool", "llm_client", "Language processing and synthesis")
    ]
    
    compatibility_score = 0
    
    for tool_class, brain_attr, description in brain_mappings:
        if tool_class in content and brain_attr in content:
            print(f"✅ {tool_class:<20} ↔ {brain_attr:<20} - {description}")
            compatibility_score += 1
        else:
            print(f"❌ {tool_class:<20} ↔ {brain_attr:<20} - INCOMPLETE: {description}")
    
    print(f"\nCompatibility Score: {compatibility_score}/{len(brain_mappings)} ({compatibility_score/len(brain_mappings)*100:.0f}%)")
    
    return compatibility_score == len(brain_mappings)

def generate_migration_report():
    """Generate migration status report"""
    print("\n📊 Migration Status Report")
    print("=" * 50)
    
    # Run all validations
    imports_ok, missing_imports = validate_imports()
    structure_ok = validate_langchain_orchestrator()
    integration_ok = validate_api_integration()
    requirements_ok = validate_requirements()
    compatibility_ok = analyze_brain_tool_compatibility()
    
    # Calculate overall score
    checks = [imports_ok, structure_ok, integration_ok, requirements_ok, compatibility_ok]
    passed_checks = sum(checks)
    total_checks = len(checks)
    
    print(f"\n🎯 OVERALL MIGRATION STATUS")
    print(f"Passed Checks: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.0f}%)")
    
    if passed_checks == total_checks:
        status = "✅ READY FOR TESTING"
        recommendation = "LangChain integration appears complete. Proceed with runtime testing."
    elif passed_checks >= total_checks * 0.8:
        status = "⚠️  MOSTLY READY"
        recommendation = "Minor issues detected. Review missing components before testing."
    else:
        status = "❌ NOT READY"
        recommendation = "Significant issues found. Complete missing components before testing."
    
    print(f"Status: {status}")
    print(f"Recommendation: {recommendation}")
    
    if missing_imports:
        print(f"\n🔧 REQUIRED ACTIONS:")
        print("1. Install missing dependencies:")
        for module, error in missing_imports:
            print(f"   pip install {module}")
    
    return {
        "overall_status": status,
        "passed_checks": passed_checks,
        "total_checks": total_checks,
        "recommendation": recommendation,
        "missing_imports": missing_imports
    }

def main():
    """Run complete validation"""
    print("Nancy LangChain Integration Validation")
    print("=" * 60)
    print("This script validates the LangChain integration code structure")
    print("without requiring a running Docker environment.\n")
    
    # Change to project directory if needed
    project_root = Path(".")
    if not (project_root / "nancy-services").exists():
        print("⚠️  Note: Run this script from the Nancy project root directory")
        return False
    
    # Generate comprehensive report
    report = generate_migration_report()
    
    print(f"\n📝 Validation completed.")
    
    # Exit with appropriate code
    if "READY" in report["overall_status"]:
        return True
    else:
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)