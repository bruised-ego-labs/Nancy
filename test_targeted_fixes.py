#!/usr/bin/env python3
"""
Test the specific targeted fixes for LangChain agent issues:
1. Graph brain hallucination fix
2. Anti-loop mechanisms  
3. Better final synthesis
"""

import requests
import json
import time

def test_specific_fix(query, expected_behavior, max_wait=75):
    """Test a specific fix with detailed analysis"""
    print(f"\nTesting: {query}")
    print(f"Expected: {expected_behavior}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/query",
            json={
                "query": query,
                "orchestrator": "langchain",
                "n_results": 3
            },
            timeout=max_wait
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"SUCCESS in {elapsed:.1f}s")
            
            # Analyze agent behavior for specific issues
            tools_used = result.get('tools_used', [])
            agent_steps = result.get('agent_steps', [])
            response_text = result.get('response', '')
            
            print(f"Tools Used: {', '.join(tools_used)} ({len(tools_used)} total)")
            print(f"Agent Steps: {len(agent_steps)}")
            
            # Check for the specific fixes
            analysis = {
                "no_loops": True,
                "no_hallucination": True, 
                "proper_synthesis": True,
                "issues": []
            }
            
            # 1. Check for loops (repeated tool calls)
            tool_calls = []
            for step in agent_steps:
                if step.get('type') == 'action':
                    tool = step.get('tool', '')
                    input_val = step.get('input', '')
                    call_signature = f"{tool}:{input_val}"
                    
                    if call_signature in tool_calls:
                        analysis["no_loops"] = False
                        analysis["issues"].append(f"LOOP DETECTED: {call_signature}")
                    tool_calls.append(call_signature)
            
            # 2. Check for hallucinated inputs (like 'author:John Doe')
            for step in agent_steps:
                if step.get('type') == 'action' and step.get('tool') == 'graph_brain':
                    input_val = step.get('input', '')
                    if 'author:John Doe' in input_val or 'author:Jane' in input_val:
                        analysis["no_hallucination"] = False
                        analysis["issues"].append(f"HALLUCINATION: {input_val}")
            
            # 3. Check for proper synthesis (not outputting agent thoughts)
            if response_text:
                if 'Thought:' in response_text or 'Action:' in response_text or 'Observation:' in response_text:
                    analysis["proper_synthesis"] = False
                    analysis["issues"].append("SYNTHESIS FAILED: Outputting agent thoughts")
            
            # Report analysis
            fixes_working = all([analysis["no_loops"], analysis["no_hallucination"], analysis["proper_synthesis"]])
            
            if fixes_working:
                print("ALL FIXES WORKING CORRECTLY")
            else:
                print("ISSUES DETECTED:")
                for issue in analysis["issues"]:
                    print(f"   - {issue}")
            
            # Show response preview
            if response_text and len(response_text) > 0:
                preview = response_text[:150] + "..." if len(response_text) > 150 else response_text
                print(f"Response: {preview}")
            
            return {
                "success": True,
                "elapsed": elapsed,
                "analysis": analysis,
                "response_preview": response_text[:200] if response_text else "No response"
            }
            
        else:
            print(f"FAILED: HTTP {response.status_code}")
            error = response.json().get('detail', response.text) if response.text else 'No error details'
            print(f"Error: {error}")
            return {"success": False, "error": error, "elapsed": elapsed}
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time  
        print(f"TIMEOUT after {elapsed:.1f}s")
        return {"success": False, "error": "Timeout", "elapsed": elapsed}
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"ERROR: {e}")
        return {"success": False, "error": str(e), "elapsed": elapsed}

def main():
    print("Testing Targeted LangChain Agent Fixes")
    print("=" * 60)
    
    # Wait for container initialization
    print("Waiting for container to initialize...")
    time.sleep(20)
    
    # Test cases designed to trigger the specific issues we fixed
    test_cases = [
        {
            "query": "Who wrote the electrical design review?",
            "expected": "Should use graph_brain with 'authors_list' first, not hallucinate names"
        },
        {
            "query": "What is the operating temperature range?", 
            "expected": "Should use vector_brain once with specific terms, not loop"
        },
        {
            "query": "What are the integration points between electrical and mechanical systems?",
            "expected": "Should provide final answer, not output agent thoughts"
        },
        {
            "query": "Show me recent documents",
            "expected": "Should use analytical_brain with 'recent_docs'"
        }
    ]
    
    results = []
    successful_fixes = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}/{total_tests}")
        
        result = test_specific_fix(test_case["query"], test_case["expected"])
        results.append({
            "test_case": test_case,
            "result": result
        })
        
        if result["success"] and result.get("analysis", {}).get("no_loops") and result.get("analysis", {}).get("no_hallucination") and result.get("analysis", {}).get("proper_synthesis"):
            successful_fixes += 1
    
    # Final summary
    print(f"\n{'='*60}")
    print("TARGETED FIXES SUMMARY")
    print("=" * 60)
    print(f"Tests with all fixes working: {successful_fixes}/{total_tests} ({(successful_fixes/total_tests)*100:.0f}%)")
    
    # Analyze specific fix effectiveness
    loop_issues = sum(1 for r in results if r["result"].get("success") and not r["result"].get("analysis", {}).get("no_loops", True))
    hallucination_issues = sum(1 for r in results if r["result"].get("success") and not r["result"].get("analysis", {}).get("no_hallucination", True))  
    synthesis_issues = sum(1 for r in results if r["result"].get("success") and not r["result"].get("analysis", {}).get("proper_synthesis", True))
    
    print(f"\nFix Effectiveness:")
    print(f"  Anti-loop mechanism: {total_tests - loop_issues}/{total_tests} tests fixed")
    print(f"  Hallucination prevention: {total_tests - hallucination_issues}/{total_tests} tests fixed")
    print(f"  Synthesis improvement: {total_tests - synthesis_issues}/{total_tests} tests fixed")
    
    if successful_fixes >= total_tests * 0.75:
        print(f"\nEXCELLENT: Targeted fixes are working well!")
        print("The agent should now be ready for broader testing.")
    elif successful_fixes >= total_tests * 0.5:
        print(f"\nGOOD: Significant improvement, may need minor tweaks.")
    else:
        print(f"\nNEEDS WORK: Fixes not fully effective, need different approach.")

if __name__ == "__main__":
    main()