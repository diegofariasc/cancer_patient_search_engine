class DocumentStatistics:
    def __init__(self, document_count: int, average_document_length: int):
        self.__document_count: int = document_count
        self.__average_document_length: float = average_document_length

    def get_document_count(self) -> int:
        return self.__document_count

    def get_average_document_length(self) -> float:
        return self.__average_document_length
