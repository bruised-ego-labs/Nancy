from functools import lru_cache
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.query_orchestrator import QueryOrchestrator
from core.enhanced_query_orchestrator import EnhancedQueryOrchestrator
from core.intelligent_query_orchestrator import IntelligentQueryOrchestrator
from core.langchain_orchestrator import LangChainOrchestrator

router = APIRouter()

# NEW: LangChain-integrated orchestrator (RECOMMENDED)
@lru_cache()
def get_langchain_orchestrator():
    print("Creating LangChain-integrated Nancy Orchestrator...")
    return LangChainOrchestrator()

# Intelligent orchestrator with true LLM-based processing
@lru_cache()
def get_intelligent_query_orchestrator():
    print("Creating Intelligent QueryOrchestrator instance (LLM-based)...")
    return IntelligentQueryOrchestrator()

# Enhanced orchestrator with intelligent routing (rule-based)
@lru_cache()
def get_enhanced_query_orchestrator():
    print("Creating Enhanced QueryOrchestrator instance...")
    return EnhancedQueryOrchestrator()

# Legacy orchestrator for compatibility
@lru_cache()
def get_query_orchestrator():
    print("Creating Legacy QueryOrchestrator instance...")
    return QueryOrchestrator()

class QueryRequest(BaseModel):
    query: str
    n_results: int = 5
    orchestrator: str = "langchain"  # Default to LangChain-integrated (RECOMMENDED)

@router.post("/query")
def query_data(request: QueryRequest):
    """
    Receives a user query and processes it with conditional orchestrator loading.
    
    Orchestrator options:
    - "langchain" (default): LangChain-integrated Nancy with professional agent orchestration
    - "intelligent": Uses LLM for query analysis and response synthesis
    - "enhanced": Uses rule-based pattern matching (no LLM)
    - "legacy": Basic orchestration for compatibility
    """
    try:
        # Conditional orchestrator loading - only create what we need!
        if request.orchestrator == "langchain":
            orchestrator = get_langchain_orchestrator()
            result = orchestrator.query(request.query, request.n_results)
        elif request.orchestrator == "intelligent":
            orchestrator = get_intelligent_query_orchestrator()
            result = orchestrator.query(request.query, request.n_results)
        elif request.orchestrator == "enhanced":
            orchestrator = get_enhanced_query_orchestrator()
            result = orchestrator.query(request.query, request.n_results)
        elif request.orchestrator == "legacy":
            orchestrator = get_query_orchestrator()
            result = orchestrator.query(request.query, request.n_results)
        else:
            raise ValueError(f"Unknown orchestrator type: {request.orchestrator}")
            
        return result
    except Exception as e:
        # Clear error reporting with orchestrator context
        error_details = {
            "error": str(e),
            "query": request.query,
            "orchestrator_type": request.orchestrator,
            "message": "Query processing failed. Check that local LLM is functional for intelligent mode."
        }
        raise HTTPException(status_code=500, detail=error_details)

class GraphQueryRequest(BaseModel):
    author_name: str
    use_enhanced: bool = True

@router.post("/query/graph")
def query_graph_data(
    request: GraphQueryRequest,
    enhanced_orchestrator: EnhancedQueryOrchestrator = Depends(get_enhanced_query_orchestrator),
    legacy_orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
):
    """
    Receives a graph query for author documents, passes it to the appropriate QueryOrchestrator,
    and returns the results.
    """
    try:
        if request.use_enhanced:
            result = enhanced_orchestrator.query_authored_documents(request.author_name)
        else:
            result = legacy_orchestrator.query_authored_documents(request.author_name)
        return result
    except Exception as e:
        # Enhanced error handling
        error_details = {
            "error": str(e),
            "author_name": request.author_name,
            "orchestrator_type": "enhanced" if request.use_enhanced else "legacy"
        }
        raise HTTPException(status_code=500, detail=error_details)

# New endpoint for testing different query strategies
@router.post("/query/test-strategy")
def test_query_strategy(
    request: QueryRequest,
    enhanced_orchestrator: EnhancedQueryOrchestrator = Depends(get_enhanced_query_orchestrator)
):
    """
    Test endpoint that shows what strategy would be used for a query without executing it.
    """
    try:
        intent = enhanced_orchestrator.query_analyzer.analyze_query_intent(request.query)
        return {
            "query": request.query,
            "predicted_strategy": intent,
            "description": f"This query would use the {intent['primary_brain']} brain first with {intent['type']} strategy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check(
    intelligent_orchestrator: IntelligentQueryOrchestrator = Depends(get_intelligent_query_orchestrator)
):
    """
    Check the health of all four brains in Nancy's architecture.
    Especially important to verify LLM functionality.
    """
    try:
        health_status = intelligent_orchestrator.health_check()
        
        if health_status["overall"] == "unhealthy":
            raise HTTPException(
                status_code=503, 
                detail={
                    "message": "Nancy system is unhealthy - LLM required for intelligent processing",
                    "health": health_status
                }
            )
        elif health_status["overall"] == "degraded":
            # Return 200 but with warning
            return {
                "status": "degraded",
                "message": "Some brains are unhealthy but LLM is functional",
                "health": health_status
            }
        else:
            return {
                "status": "healthy", 
                "message": "All four brains operational - ready for intelligent query processing",
                "health": health_status
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": str(e),
            "message": "Health check failed - system may be misconfigured"
        })
