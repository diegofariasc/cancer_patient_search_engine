import aiohttp

from backend.index.extraction.Extractor import Extractor
from backend.index.extraction.utils import download_pdf, get_pdf_text


class PubMedExtractor(Extractor):
    headers = {
        "User-Agent": Extractor.agent,
        "Accept": "application/json",
        "Referer": "https://www.ncbi.nlm.nih.gov/",
    }
    entrez_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    entrez_params = {
        "db": "pmc",
        "term": Extractor.query,
        "retmax": Extractor.max_results,
        "retmode": "json",
    }

    def __init__(self, debugMode=False):
        super().__init__("PubMed", debugMode=debugMode)

    async def get_source_pointers(self) -> list:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    PubMedExtractor.entrez_url,
                    params=PubMedExtractor.entrez_params,
                    headers=PubMedExtractor.headers,
                ) as response:
                    if response.status == 200:
                        search_response = await response.json()
                        return search_response.get("esearchresult", {}).get(
                            "idlist", []
                        )
                    else:
                        return []
            except aiohttp.ClientError as e:
                if self._debugMode:
                    print(
                        f"Error in PubMed extraction get_source_pointers HTTP request: {e}"
                    )
                return []

    async def get_source_text(self, pointer) -> str:
        pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pointer}/pdf/"
        try:
            pdf_data = await download_pdf(pdf_url, PubMedExtractor.headers)
            text = await get_pdf_text(pdf_data)
            return text
        except Exception as e:
            if self._debugMode:
                print(
                    f"Error retrieving PubMed source text with pointer {pointer}: {e}"
                )
            return ""
