from uuid import uuid4

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import root_agent

APP_NAME = "smartshopper"
DEFAULT_USER_ID = "streamlit_user"

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
_created_sessions: set[tuple[str, str]] = set()


async def ensure_session(user_id: str, session_id: str) -> None:
    key = (user_id, session_id)
    if key not in _created_sessions:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        _created_sessions.add(key)


async def run_agent(query: str, user_id: str = DEFAULT_USER_ID, session_id: str | None = None) -> str:
    session_id = session_id or str(uuid4())
    await ensure_session(user_id, session_id)
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    )

    final_response = ""
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            final_response = "".join(
                part.text or "" for part in event.content.parts if getattr(part, "text", None)
            )

    return final_response.strip()
