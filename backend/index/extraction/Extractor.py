from abc import abstractmethod
import re
from pdfminer.high_level import extract_text
from io import BytesIO
from typing import Callable, Coroutine
from backend.index.DataSource import DataSource
from backend.index.database.entities.Document import Document
from backend.index.database.entities.Source import Source
from backend.index.scrapping.utils import get_favicon

import inspect
import aiohttp


class Extractor(DataSource):
    max_results = 1

    def __init__(
        self, extractor_name: str, base_url: str, use_full_text=True, debug_mode=False
    ):
        self._debug_mode = debug_mode
        self._extractorName = extractor_name
        self._base_url = base_url
        self._use_full_text = use_full_text
        super().__init__()

    async def get_source_data(self) -> Source:
        source = Source.from_attributes(
            source_name=self._extractorName,
            base_url=self._base_url,
            icon=get_favicon(self._base_url),
        )
        return source

    def get_source_name(self) -> str:
        return self._extractorName

    def _log_extraction_error(self, message: str) -> str:
        if not self._debug_mode:
            return

        frame = inspect.currentframe()
        caller_frame = frame.f_back
        caller_function_name = caller_frame.f_code.co_name

        print(
            f"Error in extractor {self._extractorName} at function {caller_function_name}:",
            message,
        )

    async def get_document_text(self, document_data: Document) -> str:
        if not self._use_full_text:
            return document_data.get_summary()

        pdf_url = document_data.get_document_url()
        pdf_data = await self._download_pdf(
            pdf_url, headers={"User-Agent": DataSource.agent}
        )
        text = await self._get_pdf_text(pdf_data)
        return text or document_data.get_summary()

    async def _download_pdf(self, url: str, headers) -> bytes:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        self._log_extraction_error(
                            f"error downloading PDF from url '{url}': {response.status}"
                        )
                        return b""
            except aiohttp.ClientError as e:
                self._log_extraction_error(
                    f"error with download PDF HTTP request for url '{url}': {e}"
                )
                return b""

    async def _get_pdf_text(self, pdf_data: bytes) -> str:
        try:
            with BytesIO(pdf_data) as pdf_file:
                return extract_text(pdf_file)
        except Exception as e:
            self._log_extraction_error(f"Error getting PDF text: {e}")
            return ""

    def _sanitize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.replace("\n", "").replace("\t", "")).strip()

    async def get_document_text(
        self,
        document_data: Document,
    ) -> str:
        document_summary = document_data.get_summary()
        if not self._use_full_text:
            return document_summary

        pdf_url = document_data.get_document_url()
        pdf_data = await self._download_pdf(
            pdf_url, headers={"User-Agent": DataSource.agent}
        )
        text = await self._get_pdf_text(pdf_data)
        return text or document_summary
