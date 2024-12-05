import os
import sys

sys.path.append("/root/cancer_patient_search_engine")

import asyncio
from backend.index.utils import read_websites_csv
from backend.index.scrapping.WebsiteScrapper import WebsiteScrapper
from backend.engine.TermProcessor import TermProcessor
from backend.index.Indexer import Indexer
from backend.index.extraction.PubMedExtractor import PubMedExtractor
from backend.index.extraction.DOAJExtractor import DOAJExtractor
from backend.index.extraction.ArXivExtractor import ArXivExtractor
from backend.index.extraction.COREExtractor import COREExtractor
from backend.index.database.DatabaseModel import DatabaseModel


def main():
    model = DatabaseModel()
    termProcessor = TermProcessor()
    debug_mode = False
    use_full_text = True

    sources = [
        ArXivExtractor(use_full_text=use_full_text, debug_mode=debug_mode),
        PubMedExtractor(use_full_text=use_full_text, debug_mode=debug_mode),
        COREExtractor(use_full_text=use_full_text, debug_mode=debug_mode),
        DOAJExtractor(use_full_text=use_full_text, debug_mode=debug_mode),
    ]

    websites_data = read_websites_csv(f"{os.getcwd()}/backend/index/websites_data.csv")
    for website_data in websites_data:
        sources.append(
            WebsiteScrapper(
                website_data.get("url"),
                website_data.get("name"),
                debug_mode=debug_mode,
            )
        )

    use_dump_data = False
    if model.is_insertions_record_available():
        while True:
            answer = input(
                "There is an uncommited and pre-built insertions record available, use it? [y/n]: "
            ).lower()
            if answer == "y":
                model.load_insertions_record()
                use_dump_data = True
                print("Reusing insertions record from .dumpdata file....")
                break
            elif answer == "n":
                model.delete_insertions_record()
                print("Removed .dumpdata file and generating new index")
                break
            else:
                print("Unrecognized answer. Reuse available insertions record? [y/n]: ")

    indexer = Indexer(model, termProcessor, sources)
    asyncio.run(indexer.index(use_dump_data=use_dump_data))


if __name__ == "__main__":
    main()
