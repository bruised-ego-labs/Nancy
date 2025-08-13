#!/usr/bin/env python3
"""
Simple validation script for Nancy's LangChain integration.
"""

import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"OK - {description}: {file_path}")
        return True
    else:
        print(f"MISSING - {description}: {file_path}")
        return False

def check_content_in_file(file_path, content, description):
    """Check if content exists in file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        if content in file_content:
            print(f"OK - {description}")
            return True
        else:
            print(f"MISSING - {description}")
            return False
    except Exception as e:
        print(f"ERROR - Could not check {description}: {e}")
        return False

def main():
    print("Nancy LangChain Integration Validation")
    print("=" * 50)
    
    checks = []
    
    # 1. Check core files exist
    print("\n1. Core Files Check:")
    checks.append(check_file_exists("nancy-services/core/langchain_orchestrator.py", "LangChain Orchestrator"))
    checks.append(check_file_exists("nancy-services/api/endpoints/query.py", "Query API Endpoint"))
    checks.append(check_file_exists("nancy-services/requirements.txt", "Requirements File"))
    
    # 2. Check LangChain orchestrator structure
    print("\n2. LangChain Orchestrator Structure:")
    orchestrator_file = "nancy-services/core/langchain_orchestrator.py"
    if Path(orchestrator_file).exists():
        checks.append(check_content_in_file(orchestrator_file, "class VectorBrainTool", "VectorBrain Tool Class"))
        checks.append(check_content_in_file(orchestrator_file, "class AnalyticalBrainTool", "AnalyticalBrain Tool Class"))
        checks.append(check_content_in_file(orchestrator_file, "class GraphBrainTool", "GraphBrain Tool Class"))
        checks.append(check_content_in_file(orchestrator_file, "class LinguisticBrainTool", "LinguisticBrain Tool Class"))
        checks.append(check_content_in_file(orchestrator_file, "class LangChainOrchestrator", "Main Orchestrator Class"))
        checks.append(check_content_in_file(orchestrator_file, "initialize_agent", "LangChain Agent Initialization"))
    
    # 3. Check API integration
    print("\n3. API Integration:")
    api_file = "nancy-services/api/endpoints/query.py"
    if Path(api_file).exists():
        checks.append(check_content_in_file(api_file, "from core.langchain_orchestrator import LangChainOrchestrator", "LangChain Import"))
        checks.append(check_content_in_file(api_file, "def get_langchain_orchestrator", "LangChain Factory Function"))
        checks.append(check_content_in_file(api_file, 'orchestrator: str = "langchain"', "Default Orchestrator"))
        checks.append(check_content_in_file(api_file, 'if request.orchestrator == "langchain":', "LangChain Routing"))
    
    # 4. Check requirements
    print("\n4. Dependencies:")
    req_file = "nancy-services/requirements.txt"
    if Path(req_file).exists():
        checks.append(check_content_in_file(req_file, "langchain", "LangChain Dependency"))
        checks.append(check_content_in_file(req_file, "langchain-ollama", "LangChain Ollama"))
        checks.append(check_content_in_file(req_file, "langchain-community", "LangChain Community"))
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    print(f"Passed: {passed}/{total} ({percentage:.0f}%)")
    
    if percentage == 100:
        print("STATUS: READY FOR TESTING")
        print("All components appear to be properly integrated.")
    elif percentage >= 80:
        print("STATUS: MOSTLY READY")
        print("Minor issues detected. Review missing components.")
    else:
        print("STATUS: NOT READY")
        print("Significant issues found. Complete implementation needed.")
    
    return percentage == 100

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)