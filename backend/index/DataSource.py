from abc import ABC, abstractmethod

from backend.index.database.entities.Document import Document
from backend.index.database.entities.Source import Source


class DataSource(ABC):
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    @abstractmethod
    async def get_source_data(self) -> Source:
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        pass

    @abstractmethod
    async def get_document_text(self, document_data: Document) -> str:
        pass

    @abstractmethod
    async def get_document_collection_data(self, source_id: int) -> list[Document]:
        pass
