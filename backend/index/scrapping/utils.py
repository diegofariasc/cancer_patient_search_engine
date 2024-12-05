from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests


def get_favicon(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Search in link tags
            favicon = None
            for link in soup.find_all("link", rel=["icon", "shortcut icon"]):
                favicon = link.get("href")
                if favicon:
                    break

            # Default icon if not found
            if not favicon:
                favicon = urljoin(url, "/favicon.ico")

            # Download
            favicon_response = requests.get(favicon)
            if favicon_response.status_code == 200:
                return favicon_response.content
            else:
                return None
        else:
            return None
    except requests.RequestException as e:
        return None
