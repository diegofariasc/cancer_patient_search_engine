import sys


sys.path.append("/root/cancer_patient_search_engine")

import asyncio
from backend.engine.TermProcessor import TermProcessor
from backend.index.Indexer import Indexer
from backend.index.extraction.PubMedExtractor import PubMedExtractor
from backend.index.extraction.ArXivExtractor import ArXivExtractor
from backend.index.database.DatabaseModel import DatabaseModel


def main():
    model = DatabaseModel()
    termProcessor = TermProcessor()
    extractors = [
        ArXivExtractor(),
        PubMedExtractor(),
    ]
    indexer = Indexer(model, termProcessor, extractors)
    asyncio.run(indexer.index())


if __name__ == "__main__":
    main()
