import base64
import json
import logging
import re

import requests

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.exceptions.photo_verification_failed_exception import PhotoVerificationFailedException
from microadventures.domain.models.photo_verdict import PhotoVerdict
from microadventures.domain.services.photo_verifier import PhotoVerifier
from microadventures.infrastructure.api.model_tracing import record_usage, traced_model_call

logger = logging.getLogger(__name__)

YES = ("true", "yes", "si", "sí", "aceptada", "aceptado")


def _as_bool(value) -> bool:
    """The model sometimes answers "false" as text, and bool("false") would be True."""
    if isinstance(value, str):
        return value.strip().lower() in YES
    return bool(value)


def parse_verdict(text: str) -> PhotoVerdict:
    """Reads the model's answer. Asked for plain text (a JSON mode can come back empty with images), it also accepts JSON."""
    text = (text or "").strip()
    if not text:
        raise ValueError("the model answered nothing")
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            verdict = json.loads(match.group(0))
            return PhotoVerdict(accepted=_as_bool(verdict["accepted"]), reason=str(verdict.get("reason", "")))
        except (ValueError, KeyError, TypeError):
            pass  # not the JSON we asked for: read it as text
    verdict = re.search(r"\b(ACEPTADA|RECHAZADA)\b", text, re.IGNORECASE)
    if not verdict:
        raise ValueError(f"no verdict in the answer: {text[:120]!r}")
    reason = text[verdict.end():].strip(" :.-\n")
    return PhotoVerdict(accepted=verdict.group(1).upper() == "ACEPTADA", reason=reason[:200])


class OllamaPhotoVerifier(PhotoVerifier):
    def __init__(self, base_url: str, model: str, timeout_seconds: float = 30, http=requests):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.http = http

    def verify(self, challenge: Challenge, photo: bytes) -> PhotoVerdict:
        prompt = (
            "Eres un revisor estricto de retos de paseo al aire libre. "
            f'Reto: "{challenge.text}"\n'
            "Mira la foto y decide: acepta solo si lo que se ve es lo que pide el reto (por ejemplo, un reto de árbol "
            "exige un árbol o una planta). Rechaza fotos de interiores, pantallas, teclados, objetos que no "
            "tienen que ver con el reto, fotos borrosas o sin contenido. Ante la duda, rechaza.\n"
            "Responde en una sola línea, en español, con esta forma exacta: "
            "ACEPTADA: lo que se ve   o   RECHAZADA: lo que se ve y por qué no vale"
        )
        try:
            with traced_model_call("verify_photo", self.model, prompt) as span:
                span.set_data("photo.bytes", len(photo))
                response = self.http.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "images": [base64.b64encode(photo).decode()],
                        "stream": False,
                        "think": False,  # a short verdict needs no long reasoning, and thinking can leave the answer empty
                        "keep_alive": "30m",
                    },
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
                body = response.json()
                record_usage(span, body)
            verdict = parse_verdict(body.get("response") or body.get("thinking") or "")
            logger.info("📷 Photo %s: %s", "accepted" if verdict.accepted else "rejected", verdict.reason)
            return verdict
        except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError) as error:
            logger.warning("📷 The photo could not be checked (%s): %s", type(error).__name__, error)
            raise PhotoVerificationFailedException(str(error)) from error
