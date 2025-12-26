import requests

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"

def generate_with_ollama(prompt: str, model: str = "gemma2:2b") -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
