# app/llm/llm.py
import json
from google.genai import Client
from app.llm.tool_schema import TOOLS
from app.llm.system_prompt import SYSTEM_PROMPT
from app.core.config import settings

client = Client(api_key=settings.GEMINI_API_KEY)


async def call_llm_with_tools(history, message, tools, conversation_id=None):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": message},
    ]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config={"tools": TOOLS},
    )

    part = response.candidates[0].content.parts[0]

    # ---------- TOOL CALL ----------
    if part.function_call:
        name = part.function_call.name
        args = part.function_call.args

        if not hasattr(tools, name):
            return {
                "message": "That action is not allowed.",
                "actions": [],
            }, {
                "tool_name": None,
                "confidence": 0.2,
                "conversation_id": conversation_id,
            }

        result = await getattr(tools, name)(**args)

        return {
            "message": "Done.",
            "data": result,
            "actions": [],
        }, {
            "tool_name": name,
            "confidence": 0.9,
            "conversation_id": conversation_id,
        }

    # ---------- NORMAL RESPONSE ----------
    try:
        parsed = json.loads(part.text)
    except Exception:
        parsed = {
            "message": part.text,
            "actions": [],
        }

    return parsed, {
        "tool_name": None,
        "confidence": 0.6,
        "conversation_id": conversation_id,
    }
