"""Explicit local-only model adapter. Failures never become fixture answers."""

import os
import httpx


def generate(prompt: str, *, schema=None, model=None):
    payload = {
        "model": model or os.getenv("OLLAMA_MODEL", "qwen3:4b"),
        "prompt": prompt,
        "stream": False,
        "think": False,
        "keep_alive": 0,
        "options": {"temperature": 0, "seed": 42, "num_predict": 512, "num_ctx": 4096},
    }
    if schema:
        payload["format"] = schema
    with httpx.Client(timeout=180) as client:
        r = client.post(os.getenv("OLLAMA_URL", "http://127.0.0.1:11435") + "/api/generate", json=payload)
        r.raise_for_status()
        data = r.json()
    return {
        "text": data["response"],
        "model": data["model"],
        "tokens": data.get("eval_count"),
        "duration_ns": data.get("total_duration"),
        "mode": "local-model",
    }
