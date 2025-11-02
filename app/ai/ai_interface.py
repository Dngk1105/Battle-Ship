import random
from abc import ABC, abstractmethod
from app.game_logic.base_logic import GameLogic


class AIInterface(ABC):
    """
    Interface quy định mọi AI phải có 2 hàm chính:
    - place_ships(): cách AI đặt tàu
    - make_shot(): cách AI chọn ô để bắn
    """

    @abstractmethod
    def place_ships(self):
        pass

    @abstractmethod
    def make_shot(self, attacker_name: str, target_name: str) -> dict:
        """
        Chọn ô để bắn.

        Returns:
            dict: {"result": str, "x": int, "y": int}
        """
        pass


class BaseAI(GameLogic, AIInterface, ABC):
    """
    Base class cho tất cả AI.
    """

    def __init__(self, game, name=None):
        super().__init__(game)
        self.game = game
        self.name = name or (game.ai.name if game.ai else "AI bot")

    @abstractmethod
    def place_ships(self):
        pass

    @abstractmethod
    def make_shot(self, attacker_name: str, target_name: str) -> dict:
        pass
