import aiohttp
from io import BytesIO
from pdfminer.high_level import extract_text


async def download_pdf(url, headers) -> bytes:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    print(f"Error downloading PDF from url '{url}': {response.status}")
                    return b""
        except aiohttp.ClientError as e:
            print(f"Error in PDF download HTTP request for url '{url}': {e}")
            return b""


async def get_pdf_text(pdf_data: bytes) -> str:
    try:
        with BytesIO(pdf_data) as pdf_file:
            return extract_text(pdf_file)
    except Exception as e:
        print(f"Error getting PDF text: {e}")
        return ""
