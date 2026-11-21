# CallMissed AI Agent API

A Python backend prototype built with **FastAPI** that wraps the CallMissed AI API. This project exposes three core endpoints: stateful chat streaming, image generation, and vision analysis. 

As a bonus for easy evaluation, this project includes a lightweight, interactive HTML/JS frontend served directly from the root endpoint, allowing for instant testing of all features without external tools.

## 🚀 Core Features
- **Chat (`POST /chat`)**: Streams AI responses using Server-Sent Events (SSE). Includes stateful conversation memory via session tracking.
- **Image Generation (`POST /image`)**: Generates images from text prompts with robust error handling and loading states.
- **Vision (`POST /vision`)**: Analyzes uploaded images (multipart/form-data) combined with text queries.
- **Interactive UI**: A Vanilla JS/HTML frontend to interact with all three endpoints cleanly.
- **Unit Tested**: Core routing, validation, and mocked API calls are covered using `pytest`.

## 📦 Models Used
- **Chat & Vision:** `kimi-k2.7-code`
- **Image Generation:** `flux-2-klein-9b`

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- A CallMissed API key. See [docs.callmissed.com](https://docs.callmissed.com).

### 2. Install Dependencies
Clone the repository and install the required packages:

```bash
git clone https://github.com/smmsa1912/callmissed-ai-agent.git
cd callmissed-ai-agent
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory (you can copy `.env.example`). It must contain your API key, the base URL, and the model mapping:

```env
CALLMISSED_API_KEY="cm_your_api_key_here"
BASE_URL="https://api.callmissed.com/v1"
MODELS='{
    "chat":"kimi-k2.7-code",
    "vision":"kimi-k2.7-code",
    "image":"flux-2-klein-9b"
}'
```

### 4. Run the Server
Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```
- **Frontend UI:** Open your browser to `http://127.0.0.1:8000/` to test the API via the built-in interface.
- **Swagger Docs:** Available at `http://127.0.0.1:8000/docs`

### 5. Run Tests
Execute the test suite using pytest:

```bash
pytest test_main.py -v
```

---

## 📖 API Endpoints (cURL Examples)

### 1. Chat (Streaming with Memory)
`POST /chat`
Accepts a message and streams the response back via Server-Sent Events (SSE). To utilize conversation memory, include the `session_id` returned from your initial request.

**Start a new session:**
```bash
curl -N -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, my favorite color is blue."}'
```
*(Look for `[SESSION_ID]your-uuid-here` at the end of the stream)*

**Continue session (tests memory):**
```bash
curl -N -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-uuid-here", "message": "What is my favorite color?"}'
```

### 2. Image Generation
`POST /image`
Generates an image based on a text prompt.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/image \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A futuristic city skyline at sunset, cyberpunk style, digital art"}'
```

### 3. Vision Analysis
`POST /vision`
Analyzes an uploaded image based on a provided question.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/vision \
  -F "question=What is in this image?" \
  -F "image=@/path/to/your/image.jpg"
```

---

## 🏗️ Architecture & Design Decisions

- **Separation of Concerns:** The CallMissed API client configuration (`client.py`) is isolated from the routing and schema logic (`main.py`) to keep the codebase modular.
- **Robust Error Handling:** Upstream CallMissed API errors (e.g., 402, 429) are caught in the service layer and raised as generic `HTTPException`s. This is intended to avoid returning raw upstream errors to clients; review logging and exception paths before production use.
- **Configuration Management:** Uses `pydantic-settings` to safely validate and parse environment variables, including parsing a JSON string for model definitions to prevent hardcoding.
- **Stateful Memory:** Implemented an in-memory dictionary to track `session_id`s, allowing the LLM to maintain conversation context seamlessly.

## ⚖️ Trade-offs

- **In-Memory Storage vs. Database:** I chose to use an in-memory Python dictionary for conversation persistence. 
  - *Pros:* It is incredibly fast, requires zero setup for the evaluator, and reduces external dependencies.
  - *Cons:* State is lost if the server restarts. In a real production environment, this would not scale horizontally across multiple worker nodes.
- **Base64 vs Cloud Storage for Vision:** I opted to encode uploaded images to base64 in memory to pass to the Vision model.
  - *Pros:* Avoids needing an S3 bucket or managing local file cleanup.
  - *Cons:* Very large images could cause memory bloat on the server. 

## 🔮 What I'd Do Next (Future Improvements)

If I had more time to expand this into a true production service, I would add:
1. **Persistent Storage:** Swap the in-memory chat history for PostgreSQL or Redis to ensure horizontal scalability and persistence.
2. **Authentication & Rate Limiting:** Add a lightweight API key middleware and token-bucket rate limiting to protect the endpoints from abuse.
3. **Dockerization:** Add a `Dockerfile` and `docker-compose.yml` to improve reproducibility across development environments.
4. **Image Compression:** Add a utility function to compress large image uploads on the `/vision` endpoint before converting them to base64 to save bandwidth and API limits.

## 🤖 AI Usage Disclosure
AI tools (Gemini) were utilized during the development of this assignment for:
- Scaffolding the initial FastAPI boilerplate and Pydantic validation models.
- Generating the CSS, Animations, and Fetch API logic for the interactive `index.html` frontend UI.
- Generating mock structures for the `pytest` suite.
