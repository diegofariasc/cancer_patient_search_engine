from datetime import datetime
from backend.documentTypes import DocumentType
from backend.utils import get_text_language


class Document:
    def __init__(
        self,
        title: str,
        summary: str,
        document_type: DocumentType,
        document_url: str,
        source_id: int,
        publish_date: datetime = None,
    ):
        self.__title = title
        self.__summary = summary
        self.__document_type = document_type
        self.__publish_date = publish_date
        self.__document_url = document_url
        self.__document_language = get_text_language(summary)
        self.__source_id = source_id

    def to_tuple(self) -> tuple:
        return (
            self.__title,
            self.__summary[:1001],
            self.__document_type.value,
            self.__publish_date,
            self.__document_url,
            self.__document_language,
            self.__source_id,
        )

    def get_title(self) -> str:
        return self.__title

    def get_summary(self) -> str:
        return self.__summary

    def get_document_type(self) -> str:
        return self.__document_type

    def get_publish_date(self) -> datetime:
        return self.__publish_date

    def get_document_url(self) -> str:
        return self.__document_url

    def get_document_language(self) -> str:
        return self.__document_language

    def get_source_id(self) -> int:
        return self.__source_id
