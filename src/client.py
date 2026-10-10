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

        # Sanitize and normalize questions for OpenRouter System One schema
        clean_questions = {}
        for q_id, q_val in questions.items():
            q_clean = dict(q_val)
            q_type = q_clean.get("type", "noul")

            # Ensure instructions is always present
            if not q_clean.get("instructions"):
                q_clean["instructions"] = f"Evaluate {q_id.replace('_', ' ')} based on the state."

            # Normalize choice: convert 'options' list to 'criteria' dict
            if q_type == "choice":
                if "options" in q_clean and "criteria" not in q_clean:
                    opts = q_clean.pop("options")
                    if isinstance(opts, list):
                        q_clean["criteria"] = {str(opt): f"Category: {opt}" for opt in opts}
                elif "criteria" not in q_clean or not isinstance(q_clean.get("criteria"), dict):
                    q_clean["criteria"] = {"default": "Default option"}

            # Normalize score: convert 'range' [min, max] to 'criteria' list
            elif q_type == "score":
                if "range" in q_clean and "criteria" not in q_clean:
                    rng = q_clean.pop("range")
                    if isinstance(rng, list) and len(rng) == 2:
                        try:
                            s, e = int(rng[0]), int(rng[1])
                            q_clean["criteria"] = [f"Level {i}" for i in range(s, e + 1)]
                        except Exception:
                            q_clean["criteria"] = [str(x) for x in rng]
                elif "criteria" not in q_clean or not isinstance(q_clean.get("criteria"), list):
                    q_clean["criteria"] = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]

            # Normalize noul: remove criteria if null
            elif q_type == "noul":
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
