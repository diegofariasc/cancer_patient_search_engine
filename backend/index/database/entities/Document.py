from datetime import datetime
from backend.documentTypes import DocumentType
from backend.index.database.entities.DatabaseEntity import DatabaseEntity
from backend.utils import get_text_language


class Document(DatabaseEntity):
    def __init__(self):
        self.__id: int = None
        self.__title: str = None
        self.__summary: str = None
        self.__document_type: DocumentType = None
        self.__publish_date: datetime = None
        self.__document_url: str = None
        self.__document_length: int = None
        self.__document_language: str = None
        self.__source_id: int = None

    @classmethod
    def from_database_row(cls, row: dict) -> "Document":
        document = cls()
        document.__id = row["ID"]
        document.__title = row["TITLE"]
        document.__summary = row["SUMMARY"]
        document.__document_type = row["DOCUMENT_TYPE"]
        document.__publish_date = row["PUBLISH_DATE"]
        document.__document_url = row["DOCUMENT_URL"]
        document.__document_length = row["DOCUMENT_LENGTH"]
        document.__document_language = row["DOCUMENT_LANGUAGE"]
        document.__source_id = row["SOURCE_ID"]
        return document

    @classmethod
    def from_attributes(
        cls,
        title: str,
        summary: str,
        document_type: DocumentType,
        document_url: str,
        source_id: int,
        publish_date: datetime = None,
    ) -> "Document":
        document = cls()
        document.__title = title
        document.__summary = summary
        document.__document_type = document_type
        document.__publish_date = publish_date
        document.__document_url = document_url
        document.__document_language = get_text_language(summary)
        document.__source_id = source_id
        return document

    def to_db_tuple(self) -> tuple:
        return (
            self.__title,
            self.__summary[:1001],
            self.__document_type.value,
            self.__publish_date,
            self.__document_url,
            self.__document_language,
            self.__source_id,
        )

    def get_id(self) -> int:
        return self.__id

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

    def get_document_length(self) -> int:
        return self.__document_length

    def get_document_language(self) -> str:
        return self.__document_language

    def get_source_id(self) -> int:
        return self.__source_id
