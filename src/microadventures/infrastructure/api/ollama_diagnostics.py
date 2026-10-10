import base64
import struct
import time
import zlib

import requests


def _green_square_png(size: int = 32) -> bytes:
    """A tiny valid PNG made on the spot, so the check needs no file."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    row = b"\x00" + bytes([40, 170, 80]) * size
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(row * size))
        + chunk(b"IEND", b"")
    )


def _call(http, url: str, payload: dict, timeout: float) -> dict:
    """One request to the model. Says what happened without ever including the API key."""
    started = time.monotonic()
    result = {"ok": False, "status": None, "ms": 0, "answer": "", "answer_fields": [], "error": ""}
    try:
        response = http.post(url, json=payload, timeout=timeout)
        result["status"] = response.status_code
        response.raise_for_status()
        result["ok"] = True
        body = response.json()
        result["answer"] = str(body.get("response", ""))[:120]
        result["answer_fields"] = sorted(key for key, value in body.items() if value and key in ("response", "thinking"))
    except requests.RequestException as error:
        reply = getattr(getattr(error, "response", None), "text", "") or ""
        result["error"] = f"{type(error).__name__}: {str(error)[:200]} {reply[:300]}".strip()
    except ValueError as error:
        result["error"] = f"The answer was not JSON: {error}"
    result["ms"] = round((time.monotonic() - started) * 1000)
    return result


def check_ollama(http, base_url: str, model: str, vision_model: str, timeout: float, has_api_key: bool) -> dict:
    """What the deploy needs to know when challenges come from templates or photos cannot be checked."""
    url = f"{base_url.rstrip('/')}/api/generate"
    image = base64.b64encode(_green_square_png()).decode()
    return {
        "config": {"url": base_url, "model": model, "vision_model": vision_model, "timeout_seconds": timeout, "api_key_set": has_api_key},
        "text": _call(http, url, {"model": model, "prompt": "Reply with one word: hello", "stream": False}, timeout),
        "vision": _call(
            http, url,
            {"model": vision_model, "prompt": "What colour is this image? Reply with one word.", "images": [image], "stream": False, "think": False},
            timeout,
        ),
    }
