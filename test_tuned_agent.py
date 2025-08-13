#!/usr/bin/env python3
"""
Quick test of the tuned LangChain agent to see if it resolves looping issues
"""

import requests
import time

def test_tuned_agent(query, max_wait=90):
    """Test the tuned agent with a specific query"""
    print(f"\nTesting Tuned Agent: {query}")
    print("-" * 50)
    
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
            
            # Analyze agent behavior
            tools_used = result.get('tools_used', [])
            agent_steps = result.get('agent_steps', [])
            
            print(f"Tools Used: {', '.join(tools_used)} ({len(tools_used)} total)")
            print(f"Agent Steps: {len(agent_steps)}")
            
            # Check for loops (same tool used multiple times)
            tool_usage = {}
            for step in agent_steps:
                if step.get('type') == 'action':
                    tool = step.get('tool', 'unknown')
                    tool_usage[tool] = tool_usage.get(tool, 0) + 1
            
            loops_detected = [f"{tool}({count}x)" for tool, count in tool_usage.items() if count > 1]
            if loops_detected:
                print(f"LOOPS DETECTED: {', '.join(loops_detected)}")
            else:
                print("No loops detected - good!")
            
            # Show response
            response_text = result.get('response', '')
            if response_text:
                preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                print(f"Response: {preview}")
                return True
            else:
                print("No response generated")
                return False
                
        else:
            print(f"FAILED: HTTP {response.status_code}")
            error = response.json().get('detail', response.text)
            print(f"Error: {error}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"TIMEOUT after {elapsed:.1f}s")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"ERROR after {elapsed:.1f}s: {e}")
        return False

def main():
    print("Testing Tuned LangChain Agent")
    print("=" * 50)
    
    # Wait for container to initialize
    print("Waiting for container to initialize...")
    time.sleep(15)
    
    # Test queries that previously caused loops
    test_queries = [
        "Who wrote the electrical design review?",  # Should use graph_brain
        "What is the operating temperature?",       # Should use vector_brain
        "Show me recent documents",                 # Should use analytical_brain
        "What documents are available?"             # General query
    ]
    
    successes = 0
    total = len(test_queries)
    
    for query in test_queries:
        if test_tuned_agent(query, 90):
            successes += 1
    
    print("\n" + "=" * 50)
    print("TUNING RESULTS")
    print("=" * 50)
    print(f"Success Rate: {successes}/{total} ({(successes/total)*100:.0f}%)")
    
    if successes >= total * 0.75:
        print("✓ Tuning appears successful - significantly improved reliability")
    elif successes >= total * 0.5:
        print("~ Tuning shows improvement but may need further refinement")
    else:
        print("✗ Tuning did not resolve the main issues - need different approach")

if __name__ == "__main__":
    main()