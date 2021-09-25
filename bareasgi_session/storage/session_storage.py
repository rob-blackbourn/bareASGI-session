"""Session Storage"""

from abc import ABCMeta, abstractmethod


class SessionStorage(metaclass=ABCMeta):
    """Session Storage"""

    @abstractmethod
    async def load(self, key: str) -> dict:
        """Load session data

        Args:
            key (str): The session key.

        Returns:
            dict: The session data.
        """

    @abstractmethod
    async def save(self, key: str, session: dict) -> None:
        """Save session data

        Args:
            key (str): The session key.
            session (dict): The session data.
        """
