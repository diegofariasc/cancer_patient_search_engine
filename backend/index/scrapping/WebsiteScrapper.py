import asyncio
import inspect
import re
import aiohttp

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from backend.documentTypes import DocumentType
from backend.index.DataSource import DataSource
from backend.index.database.entities.Document import Document
from backend.index.database.entities.Source import Source
from backend.index.scrapping.utils import get_favicon


class WebsiteScrapper(DataSource):
    def __init__(
        self,
        base_url: str,
        source_name: str,
        max_depth: int = 5,
        scrapping_delay=1,
        debug_mode=False,
    ):
        self.__base_url = base_url
        self.__debug_mode = debug_mode
        self.__max_depth = max_depth
        self.__source_name = source_name
        self.__scrapping_delay = scrapping_delay
        self.__visited_links = set()
        self.__visited_links_lock = asyncio.Lock()

    async def get_source_data(self) -> Source:
        source = Source(
            source_name=self.__source_name,
            base_url=self.__base_url,
            icon=get_favicon(self.__base_url),
        )
        return source

    def get_source_name(self) -> str:
        return self.__source_name

    async def get_document_text(self, document_data: Document) -> str:
        return document_data.get_summary()

    async def __get_all_subsites_data_recursive(
        self, url: str, source_id: int, depth: int = 0
    ) -> set[Document]:
        if depth >= self.__max_depth:
            return set()

        async with self.__visited_links_lock:
            if url in self.__visited_links:
                return set()

            self.__visited_links.add(url)

        soup = await self.__get_site_soup(url)

        if soup is None:
            return set()

        try:
            subsites_data = set[Document]()
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                full_url = urljoin(url, href)  # Convert to absolute
                subsite_data = await self.__get_site_data(full_url, source_id)

                if subsite_data is not None:
                    subsites_data.add(subsite_data)

            all_subsites_data = subsites_data.copy()
            for document in subsites_data:
                await asyncio.sleep(self.__scrapping_delay)  # Usamos asyncio.sleep
                all_subsites_data.update(
                    await self.__get_all_subsites_data_recursive(
                        document.get_document_url(), source_id, depth + 1
                    )
                )

            return all_subsites_data

        except aiohttp.ClientError as e:
            self.__log_scrapper_error(url, e)
            return set()

    async def get_document_collection_data(self, source_id: int) -> set[Document]:
        self.__visited_links = set()
        return await self.__get_all_subsites_data_recursive(
            self.__base_url, source_id, depth=0
        )

    def __log_scrapper_error(self, url: str, message: str):
        if not self.__debug_mode:
            return

        frame = inspect.currentframe()
        caller_frame = frame.f_back
        caller_function_name = caller_frame.f_code.co_name

        print(
            f"Error while scrapping url {url} at function {caller_function_name}:",
            message,
        )

    async def __get_site_soup(self, url: str) -> BeautifulSoup:
        if not url:
            self.__log_scrapper_error(url, "empty url provided")
            return None

        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            self.__log_scrapper_error(url, "invalid url format")
            return None

        if not url.startswith(self.__base_url):
            self.__log_scrapper_error(url, "out of scope url")
            return None

        headers = {
            "User-Agent": DataSource.agent,
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        return BeautifulSoup(html, "html.parser")
                    else:
                        self.__log_scrapper_error(
                            url,
                            f"failed to retrieve page with status {response.status}",
                        )
                        return None
        except Exception as e:
            self.__log_scrapper_error(url, e)
            return None

    def __get_site_text(self, soup: BeautifulSoup) -> str:
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        paragraphs = soup.find_all(["p"])
        cleaned_paragraphs = []

        for p in paragraphs:
            text = p.get_text()
            cleaned_paragraphs.append(self.__sanitize_text(text))

        return " ".join(cleaned_paragraphs)

    def __sanitize_text(self, text: str):
        new_text = re.sub(r"https?://\S+", "", text)  # Delete URLs
        new_text = " ".join(text.split())  # Delete extra spaces

        return new_text

    def __sanitize_document_title(self, title: str | None):
        if not title:
            return None

        new_title = self.__sanitize_text(title)
        new_title = re.sub(r"\s*\|.*", "", title)  # Delete all after "|"

        if new_title:
            return new_title

        return None

    async def __get_site_data(self, url: str, source_id: int) -> Document | None:
        async with self.__visited_links_lock:
            if url in self.__visited_links:
                return None

            self.__visited_links.add(url)

        soup = await self.__get_site_soup(url)

        if soup == None:
            return None

        site_text = self.__get_site_text(soup)
        title_tag = soup.find("title") or soup.find("h1")
        title = (
            None
            if title_tag == None
            else self.__sanitize_document_title(title_tag.get_text())
        )

        if title == None or site_text == "":
            return None

        document = Document(
            title=title,
            summary=site_text,
            document_type=DocumentType.WEBSITE,
            document_url=url,
            source_id=source_id,
        )
        return document
