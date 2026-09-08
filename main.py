import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import DraftRequest, DraftResponse
from services import LLMService

app = FastAPI(title="CRM Assistant API")

# Ограничиваем CORS (разрешаем запросы только с доменов CRM)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://*.itsoft.ru", "https://itsoft.ru"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Секретный ключ для защиты от сторонних запросов
API_SECRET = os.getenv("CLIENT_API_SECRET", "my_super_secret_key_123")

llm_service = LLMService()

@app.post("/api/process-thread", response_model=DraftResponse)
async def process_thread(
    request: DraftRequest, 
    x_api_secret: str = Header(None)
):
    """
    Эндпоинт принимает видимые сообщения из CRM и возвращает 
    черновики согласно выбранному режиму.
    """
    if x_api_secret != API_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Secret")
        
    response = llm_service.generate_draft(request)
    return response