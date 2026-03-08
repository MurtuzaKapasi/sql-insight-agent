import requests
from requests import HTTPError
from app.core.config import settings


class GroqClient:
    def __init__(self) -> None:
        raw_key = settings.groq_api_key or ""
        self.api_key = raw_key.strip().strip("\"").strip("'")
        self.model = settings.groq_model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _raise_groq_error(self, exc: HTTPError) -> None:
        status_code = exc.response.status_code if exc.response is not None else None
        detail = ""
        if exc.response is not None:
            try:
                payload = exc.response.json()
                detail = payload.get("error", {}).get("message", "")
            except Exception:
                detail = exc.response.text[:300]
        msg = f"Groq API request failed with status {status_code}."
        if detail:
            msg = f"{msg} Detail: {detail}"
        raise RuntimeError(msg) from exc

    def generate_text(self, prompt: str, temperature: float = 0.1) -> str:
        if not self.api_key:
            return ""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": temperature,
            "max_tokens": 2048,
        }

        try:
            resp = requests.post(self.base_url, headers=self._headers(), json=payload, timeout=60)
            resp.raise_for_status()
        except HTTPError as exc:
            self._raise_groq_error(exc)
        except requests.RequestException as exc:
            raise RuntimeError("Groq API request failed due to a network or timeout issue.") from exc

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            return ""

        message = choices[0].get("message", {})
        return (message.get("content") or "").strip()
