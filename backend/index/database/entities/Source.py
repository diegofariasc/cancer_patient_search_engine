from backend.index.database.entities.DatabaseEntity import DatabaseEntity


class Source(DatabaseEntity):
    def __init__(self):
        self.__id: int = None
        self.__source_name: str = None
        self.__base_url: str = None
        self.__icon: bytes = None

    @classmethod
    def from_database_row(cls, row: dict) -> "Source":
        source = cls()
        source.__id = row["ID"]
        source.__source_name = row["SOURCE_NAME"]
        source.__base_url = row["BASE_URL"]
        source.__icon = row["ICON"]
        return source

    @classmethod
    def from_attributes(
        cls, id: int, source_name: str, base_url: str, icon: bytes
    ) -> "Source":
        source = cls()
        source.__id = id
        source.__source_name = source_name
        source.__base_url = base_url
        source.__icon = icon
        return source

    def to_dict(self) -> dict:
        return {
            "source_name": self.__source_name,
            "base_url": self.__base_url,
            "icon": self.__icon,
        }

    def get_id(self) -> int:
        return self.__id

    def get_source_name(self) -> str:
        return self.__source_name

    def get_base_url(self) -> str:
        return self.__base_url

    def get_icon(self) -> bytes:
        return self.__icon
