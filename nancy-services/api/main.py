from fastapi import FastAPI
from api.endpoints import ingest, query

app = FastAPI(title="Project Nancy - Core API")

# Include routers from the endpoints
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(query.router, prefix="/api", tags=["Querying"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Nancy Core API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
