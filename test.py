import requests

URL = "http://localhost:11434/v1/chat/completions"

payload = {
    "model": "gemma2:2b",
    "messages": [
        {"role": "user", "content": "hello"}
    ]
}

r = requests.post(URL, json=payload, timeout=30)

print("STATUS:", r.status_code)
print("BODY:", r.text)
