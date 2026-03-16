import httpx
from typing import AsyncGenerator

OLLAMA_URL = "http://localhost:11434/api/chat"
# MODEL = "qwen3.5:0.8b"
MODEL = "qwen2.5:0.5b"


async def stream_chat(messages: list[dict]) -> AsyncGenerator[str, None]:
    """
    Stream chat completion from Ollama.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys.
    
    Yields:
        Tokens as they arrive from the model.
    """
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "messages": messages,
                    "stream": True
                },
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"⚠️ Error from Ollama: {response.status_code} - {error_text.decode()}"
                    return
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        import json
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            token = data["message"]["content"]
                            yield token
                    except json.JSONDecodeError:
                        continue
    except httpx.ConnectError:
        yield "⚠️ Ollama is not running. Please start it with ollama serve."
    except httpx.ReadTimeout:
        yield "⚠️ Ollama request timed out."
    except Exception as e:
        yield f"⚠️ Error connecting to Ollama: {str(e)}"
