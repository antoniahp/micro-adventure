import base64
import json

import requests

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.exceptions.photo_verification_failed_exception import PhotoVerificationFailedException
from microadventures.domain.models.photo_verdict import PhotoVerdict
from microadventures.domain.services.photo_verifier import PhotoVerifier
from microadventures.infrastructure.api.model_tracing import record_usage, traced_model_call


class OllamaPhotoVerifier(PhotoVerifier):
    def __init__(self, base_url: str, model: str, timeout_seconds: float = 30, http=requests):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.http = http

    def verify(self, challenge: Challenge, photo: bytes) -> PhotoVerdict:
        prompt = (
            f'Reto de paseo: "{challenge.text}". ¿La foto cumple el reto? '
            'Responde solo con JSON: {"accepted": true o false, "reason": "motivo en pocas palabras"}'
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
                        "format": "json",
                        "stream": False,
                        "keep_alive": "30m",
                    },
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
                body = response.json()
                record_usage(span, body)
            verdict = json.loads(body["response"])
            return PhotoVerdict(accepted=bool(verdict["accepted"]), reason=str(verdict.get("reason", "")))
        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            raise PhotoVerificationFailedException(str(error)) from error
