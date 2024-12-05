from datetime import datetime
import aiohttp

from backend.documentTypes import DocumentType
from backend.index.DataSource import DataSource
from backend.index.database.entities.Document import Document
from backend.index.extraction.Extractor import Extractor
from backend.index.extraction.queryTerms import extractor_query_terms


class PubMedExtractor(Extractor):

    def __init__(self, use_full_text=True, debug_mode=False):
        self.__headers = {
            "User-Agent": DataSource.agent,
            "Accept": "application/json",
            "Referer": "https://www.ncbi.nlm.nih.gov/",
        }
        super().__init__(
            "PubMed",
            "https://pubmed.ncbi.nlm.nih.gov/",
            use_full_text=use_full_text,
            debug_mode=debug_mode,
        )

    async def _fetch_documents_details(
        self, session, document_ids: set[str], source_id: int
    ) -> list[Document]:
        entrez_url_summary = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        )
        entrez_params_summary = {
            "db": "pmc",
            "id": ",".join(document_ids),
            "retmode": "json",
        }
        async with session.get(
            entrez_url_summary, params=entrez_params_summary, headers=self.__headers
        ) as response:
            if response.status == 200:
                summary_response = await response.json()
                result = summary_response.get("result", {})
                documents_data = [(key, result[key]) for key in result if key != "uids"]

                documents = []
                for document_id, document_data in documents_data:
                    title = document_data.get("title", None)
                    summary = document_data.get("summary", None)

                    publish_date = document_data.get("pubdate", None)
                    publish_date = (
                        datetime.strptime(publish_date, "%Y %b %d")
                        if publish_date
                        else None
                    )

                    if not title or not summary:
                        continue

                    document = Document.from_attributes(
                        title=title,
                        summary=summary,
                        document_type=DocumentType.PAPER,
                        document_url=f"https://www.ncbi.nlm.nih.gov/pmc/articles/{document_id}/pdf/",
                        source_id=source_id,
                        publish_date=publish_date,
                    )
                    documents.append(document)

                return documents
            else:
                self._log_extraction_error(
                    f"error in eSummary request: {response.status}"
                )
                return []

    async def get_document_collection_data(self, source_id: int) -> list[Document]:
        entrez_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        entrez_params = {
            "db": "pmc",
            "term": " OR ".join(extractor_query_terms),
            "retmax": Extractor.max_results,
            "retmode": "json",
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    entrez_url,
                    params=entrez_params,
                    headers=self.__headers,
                ) as response:
                    if response.status == 200:
                        search_response = await response.json()
                        esearch_result = search_response.get("esearchresult", {})
                        document_ids = set(esearch_result.get("idlist", []))
                        return await self._fetch_documents_details(
                            session, document_ids, source_id
                        )
                        return []
                    else:
                        self._log_extraction_error(
                            f"received status code {response.status} {response.reason}"
                        )
                        return []
            except aiohttp.ClientError as e:
                self._log_extraction_error(f"http request error {e}")
                return []
