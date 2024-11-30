from abc import ABC, abstractmethod
import asyncio


class Extractor(ABC):
    query = "cancer"
    max_results = 10
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def __init__(self, extractorName: str, debugMode=False):
        self._debugMode = debugMode
        self.__extractorName = extractorName
        super().__init__()

    @abstractmethod
    async def get_source_pointers() -> list:
        pass

    @abstractmethod
    async def get_source_text(pointer) -> str:
        pass

    def get_extractor_name(self) -> str:
        return self.__extractorName
