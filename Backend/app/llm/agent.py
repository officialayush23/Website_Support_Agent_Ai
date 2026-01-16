# app/llm/agent.py

from app.llm.memory import AgentMemory
from app.llm.tools import Tools
from app.llm.llm import call_llm_with_tools
from app.core.database import AsyncSessionLocal
from app.services.handoff_service import escalate_to_human
from app.services.agent_action_service import log_agent_action

CONFIDENCE_THRESHOLD = 0.6


async def run_agent(
    user_id,
    user_message: str,
    conversation_id,
):
    """
    Runs the AI agent and returns a WS-friendly response structure.
    """

    memory = AgentMemory(user_id)

    async with AsyncSessionLocal() as db:
        tools = Tools(db=db, user_id=user_id)

        # ----------------------------
        # Load conversation memory
        # ----------------------------
        history = await memory.read()

        # ----------------------------
        # LLM + TOOL CALL
        # ----------------------------
        response_data, meta = await call_llm_with_tools(
            history=history,
            message=user_message,
            tools=tools,
            conversation_id=conversation_id,
        )

        confidence = meta.get("confidence", 0.5)
        tool_used = meta.get("tool_name")

        # ----------------------------
        # Normalize response
        # ----------------------------
        ai_content = (
            response_data.get("message")
            or response_data.get("content")
            or "I'm not sure how to help with that."
        )

        products = response_data.get("products", [])
        if not isinstance(products, list):
            products = []

        # ----------------------------
        # Log agent action
        # ----------------------------
        await log_agent_action(
            db=db,
            conversation_id=conversation_id,
            action_type=tool_used or "chat",
            payload={
                "user_message": user_message,
                "response_text": ai_content,
                "products_count": len(products),
            },
            confidence=confidence,
        )

        # ----------------------------
        # Confidence-based handoff
        # ----------------------------
        handoff_triggered = False
        if confidence < CONFIDENCE_THRESHOLD:
            await escalate_to_human(
                db=db,
                conversation_id=conversation_id,
                reason="Low agent confidence",
            )
            handoff_triggered = True

        # ----------------------------
        # Persist memory (TEXT ONLY)
        # ----------------------------
        await memory.append("user", user_message)
        await memory.append("assistant", ai_content)

        # ----------------------------
        # WS RESPONSE (FINAL CONTRACT)
        # ----------------------------
        return {
            "content": ai_content,        # ✅ frontend text
            "products": products,         # ✅ optional recommendations
            "confidence": confidence,
            "handoff": handoff_triggered,
            "tool_used": tool_used,
        }
