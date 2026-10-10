"""Configuration and model registry for OpenRouter System One decision models."""
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_SYSTEMONE_URL = "https://openrouter.ai/api/v1/systemone"
OPENROUTER_DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"

AVAILABLE_MODELS: List[Dict[str, Any]] = [
    {
        "id": "inception/mercury-decide:free",
        "name": "Inception: Mercury Decide (free)",
        "badge": "Free Tier",
        "provider": "Inception Labs",
        "speed": "Up to 14 dec/sec",
        "context": "66K",
        "description": "Inception's structured decision model served as a System One endpoint. Free output tokens with calibrated probability.",
    },
    {
        "id": "inception/mercury-decide",
        "name": "Inception: Mercury Decide",
        "badge": "Standard",
        "provider": "Inception Labs",
        "speed": "Up to 14 dec/sec",
        "context": "66K",
        "description": "Full production endpoint for Inception Mercury Decide.",
    },
    {
        "id": "typesafe/jev-1.13",
        "name": "TypeSafe: Jev 1.13",
        "badge": "Standard",
        "provider": "TypeSafe",
        "speed": "Fast",
        "context": "16K",
        "description": "Original System One decision model from TypeSafe for routing, safety gates, and rubric scoring.",
    },
    {
        "id": "typesafe/jev-latest",
        "name": "TypeSafe: Jev (Latest)",
        "badge": "Latest Release",
        "provider": "TypeSafe",
        "speed": "Fast",
        "context": "16K",
        "description": "Latest snapshot release of Jev.",
    },
]

DEFAULT_MODEL_ID = os.getenv("DEFAULT_MODEL", "inception/mercury-decide:free")

def get_api_key() -> str:
    """Retrieve OpenRouter API key from environment or Streamlit secrets."""
    env_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if env_key:
        return env_key
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "OPENROUTER_API_KEY" in st.secrets:
            return str(st.secrets["OPENROUTER_API_KEY"]).strip()
    except Exception:
        pass
    return ""
