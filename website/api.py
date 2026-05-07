from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from smartshopper_agent.runtime import run_agent


app = FastAPI(
    title="SmartShopper Assistant API",
    description="Google ADK agent API with Product Recommendation and Common Information tools.",
    version="2.0.0",
)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    user_id: str = "api_user"
    session_id: str | None = None


class ChatResponse(BaseModel):
    query: str
    answer: str
    user_id: str
    session_id: str


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SmartShopper ADK API",
        "tools": ["retrieve_product_recommendation", "retrieve_common_information"],
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query tidak boleh kosong.")

    session_id = request.session_id or str(uuid4())
    answer = await run_agent(
        query=query,
        user_id=request.user_id,
        session_id=session_id,
    )
    return ChatResponse(
        query=query,
        answer=answer,
        user_id=request.user_id,
        session_id=session_id,
    )


@app.post("/recommend", response_model=ChatResponse)
async def recommend(request: ChatRequest):
    return await chat(request)
