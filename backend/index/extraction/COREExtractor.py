import os
import aiohttp

from dotenv import load_dotenv
from datetime import datetime
from backend.documentTypes import DocumentType
from backend.index.DataSource import DataSource
from backend.index.database.entities.Document import Document
from backend.index.extraction.Extractor import Extractor
from backend.index.extraction.queryTerms import extractor_query_terms


class COREExtractor(Extractor):
    def __init__(self, use_full_text=True, debug_mode=False):

        # Retrieve params
        load_dotenv()
        core_api_key = os.getenv("CORE_API_KEY")

        self.__headers = {
            "User-Agent": DataSource.agent,
            "Authorization": f"Bearer {core_api_key}",
        }

        super().__init__(
            "CORE",
            "https://core.ac.uk/",
            use_full_text=use_full_text,
            debug_mode=debug_mode,
        )

    async def get_document_collection_data(self, source_id: int) -> list[Document]:
        async with aiohttp.ClientSession() as session:
            params = {
                "q": " OR ".join(extractor_query_terms),
                "limit": Extractor.max_results,
            }
            try:
                async with session.get(
                    "https://api.core.ac.uk/v3/search/works",
                    headers=self.__headers,
                    params=params,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [
                            Document.from_attributes(
                                self._sanitize_text(result["title"]),
                                self._sanitize_text(result["abstract"]),
                                DocumentType.PAPER,
                                result["downloadUrl"],
                                source_id,
                                datetime.fromisoformat(result["publishedDate"]),
                            )
                            for result in data["results"]
                        ]
                    else:
                        self._log_extraction_error(
                            f"received status code {response.status} {response.reason}"
                        )
                        return []
            except aiohttp.ClientError as e:
                self._log_extraction_error(f"http request error {e}")
                return []
