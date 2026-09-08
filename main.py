from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import DraftRequest, DraftResponse
from services import LLMService

app = FastAPI(title="CRM Assistant API")

# Разрешаем кросс-доменные запросы из CRM
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_service = LLMService()

@app.post("/api/process-thread", response_model=DraftResponse)
async def process_thread(request: DraftRequest):
    """
    Эндпоинт принимает видимые сообщения из CRM и возвращает 
    черновики согласно выбранному режиму.
    """
    response = llm_service.generate_draft(request)
    return response