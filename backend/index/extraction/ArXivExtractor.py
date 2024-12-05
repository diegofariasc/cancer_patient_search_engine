import aiohttp
from xml.etree import ElementTree
from backend.documentTypes import DocumentType
from backend.index.DataSource import DataSource
from backend.index.database.entities.Document import Document
from backend.index.database.entities.Source import Source
from backend.index.extraction.Extractor import Extractor
from backend.index.extraction.queryTerms import extractor_query_terms
from backend.index.extraction.utils import (
    find_all_elements_by_atom_xpath,
    find_elements_by_atom_xpath,
)


class ArXivExtractor(Extractor):
    def __init__(self, use_full_text=True, debug_mode=False):
        super().__init__(
            "ArXiv",
            "https://arxiv.org/",
            use_full_text=use_full_text,
            debug_mode=debug_mode,
        )

    def _get_documents_data(self, source_id: int, xml_response: str) -> list[Document]:
        tree = ElementTree.fromstring(xml_response)
        entries = find_all_elements_by_atom_xpath(tree, "entry")
        documents_data = []

        for entry in entries:
            elements_dict = find_elements_by_atom_xpath(
                entry, ["id", "title", "summary"]
            )

            summary = elements_dict["summary"].text
            title = elements_dict["title"].text

            if not title or not summary:
                continue

            document = Document(
                title=self._sanitize_text(title),
                summary=self._sanitize_text(summary),
                document_type=DocumentType.PAPER,
                document_url=elements_dict["id"].text.replace("/abs/", "/pdf/"),
                source_id=source_id,
            )
            documents_data.append(document)

        return documents_data

    async def get_document_collection_data(self, source_id: int) -> list[Document]:
        arxiv_url = f"http://export.arxiv.org/api/query?search_query={" ".join(extractor_query_terms)}&max_results={Extractor.max_results}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(arxiv_url) as response:
                    if response.status == 200:
                        xml_response = await response.text()
                        documents_data = self._get_documents_data(
                            source_id, xml_response
                        )
                        return documents_data
                    else:
                        self._log_extraction_error(
                            f"received status code {response.status} {response.reason}"
                        )
                        return []
            except aiohttp.ClientError as e:
                self._log_extraction_error(f"http request error {e}")
                return []
