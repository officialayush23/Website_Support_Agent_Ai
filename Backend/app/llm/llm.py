# app/llm/llm.py
import json
from google.genai import Client
from app.llm.tool_schema import TOOLS
from app.llm.system_prompt import SYSTEM_PROMPT
from app.core.config import settings

client = Client(api_key=settings.GEMINI_API_KEY)

# app/llm/llm.py (IMPORTANT CHANGE)

async def call_llm_with_tools(history, message, tools, conversation_id=None):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=history + [message],
        config={"tools": TOOLS},
    )

    part = response.candidates[0].content.parts[0]

    # TOOL CALL
    if part.function_call:
        name = part.function_call.name
        args = part.function_call.args

        if not hasattr(tools, name):
            return (
                {"message": "Action not allowed", "actions": []},
                {"confidence": 0.2, "tool_name": None},
            )

        result = await getattr(tools, name)(**args)

        return (
            {
                "message": "Done ✅",
                "actions": [],
                "data": result,
            },
            {
                "confidence": 0.9,
                "tool_name": name,
            },
        )

    # NORMAL CHAT
    return (
        {
            "message": part.text,
            "actions": [],
        },
        {
            "confidence": 0.7,
            "tool_name": None,
        },
    )
