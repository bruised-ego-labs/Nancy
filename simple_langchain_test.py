#!/usr/bin/env python3
"""
Simple test to demonstrate LangChain agent reasoning vs traditional orchestrators
"""

import requests
import json

def test_query(orchestrator, query, timeout=60):
    """Test a single query with timing"""
    import time
    
    print(f"\n--- Testing {orchestrator.upper()} ---")
    print(f"Query: {query}")
    
    start = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/query",
            json={"query": query, "orchestrator": orchestrator, "n_results": 3},
            timeout=timeout
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS in {elapsed:.1f}s")
            
            if orchestrator == "langchain":
                tools = result.get('tools_used', [])
                steps = len(result.get('agent_steps', []))
                print(f"LangChain Agent: {steps} steps, used tools: {', '.join(tools)}")
                
            elif orchestrator == "intelligent":
                intent = result.get('intent_analysis', {}).get('type', 'unknown')
                brains = result.get('brains_used', [])
                print(f"Intelligent: {intent} intent, brains: {', '.join(brains)}")
            
            response_text = result.get('response', result.get('synthesized_response', ''))
            print(f"Response preview: {response_text[:150]}...")
            
        else:
            print(f"FAILED: HTTP {response.status_code}")
            print(f"Error: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"TIMEOUT after {elapsed:.1f}s")
    except Exception as e:
        elapsed = time.time() - start
        print(f"ERROR after {elapsed:.1f}s: {e}")

def main():
    print("Simple LangChain Agent Reasoning Demonstration")
    print("=" * 55)
    
    # Simple test query
    query = "What documents are available?"
    
    # Test each orchestrator
    orchestrators = ["enhanced", "intelligent", "langchain"] 
    
    for orchestrator in orchestrators:
        test_query(orchestrator, query, timeout=90)
    
    print(f"\n" + "=" * 55)
    print("EXPLANATION:")
    print("- Enhanced: Rule-based routing, fastest")
    print("- Intelligent: LLM intent analysis + synthesis") 
    print("- LangChain: Agent reasoning with ReAct pattern")
    print("  * Thinks about what tools to use")
    print("  * Uses tools sequentially")
    print("  * Reasons about results")
    print("  * Synthesizes final answer")

if __name__ == "__main__":
    main()