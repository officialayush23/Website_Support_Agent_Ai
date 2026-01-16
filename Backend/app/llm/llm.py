# app/llm/llm.py
from google.genai import Client
from app.llm.tool_schema import TOOLS
from app.llm.system_prompt import SYSTEM_PROMPT
from app.core.config import settings

client = Client(api_key=settings.GEMINI_API_KEY)

CONFIRMATION_REQUIRED = {
    "cancel_order",
    "request_refund",
    "create_order",
    "remove_from_cart",
    "raise_complaint",
    "delete_address",
}


async def call_llm_with_tools(history, message, tools):
    contents = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": message},
    ]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config={"tools": TOOLS},
    )

    candidate = response.candidates[0]
    parts = candidate.content.parts

    part = next((p for p in parts if p.text or p.function_call), None)
    if not part:
        return {"message": "I couldn’t process that."}, {"confidence": 0.2}

    if part.function_call:
        name = part.function_call.name
        args = part.function_call.args or {}

        if name in CONFIRMATION_REQUIRED:
            return (
                {
                    "message": f"Please confirm to proceed with {name.replace('_', ' ')}.",
                    "actions": [
                        {
                            "type": "confirm",
                            "label": "Confirm",
                            "tool": name,
                            "params": args,
                        },
                        {"type": "cancel", "label": "Cancel"},
                    ],
                },
                {"confidence": 0.85, "tool_name": name},
            )

        if not hasattr(tools, name):
            return {"message": "Action not allowed."}, {"confidence": 0.2}

        result = await getattr(tools, name)(**args)

        return (
            {"message": "Done ✅", "data": result, "actions": []},
            {"confidence": 0.9, "tool_name": name},
        )

    return (
        {"message": part.text, "actions": []},
        {"confidence": 0.7, "tool_name": None},
    )
