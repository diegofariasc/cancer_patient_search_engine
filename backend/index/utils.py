import csv
from typing import TypedDict


class WebsiteData(TypedDict):
    url: str
    name: str


def read_websites_csv(filename: str) -> list[WebsiteData]:
    with open(filename, mode="r", newline="") as file:
        reader = csv.reader(file)
        data = [{"url": row[0], "name": row[1]} for row in reader]
    return data
