import sys
import asyncio
from backend.engine.TermProcessor import TermProcessor
from backend.index.database.DatabaseModel import DatabaseModel
from backend.index.extraction.Extractor import Extractor


class Indexer:
    def __init__(
        self,
        model: DatabaseModel,
        termProcessor: TermProcessor,
        extractors: list[Extractor],
    ):
        self.__model = model
        self.__termProcessor = termProcessor
        self.__extractors = extractors
        self.__progress_indicators = {
            extractor.get_extractor_name(): 0 for extractor in extractors
        }

    def __report_progress(self):
        progress_lines = []
        for extractor_name, progress in self.__progress_indicators.items():
            progress_percentage = (progress / Extractor.max_results) * 100
            progress_line = f"Indexing {extractor_name}: {progress}/{Extractor.max_results} ({progress_percentage:.2f}%)"
            progress_lines.append(progress_line)

        print(self.__progress_indicators)
        #sys.stdout.write("\r" + "   " * 3 + "\r")
        #sys.stdout.write("\r".join(progress_lines))
        #sys.stdout.flush()

    async def __index_document(self, extractor: Extractor, pointer):
        text = await extractor.get_source_text(pointer)
        terms = self.__termProcessor.get_terms(text)
        self.__progress_indicators[extractor.get_extractor_name()] += 1
        self.__report_progress()

    async def __index_source(self, extractor: Extractor):
        pointers = await extractor.get_source_pointers()
        tasks = []
        for pointer in pointers:
            task = self.__index_document(extractor, pointer)
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def index(self):
        print("Started indexing process")

        tasks = []
        for extractor in self.__extractors:
            task = self.__index_source(extractor)
            tasks.append(task)

        await asyncio.gather(*tasks)

        print("Finished indexing process")
