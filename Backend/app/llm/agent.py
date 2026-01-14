# app/llm/agent.py
# app/llm/agent.py
from app.llm.memory import AgentMemory
from app.llm.tools import Tools
from app.llm.llm import call_llm_with_tools
from app.core.database import AsyncSessionLocal
from app.services.handoff_service import escalate_to_human
from app.services.agent_action_service import log_agent_action

CONFIDENCE_THRESHOLD = 0.6


async def run_agent(user_id, user_message, conversation_id):
    memory = AgentMemory(user_id)

    async with AsyncSessionLocal() as db:
        tools = Tools(db=db, user_id=user_id)

        history = await memory.read()

        # 🔹 LLM CALL
        response, meta = await call_llm_with_tools(
            history=history,
            message=user_message,
            tools=tools,
            conversation_id=conversation_id,
        )

        confidence = meta.get("confidence", 0.5)
        tool_used = meta.get("tool_name")

        # 🔹 LOG AGENT ACTION
        await log_agent_action(
            db=db,
            conversation_id=conversation_id,
            action_type=tool_used or "chat",
            payload={
                "user_message": user_message,
                "response": response,
            },
            confidence=confidence,
        )

        # 🔹 HUMAN HANDOFF
        if confidence < CONFIDENCE_THRESHOLD:
            await escalate_to_human(
                db=db,
                conversation_id=conversation_id,
                reason="Low agent confidence",
            )

        # 🔹 MEMORY (store plain text only)
        await memory.append("user", user_message)
        await memory.append(
            "assistant",
            response.get("message", ""),
        )

        # 🔹 ALWAYS RETURN JSON FOR UI
        return {
            "message": response.get("message", ""),
            "actions": response.get("actions", []),
            "confidence": confidence,
            "tool_used": tool_used,
        }
