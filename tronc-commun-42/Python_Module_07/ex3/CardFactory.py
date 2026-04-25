from abc import ABC, abstractmethod
from typing import Optional, Union

from ex0.Card import Card


class CardFactory(ABC):
    """Abstract factory interface."""

    @abstractmethod
    def create_creature(
        self,
        name_or_power: Optional[
            Union[str, int]
        ] = None
    ) -> Card:
        pass

    @abstractmethod
    def create_spell(
        self,
        name_or_power: Optional[
            Union[str, int]
        ] = None
    ) -> Card:
        pass

    @abstractmethod
    def create_artifact(
        self,
        name_or_power: Optional[
            Union[str, int]
        ] = None
    ) -> Card:
        pass

    @abstractmethod
    def create_themed_deck(
        self, size: int
    ) -> dict:
        pass

    @abstractmethod
    def get_supported_types(self) -> dict:
        pass
