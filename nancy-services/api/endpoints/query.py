from functools import lru_cache
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.query_orchestrator import QueryOrchestrator
from core.enhanced_query_orchestrator import EnhancedQueryOrchestrator

router = APIRouter()

# Enhanced orchestrator with intelligent routing
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
    use_enhanced: bool = True  # Default to enhanced orchestrator

@router.post("/query")
def query_data(
    request: QueryRequest,
    enhanced_orchestrator: EnhancedQueryOrchestrator = Depends(get_enhanced_query_orchestrator),
    legacy_orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
):
    """
    Receives a user query, passes it to the appropriate QueryOrchestrator,
    and returns the results with intelligent database routing.
    """
    try:
        if request.use_enhanced:
            result = enhanced_orchestrator.query(request.query, request.n_results)
        else:
            result = legacy_orchestrator.query(request.query, request.n_results)
        return result
    except Exception as e:
        # Enhanced error handling with more context
        error_details = {
            "error": str(e),
            "query": request.query,
            "orchestrator_type": "enhanced" if request.use_enhanced else "legacy"
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
