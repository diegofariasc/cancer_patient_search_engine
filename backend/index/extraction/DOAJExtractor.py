import aiohttp
import urllib
from datetime import datetime
from backend.documentTypes import DocumentType
from backend.index.DataSource import DataSource
from backend.index.database.entities.Document import Document
from backend.index.extraction.Extractor import Extractor
from backend.index.extraction.queryTerms import extractor_query_terms


class DOAJExtractor(Extractor):
    def __init__(self, use_full_text=True, debug_mode=False):
        self.__headers = {
            "User-Agent": DataSource.agent,
        }
        super().__init__(
            "DOAJ",
            "https://doaj.org",
            use_full_text=use_full_text,
            debug_mode=debug_mode,
        )

    async def get_document_collection_data(self, source_id: int) -> list[Document]:
        async with aiohttp.ClientSession() as session:
            params = {
                "page": 1,
                "pageSize": Extractor.max_results,
            }
            try:
                query = " OR ".join(extractor_query_terms)
                encoded_query = urllib.parse.quote(query)
                async with session.get(
                    f"https://doaj.org/api/search/articles/{encoded_query}",
                    headers=self.__headers,
                    params=params,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data["results"]

                        documents = []
                        for result in results:
                            bibjson = result["bibjson"]
                            title = bibjson.get("title")
                            summary = bibjson.get("abstract")
                            link = (
                                bibjson.get("link", [None])[0].get("url", None)
                                if bibjson.get("link")
                                else None
                            )

                            if not link or not title or not summary:
                                continue

                            documents.append(
                                Document.from_attributes(
                                    self._sanitize_text(title),
                                    self._sanitize_text(summary),
                                    DocumentType.PAPER,
                                    link,
                                    source_id,
                                    datetime.fromisoformat(bibjson["created_date"]),
                                )
                            )

                        return documents

                    else:
                        self._log_extraction_error(
                            f"received status code {response.status} {response.reason}"
                        )
                        return []
            except aiohttp.ClientError as e:
                self._log_extraction_error(f"http request error {e}")
                return []
