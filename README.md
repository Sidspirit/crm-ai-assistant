# 🚀 ITSoft CRM2 AI Assistant

An intelligent assistant for automating request processing and task management within a CRM system. The project is a full-stack solution featuring a lightweight browser injector (Tampermonkey Userscript) and a resilient FastAPI backend integrated with the Google Gemini API.

---

## 🎯 Business Problem Solved

With high volumes of inbound support tickets, managers and engineers spend significant time on routine operations:

1. Extracting key context from long ticket message threads.

2. Manually drafting task titles and descriptions.

3. Estimating effort and assigning executors.

4. Drafting polite, informative replies to clients.

**AI Assistant** reduces initial thread processing time down to a few seconds by automatically parsing context from the CRM DOM tree and generating structured drafts.

---

## 🛠 Tech Stack

* **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic.

* **AI Core:** Google Gemini API `gemini-2.5-flash-lite` / `gemini-1.5-flash-lite`).

* **Frontend / Injected UI:** Vanilla JavaScript, DOM Parser, Tampermonkey API `GM_xmlhttpRequest`).

* **DevOps & Infrastructure:** GitHub, Render (PaaS Web Service), CI/CD via Git Pushes.

* **Security:** Header-based Authentication `X-API-Secret`), Domain-restricted CORS.

---

## 🌟 Key Features

* **✨ Automated Task Generation:** Generates concise task titles, detailed descriptions (DoD / acceptance criteria), suggests time estimates in minutes, and matches appropriate executors.

* **✉️ Response Drafts:** Generates clear, professional, client-oriented email replies based on full thread history.

* **🚀 Full Thread Review:** In-depth analysis of the entire communication history, highlighting task statuses, intermediate agreements, and final responses.

* **🎨 Native UI:** Embedded floating control panel and modal popups with quick copy-to-clipboard functionality directly inside the CRM interface.

---

## 📐 System Architecture

```text

[ CRM Page ([itsoft.ru](http://itsoft.ru)) ]

          │

  (Tampermonkey JS)

  ── DOM Parsing (Extract Messages & Context)

  ── Header Auth (X-API-Secret)

          │

          ▼  HTTPS POST /api/process-thread

[ FastAPI Service on Render ]

          │

  ── Middleware: CORS & Secret Validation

  ── Pydantic Data Parsing

  ── Prompt Engineering & LLM Orchestration

          │

          ▼  Google Gemini API

[ Structured Response (JSON) ]

          │

          ▼  Return to Client

[ Dynamic UI Render / Input Population ]

```

---

## 🔐 Security & Resilience

* **Zero-Leak API Keys:** Gemini API keys are stored exclusively in encrypted Environment Variables on the Render server and are never exposed to client-side JS or public repositories.

* **Unauthorized Traffic Protection:** The backend validates a custom `X-API-Secret` header. Unauthorized requests are immediately rejected with a `401 Unauthorized` status.

* **CORS Restriction:** Cross-Origin Resource Sharing is strictly restricted to target CRM domains.

---

## 🚀 Local Setup & Installation

### 1. Backend (FastAPI)

1. Clone the repository:

   ```bash

   git clone [[https://github.com/Sidspirit/crm-ai-assistant.git](https://github.com/Sidspirit/crm-ai-assistant.git)](https://github.com/Sidspirit/crm-ai-assistant.git](https://github.com/Sidspirit/crm-ai-assistant.git))

   cd crm-ai-assistant

   ```

2. Create and activate a virtual environment:

   ```bash

   python -m venv venv

   # Windows:

   venv\Scripts\activate

   # Linux/macOS:

   source venv/bin/activate

   ```

3. Install dependencies:

   ```bash

   pip install -r requirements.txt

   ```

4. Create a `.env` file in the root directory (or set environment variables):

   ```env

   GEMINI_API_KEY=your_gemini_api_key_here

   CLIENT_API_SECRET=your_super_secret_key_here

   ```

5. Run the development server:

   ```bash

   uvicorn main:app --reload --port 8000

   ```

### 2. Browser Extension (Userscript)

1. Install the **Tampermonkey** browser extension.

2. Create a new script and paste the contents of `script.user.js`.

3. Ensure the `API_SECRET` in the userscript matches the secret configured on your backend.

---

## 📝 License & Usage

Developed for personal workflow automation, self-study, and portfolio demonstration.