from functools import lru_cache
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from core.query_orchestrator import QueryOrchestrator

router = APIRouter()

# This function will be called once, and its result will be cached for all subsequent calls.
@lru_cache()
def get_query_orchestrator():
    print("Creating QueryOrchestrator instance...")
    return QueryOrchestrator()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
def query_data(
    request: QueryRequest,
    orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
):
    """
    Receives a user query, passes it to the QueryOrchestrator,
    and returns the results.
    """
    try:
        result = orchestrator.query(request.query)
        return result
    except Exception as e:
        # Basic error handling
        raise HTTPException(status_code=500, detail=str(e))
