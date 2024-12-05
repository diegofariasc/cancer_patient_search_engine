import sys
import asyncio
from backend.engine.TermProcessor import TermProcessor
from backend.index.DataSource import DataSource
from backend.index.database.DatabaseModel import DatabaseModel
from backend.index.database.entities.Document import Document


class Indexer:
    def __init__(
        self,
        model: DatabaseModel,
        termProcessor: TermProcessor,
        sources: list[DataSource],
    ):
        self.__model = model
        self.__termProcessor = termProcessor
        self.__sources = sources
        self.__progress_indicators = {source.get_source_name(): 0 for source in sources}

    async def __index_document(self, source: DataSource, document_data: Document):
        text = await source.get_document_text(document_data)
        terms = self.__termProcessor.get_term_frequencies(text)

        # Add document
        document_id = self.__model.insert_document(document_data)

        # Add terms with their frequency
        for term in terms:
            self.__model.record_term_frequency(document_id, term, terms[term])

        self.__progress_indicators[source.get_source_name()] += 1

        print(
            "Successfully indexed document for source:",
            source.get_source_name(),
            document_data.get_document_url(),
        )

    async def __index_documents(self, source: DataSource, source_id: int):
        documents_data = await source.get_document_collection_data(source_id)
        tasks = []
        for document_data in documents_data:
            task = self.__index_document(source, document_data)
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def index(self, use_dump_data: bool):
        print("Started indexing process")

        if not use_dump_data:
            tasks = []
            for source in self.__sources:
                source_data = await source.get_source_data()
                source_id = self.__model.insert_source(source_data)
                task = self.__index_documents(source, source_id)

                tasks.append(task)

            await asyncio.gather(*tasks)

        self.__model.commit_insertions()
        print("\nFinished indexing process")
