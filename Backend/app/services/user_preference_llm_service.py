# app/services/user_preference_llm_service.py
from typing import List, Dict
import json

from google import genai
from app.core.config import settings

# --------------------------------------------------
# CLIENT SETUP (NEW SDK)
# --------------------------------------------------

client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"


# --------------------------------------------------
# PREFERENCE INFERENCE
# --------------------------------------------------

async def generate_preferences_from_events(events: List[Dict]) -> Dict:
    """
    Infers user preferences from recent user events.
    Returns STRICT JSON or {} on failure.
    """

    prompt = f"""
You are a recommendation engine.

Given the following user events, infer:
- preferred_categories (array of strings)
- preferred_price_range (object with min, max)
- preferred_brands (array of strings)

Events:
{json.dumps(events, indent=2)}

Return STRICT JSON ONLY in the following format:
{{
  "preferred_categories": [],
  "preferred_price_range": {{"min": number, "max": number}},
  "preferred_brands": []
}}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )

        # SDK guarantees text aggregation
        text = response.text.strip()

        return json.loads(text)

    except Exception:
        # Hard safety: never break event pipeline
        return {}
