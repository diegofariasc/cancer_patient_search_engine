from abc import ABC, abstractmethod


class DatabaseEntity(ABC):
    @staticmethod
    @abstractmethod
    def from_database_row(cls, row: dict) -> "DatabaseEntity":
        pass

    @staticmethod
    @abstractmethod
    def from_attributes(cls, *args, **kwargs) -> "DatabaseEntity":
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass
