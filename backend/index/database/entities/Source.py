class Source:
    def __init__(self, source_name: str, base_url: str, icon: bytes | None):
        self.__source_name = source_name
        self.__base_url = base_url
        self.__icon = icon

    def to_dict(self) -> dict:
        return {
            "source_name": self.__source_name,
            "base_url": self.__base_url,
            "icon": self.__icon,
        }

    def get_source_name(self) -> str:
        return self.__source_name

    def get_base_url(self) -> str:
        return self.__base_url

    def get_icon(self) -> bytes:
        return self.__icon
