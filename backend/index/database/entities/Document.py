from backend.documentTypes import DocumentType
from backend.index.database.entities.DatabaseEntity import DatabaseEntity


class Document(DatabaseEntity):
    def __init__(self):
        self.__id: int = None
        self.__title: str = None
        self.__authors: list[str] = None
        self.__summary: str = None
        self.__document_type: str = None
        self.__doi: str = None
        self.__country: str = None
        self.__publish_date: str = None
        self.__document_url: str = None
        self.__document_length: int = None
        self.__document_language: str = None
        self.__source_id: int = None

    @classmethod
    def from_database_row(cls, row: dict) -> "Document":
        document = cls()
        document.__id = row["ID"]
        document.__title = row["TITLE"]
        document.__authors = row["AUTHORS"]
        document.__summary = row["SUMMARY"]
        document.__document_type = row["DOCUMENT_TYPE"]
        document.__doi = row["DOI"]
        document.__country = row["COUNTRY"]
        document.__publish_date = row["PUBLISH_DATE"]
        document.__document_url = row["DOCUMENT_URL"]
        document.__document_length = row["DOCUMENT_LENGTH"]
        document.__document_language = row["DOCUMENT_LANGUAGE"]
        document.__source_id = row["SOURCE_ID"]
        return document

    @classmethod
    def from_attributes(
        cls,
        id: int,
        title: str,
        authors: list[str],
        summary: str,
        document_type: DocumentType,
        doi: str,
        country: str,
        publish_date: str,
        document_url: str,
        document_length: int,
        document_language: str,
        source_id: int,
    ) -> "Document":
        document = cls()
        document.__id = id
        document.__title = title
        document.__authors = authors
        document.__summary = summary
        document.__document_type = document_type
        document.__doi = doi
        document.__country = country
        document.__publish_date = publish_date
        document.__document_url = document_url
        document.__document_length = document_length
        document.__document_language = document_language
        document.__source_id = source_id
        return document

    def to_dict(self) -> dict[str, any]:
        return {
            "id": self.__id,
            "title": self.__title,
            "authors": self.__authors,
            "summary": self.__summary,
            "document_type": self.__document_type,
            "doi": self.__doi,
            "country": self.__country,
            "publish_date": self.__publish_date,
            "document_url": self.__document_url,
            "document_length": self.__document_length,
            "document_language": self.__document_language,
            "source_id": self.__source_id,
        }

    def get_id(self) -> int:
        return self.__id

    def get_title(self) -> str:
        return self.__title

    def get_authors(self) -> list[str]:
        return self.__authors

    def get_summary(self) -> str:
        return self.__summary

    def get_document_type(self) -> str:
        return self.__document_type

    def get_doi(self) -> str:
        return self.__doi

    def get_country(self) -> str:
        return self.__country

    def get_publish_date(self) -> str:
        return self.__publish_date

    def get_document_url(self) -> str:
        return self.__document_url

    def get_document_length(self) -> int:
        return self.__document_length

    def get_document_language(self) -> str:
        return self.__document_language

    def get_source_id(self) -> int:
        return self.__source_id
