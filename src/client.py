"""Client for making requests to OpenRouter System One decision models."""
import time
import requests
from typing import Dict, Any, Union, Optional
from src.config import OPENROUTER_SYSTEMONE_URL, OPENROUTER_DECISIONS_URL, get_api_key
from src.schemas import SystemOneRequest, SystemOneResponse, UsageInfo

class DecisionAPIError(Exception):
    """Base exception for Decision API calls."""
    pass

class AuthenticationError(DecisionAPIError):
    """Raised when API key is missing or invalid."""
    pass

class DecisionClient:
    """Client for calling OpenRouter System One endpoint."""

    def __init__(self, api_key: Optional[str] = None, endpoint_url: Optional[str] = None):
        if api_key is not None:
            self.api_key = api_key.strip()
        else:
            self.api_key = get_api_key().strip()
        self.endpoint_url = endpoint_url or OPENROUTER_SYSTEMONE_URL

    def evaluate(
        self,
        model: str,
        state: Union[str, Dict[str, Any]],
        questions: Dict[str, Any],
        timeout: int = 30,
    ) -> SystemOneResponse:
        """
        Evaluate a state against a set of typed questions using a System One decision model.
        """
        if not self.api_key:
            raise AuthenticationError(
                "OpenRouter API Key is missing. Provide it in the sidebar or set OPENROUTER_API_KEY in .env."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Decision Models Streamlit UI",
        }

        # Sanitize questions: OpenRouter rejects 'criteria': null
        clean_questions = {}
        for q_id, q_val in questions.items():
            q_clean = dict(q_val)
            if q_clean.get("criteria") is None:
                q_clean.pop("criteria", None)
            clean_questions[q_id] = q_clean

        payload = {
            "model": model,
            "state": state,
            "questions": clean_questions,
        }

        # Validate with Pydantic request schema
        SystemOneRequest.model_validate(payload)

        start_time = time.perf_counter()
        response = None
        error_msg = ""
        last_status = None

        urls_to_try = [self.endpoint_url]
        if self.endpoint_url == OPENROUTER_SYSTEMONE_URL:
            urls_to_try.append(OPENROUTER_DECISIONS_URL)

        for url in urls_to_try:
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
                last_status = resp.status_code
                if resp.status_code == 200:
                    response = resp
                    break
                elif resp.status_code in (401, 403):
                    data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                    msg = data.get("error", {}).get("message", resp.text)
                    raise AuthenticationError(f"Authentication failed ({resp.status_code}): {msg}")
                elif resp.status_code == 400:
                    data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                    msg = data.get("error", {}).get("message", resp.text)
                    raise DecisionAPIError(f"Invalid request (400): {msg}")
                elif resp.status_code == 404:
                    continue
                else:
                    data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                    error_msg = data.get("error", {}).get("message", resp.text)
            except (AuthenticationError, DecisionAPIError):
                raise
            except requests.exceptions.RequestException as e:
                error_msg = str(e)
                continue

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        if response is None:
            raise DecisionAPIError(
                f"API request failed with status {last_status or 'Unknown'}: {error_msg or 'Failed to reach OpenRouter endpoint'}"
            )

        try:
            data = response.json()
        except ValueError:
            raise DecisionAPIError(f"Failed to parse JSON response: {response.text}")

        # Parse usage
        usage_data = data.get("usage", {})
        usage = UsageInfo(
            input_tokens=usage_data.get("input_tokens", 0),
            output_tokens=usage_data.get("output_tokens", 0),
            cost=usage_data.get("cost", 0.0),
        )

        return SystemOneResponse(
            id=data.get("id"),
            model=data.get("model", model),
            provider=data.get("provider"),
            answers=data.get("answers", {}),
            usage=usage,
            latency_ms=latency_ms,
            raw=data,
        )
