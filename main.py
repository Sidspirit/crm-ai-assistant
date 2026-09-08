from fastapi import FastAPI
from models import DraftRequest, DraftResponse
from services import LLMService

app = FastAPI(title="CRM Assistant API")
llm_service = LLMService()

@app.post("/api/process-thread", response_model=DraftResponse)
async def process_thread(request: DraftRequest):
    """
    Эндпоинт принимает видимые сообщения из CRM и возвращает 
    черновики согласно выбранному режиму.
    """
    response = llm_service.generate_draft(request)
    return response

# Запуск локально: uvicorn main:app --reload --port 8000