from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.rag import RAGService


app = FastAPI(
    title="AI Manufacturing Troubleshooting Copilot",
    description=(
        "Evidence-based AI troubleshooting assistant "
        "for industrial equipment."
    ),
    version="0.1.0",
)


class AskRequest(BaseModel):
    query: str
    top_k: int = 5


class AskResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict]


@app.get("/")
def root():
    return {
        "name": "AI Manufacturing Troubleshooting Copilot",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    if request.top_k < 1 or request.top_k > 10:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 10.",
        )

    try:
        service = RAGService()

        result = service.ask(
            request.query,
            top_k=request.top_k,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
