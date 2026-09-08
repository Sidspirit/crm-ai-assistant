import math
import json
import time
import traceback
from google import genai
from models import DraftRequest, DraftResponse

class TimeEstimator:
    @staticmethod
    def calculate_task_time(raw_estimated_minutes: int) -> int:
        if raw_estimated_minutes <= 60:
            return 60
        return math.ceil(raw_estimated_minutes / 30.0) * 30

class LLMService:
    def __init__(self):
        self.client = genai.Client()
        # Актуальные модели согласно последним сообщениям API Google
        self.models_to_try = [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.6-flash"
        ]

    def _call_gemini_with_retry(self, system_instruction: str, prompt: str):
        last_exception = None
        for model in self.models_to_try:
            for attempt in range(2):
                try:
                    chat = self.client.chats.create(
                        model=model,
                        config={
                            "system_instruction": system_instruction,
                            "response_mime_type": "application/json"
                        }
                    )
                    response = chat.send_message(prompt)
                    return response.text
                
                except Exception as e:
                    last_exception = e
                    err_str = str(e)
                    
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        print(f"[LLM WARN] Лимит исчерпан для {model}. Переключаемся на следующую...")
                        break
                    
                    if "503" in err_str or "UNAVAILABLE" in err_str:
                        print(f"[LLM WARN] Сервер {model} перегружен. Попытка {attempt + 1}/2. Ждем 3 сек...")
                        time.sleep(3.0)
                        continue
                    
                    if "404" in err_str or "NOT_FOUND" in err_str:
                        print(f"[LLM WARN] Модель {model} недоступна (404), пропуск...")
                        break
                    
                    break
        
        raise last_exception

    def generate_draft(self, request: DraftRequest) -> DraftResponse:
        messages_text = "\n".join(
            [f"[{m.date}] {m.author}:\n{m.text}" for m in request.messages]
        )
        
        system_instruction = f"""
        Ты — AI-ассистент IT-проект-менеджера в CRM. Проанализируй переписку и сформируй результат для режима: {request.mode.value}.
        Контекст: Заголовок страницы '{request.context.h1_title}', ID темы {request.context.branch_id}.
        
        ПРАВИЛА ДЛЯ РЕЖИМОВ:
        - Если mode == "full_assistant": особое внимание удели полю "thread_summary". Проанализируй всю переписку, выдели все обсуждаемые задачи/темы, укажи их текущий статус (например: "В работе", "Ожидание ответа клиента", "Выполнено", "Обсуждается") и дай краткое ревью по каждой из них.
        
        ПРАВИЛА ДЛЯ task_name:
        Формат: "[Список проектов через пробел] | {request.context.branch_id} | [Отглагольное существительное/Суть задачи]"
        Пример: "cartilox.ru femibion.ru Сайт Найз гелей Хелинорм | {request.context.branch_id} | Обновление акционных баннеров"
        - Извлеки все упоминаемые в задаче сайты, домены или названия брендов/проектов из контекста и сообщений.
        - Перечисли их в самом начале через пробел.
        
        ПРАВИЛА ДЛЯ email_reply_text (Тон и местоимения):
        - Опускай личные местоимения («я», «мы», «он», «она»), если смысл понятен из контекста и формы глагола. Используй их ТОЛЬКО при острой смысловой необходимости (для логического ударения, противопоставления или во избежание двусмысленности).
- Примеры правильного стиля: пиши «Проверил задачу», «Отправляю доступы», «Сделаем к пятнице» ВМЕСТО «Я проверил задачу», «Я отправляю доступы», «Мы сделаем к пятнице».
- Действия менеджера описывай от первого лица, но без местоимения «я».
- Личные действия менеджера (прием в работу, отправка уведомлений) пиши от первого лица единственного числа: "Принял в работу...", "Сообщу вам...".
        - Совместные или командные технические задачи (учет пожеланий, разработка, правки, размещение на сайте) пиши во множественном числе: "Учтем пожелания...", "Внесем правки...", "зальем обновленную версию...".
        - Пример корректного стиля: "Наталья, добрый день! принял в работу правки по баннеру. учтем пожелания по размещению дисклеймера внизу и зальем обновленную версию на сайт. сообщу вам сразу по завершении."
        
        ПРАВИЛА ДЛЯ task_description и thread_summary:
        - ИСПОЛЬЗУЙ ТОЛЬКО ЧИСТЫЙ ТЕКСТ (PLAIN TEXT).
        - КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать Markdown-разметку: никаких звездочек (**bold**), решеток (#), курсива (*italic*).
        - Для списков используй обычную нумерацию (1., 2.) или дефисы (-).
        
        Верни JSON-объект, содержащий:
        - task_name (string)
        - task_description (string)
        - raw_minutes (integer, оценка в минутах, например 60, 90, 120)
        - suggested_executor (string, логин или роль)
        - email_reply_text (string, черновик ответа клиенту)
        - thread_summary (string, детальный аудит всех задач переписки и их статусов для режима full_assistant)
        - parsed_tasks_statuses (list of objects with keys: "task_name" and "status")
        """

        prompt = f"""
        Переписка из CRM:
        {messages_text}
        """

        try:
            response_text = self._call_gemini_with_retry(system_instruction, prompt)
            
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()

            data = json.loads(cleaned_text)
            
        except Exception as e:
            print(f"[LLM ERROR] Ошибка при обработке ответа модели:")
            traceback.print_exc()
            return DraftResponse(
                task_name=f"Ошибка генерации",
                task_description=f"Не удалось распарсить ответ от модели. Детали в консоли бэкенда: {str(e)}"
            )

        calculated_time = None
        if "raw_minutes" in data and isinstance(data["raw_minutes"], (int, float)):
            calculated_time = TimeEstimator.calculate_task_time(int(data["raw_minutes"]))

        return DraftResponse(
            task_name=data.get("task_name"),
            task_description=data.get("task_description"),
            task_time_minutes=calculated_time,
            task_executor=data.get("suggested_executor"),
            email_reply_text=data.get("email_reply_text"),
            thread_summary=data.get("thread_summary"),
            parsed_tasks_statuses=data.get("parsed_tasks_statuses")
        )