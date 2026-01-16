from itertools import product
from typing import Dict, List

from cachetools import cached, TTLCache
from httpx import Client
from loguru import logger
from bs4 import BeautifulSoup

from config import settings


@cached(cache=TTLCache(maxsize=1024, ttl=86400))
def get_current_course(currency: str) -> float:
    result = None
    with Client() as client:
        response = client.get("https://www.cbr-xml-daily.ru/daily_json.js")
        if response.status_code == 200:
            data = response.json()
            if (
                "Valute" in data
                and currency in data["Valute"]
                and "Value" in data["Valute"][currency]
            ):
                result = data.get("Valute").get(currency).get("Value")
    return result


def _convert_item_price(price_value: str, currency: str) -> float:
    result = None
    current_course = get_current_course(currency)
    if price_value:
        try:
            if "." in price_value:
                price_value = price_value.replace(".", "")
            if "," in price_value:
                price_value = price_value.replace(",", ".")
            result = (
                float(price_value)
                * current_course
                * (1 + settings.MARKUP_PERCENT / 100)
            )
        except ValueError:
            logger.exception(f"Ошибка при конвертации цены {price_value}")
    else:
        result = 0
    result = str(result) if result else ""
    return result


def convert_items_price(items: list[dict[str, str]]) -> list[dict[str, str]]:
    _items = [
        {
            "name": item["name"],
            "in_stock": item["in_stock"],
            "price_value": _convert_item_price(
                item["price_value"], item["price_currency"]
            ),
        }
        for item in items
    ]
    return _items


def get_last_link(content) -> int:
    last_number = 0
    soup = BeautifulSoup(content, "html.parser")
    links = soup.find_all(
        lambda tag: tag.name == "a" and tag.get("class") == ["dark_link"]
    )
    if links:
        numbers = [int(link.text) for link in links]
        last_number = max(numbers)
    return last_number


def get_data(content) -> List[Dict[str, str]]:
    result = []
    price_value = None
    price_currency = None
    soup = BeautifulSoup(content, "html.parser")
    elements = soup.find_all(attrs={"class": "item_info"})
    for element in elements:
        name_element = element.find(
            attrs={"class": "muted font_sxs"}
        )
        name = None
        if name_element:
            name = name_element.text.replace('Арт.: ', '')
            for to_replace in product('TТ', repeat=2):
                name = name.replace(''.join(to_replace), '')
            images = element.parent.find('div', attrs={'class': 'image_wrapper_block js-notice-block__image'}).find_all('img')
            image_url = None
            if len(images) >= 2:
                image_url = images[1].get("data-src")
        in_stock = element.find(attrs={"class": "value font_sxs"}).text
        price_value_element = element.find(attrs={"class": "price_value"})
        if price_value_element:
            price_value = price_value_element.text.strip()
            price_value = price_value.replace(".", "").replace(",", ".")
            price_value = float(price_value)
        price_currency_element = element.find(attrs={"class": "price_currency"})
        if price_currency_element:
            price_currency = price_currency_element.text.strip()
        result.append(
            {
                "name": name,
                "in_stock": in_stock,
                "price_value": price_value,
                "price_currency": price_currency,
                "image_url": image_url,
            }
        )
    return result
