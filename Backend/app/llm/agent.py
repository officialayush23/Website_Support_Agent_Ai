# app/llm/agent.py
# app/llm/agent.py
from uuid import UUID
from app.llm.memory import AgentMemory
from app.llm.tools import Tools
from app.llm.llm import call_llm_with_tools
from app.core.database import AsyncSessionLocal
from app.services.agent_action_service import log_agent_action
from app.services.user_event_service import record_event
from app.schema.enums import UserEventType

CONFIDENCE_THRESHOLD = 0.6


async def run_agent(
    *,
    user_id: UUID,
    chat_session_id: UUID,
    user_message: str,
):
    """
    Runs AI agent for a CHAT SESSION.
    Support conversation is created ONLY after handoff.
    """

    memory = AgentMemory(chat_session_id=str(chat_session_id))

    async with AsyncSessionLocal() as db:
        tools = Tools(db=db, user_id=user_id)

        # -------- analytics --------
        await record_event(
            db=db,
            user_id=user_id,
            event_type=UserEventType.chat_message.value,
            metadata={"source": "ai_chat"},
        )

        history = await memory.read()

        response, meta = await call_llm_with_tools(
            history=history,
            message=user_message,
            tools=tools,
        )

        confidence = meta.get("confidence", 0.5)
        tool_name = meta.get("tool_name")

        message = response.get("message", "")
        actions = response.get("actions", [])
        data = response.get("data")

        await log_agent_action(
            db=db,
            conversation_id=None,  # 👈 chat has no conversation
            action_type=tool_name or "chat",
            payload={
                "user_message": user_message,
                "response": message,
                "actions": actions,
            },
            confidence=confidence,
        )

        handoff = confidence < CONFIDENCE_THRESHOLD

        await memory.append("user", user_message)
        await memory.append("assistant", message)

        return {
            "content": message,
            "actions": actions,
            "data": data,
            "confidence": confidence,
            "handoff": handoff,
            "tool_used": tool_name,
        }
