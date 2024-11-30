import aiohttp
from backend.index.extraction.Extractor import Extractor
from backend.index.extraction.utils import download_pdf, get_pdf_text


import aiohttp
from xml.etree import ElementTree
from backend.index.extraction.Extractor import Extractor


class ArXivExtractor(Extractor):
    def __init__(self, debugMode=False):
        super().__init__("ArXiv", debugMode=debugMode)

    async def get_source_pointers(self):
        arxiv_url = f"http://export.arxiv.org/api/query?search_query={Extractor.query}&max_results={Extractor.max_results}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(arxiv_url) as response:
                    if response.status == 200:
                        xml_response = await response.text()
                        return self.parse_arxiv_xml(xml_response)
                    else:
                        print(f"Error: Received status code {response.status}")
                        return []
            except aiohttp.ClientError as e:
                if self._debugMode:
                    print(f"Error during HTTP request: {e}")
                return []

    def parse_arxiv_xml(self, xml_data):
        tree = ElementTree.fromstring(xml_data)
        entries = tree.findall("{http://www.w3.org/2005/Atom}entry")
        ids = []
        for entry in entries:
            id_elem = entry.find("{http://www.w3.org/2005/Atom}id")
            if id_elem is not None:
                arxiv_id = id_elem.text.replace("/abs/", "/pdf/")
                ids.append(arxiv_id)
        return ids

    async def get_source_text(self, pointer):
        try:
            pdf_data = await download_pdf(
                pointer, headers={"User-Agent": Extractor.agent}
            )
            text = await get_pdf_text(pdf_data)
            return text
        except Exception as e:
            if self._debugMode:
                print(f"Error retrieving ArXiv source text with pointer {pointer}: {e}")
            return ""
