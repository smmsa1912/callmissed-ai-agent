from fastapi import FastAPI, HTTPException,  File, UploadFile, Form
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import openai
import json
import uuid
import base64

from client import cm_client, settings

app = FastAPI()


@app.get("/")
async def serve_index():
    return FileResponse("index.html")


class Message(BaseModel):
    role: str
    content: str

chat_sessions: dict[str, list[dict]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    if session_id not in chat_sessions:
        chat_sessions[session_id] = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]

    chat_sessions[session_id].append({"role": "user", "content": request.message})

    async def event_generator():
        try:
            stream = await cm_client.chat.completions.create(
                model=settings.MODELS["chat"],
                messages=chat_sessions[session_id],
                stream=True
            )

            assistant_reply = ""
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    assistant_reply += content
                    yield f"data: {content}\n\n"

            chat_sessions[session_id].append({"role": "assistant", "content": assistant_reply})
            yield f"data: [SESSION_ID]{session_id}\n\n"
            yield "data: [DONE]\n\n"

        except openai.APIStatusError as e:
            error_msg = json.dumps({"error": f"Upstream API Error: {e.status_code}"})
            yield f"data: {error_msg}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_msg = json.dumps({"error": "Internal server error occurred."})
            yield f"data: {error_msg}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


class ImageRequest(BaseModel):
    prompt: str

@app.post("/image")
async def generate_image(request: ImageRequest):
    try:
        response = await cm_client.images.generate(
            model=settings.MODELS["image"],
            prompt=request.prompt,
            n=1
        )
        image_url = response.data[0].url
        return {"url": image_url}

    except openai.APIStatusError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=f"Upstream API Error: {e.status_code}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred while generating the image."
        )


@app.post("/vision")
async def vision_endpoint(
        question: str = Form(...),
        image: UploadFile = File(...)
):
    try:
        image_bytes = await image.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        mime_type = image.content_type or "image/jpeg"
        image_data_url = f"data:{mime_type};base64,{base64_image}"

        response = await cm_client.chat.completions.create(
            model=settings.MODELS["vision"],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": image_data_url}}
                    ]
                }
            ]
        )

        return {"answer": response.choices[0].message.content}

    except openai.APIStatusError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=f"Upstream API Error: {e.status_code}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred while analyzing the image."
        )