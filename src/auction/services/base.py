from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.db.schemas import LeadSchema


@dataclass
class BaseAuction(ABC):
    leads: list[LeadSchema]

    @abstractmethod
    async def start(self):
        raise NotImplementedError
