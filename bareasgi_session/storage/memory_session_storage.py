"""Session Storage"""

from typing import Dict

from .session_storage import SessionStorage


class MemorySessionStorage(SessionStorage):
    """Memory session storage"""

    def __init__(self) -> None:
        """Memory session storage"""
        self.sessions: Dict[str, dict] = {}

    async def load(self, key: str) -> dict:
        return self.sessions.setdefault(key, {})

    async def save(self, key: str, session: dict) -> None:
        self.sessions[key] = session
