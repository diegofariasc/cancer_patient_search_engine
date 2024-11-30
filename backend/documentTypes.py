from enum import Enum


class ExtendedEnum(Enum):

    @classmethod
    def get_values(cls):
        return list(map(lambda member: member.value, cls))


class DocumentType(ExtendedEnum):
    PAPER = "paper"
    WEBSITE = "website"

    def __str__(self):
        return self.value


class DocumentLanguage(ExtendedEnum):
    ENGLISH = "english"
    SPANISH = "spanish"

    def __str__(self):
        return self.value
