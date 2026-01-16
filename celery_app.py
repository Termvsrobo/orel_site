from typing import Dict, List
from pathlib import Path
from urllib.parse import urljoin

from celery import Celery
from celery.schedules import crontab
from httpx import Client, TimeoutException
from sanitize_filename import sanitize
from sqlmodel import select, insert, create_engine, Session
from tqdm import tqdm

from config import settings
from models import Item
from utils import get_data, get_last_link


celery_app = Celery()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        crontab(hour=0, minute=30),
        parse.s(),
    )


celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL.encoded_string(),
    result_backend=settings.CELERY_RESULT_BACKEND.encoded_string(),
)


@celery_app.task
def parse():
    print('start task')
    data: List[Dict[str, str]] = []
    last_number: int = 0
    base_dir = Path(__file__).parent
    media_dir = base_dir / "media"
    with Client(follow_redirects=True) as client:
        for attempt in range(5):
            try:
                response = client.get(
                    settings.URL,
                )
                if response.status_code == 200:
                    data += get_data(response.content)
                    last_number = get_last_link(response.content)
            except TimeoutException:
                continue
            else:
                for page_number in tqdm(range(2, last_number + 1)):
                    for attempt in range(5):
                        try:
                            response = client.get(
                                settings.URL,
                                params={
                                    "PAGEN_1": page_number,
                                    "ajax_get": "Y",
                                    "AJAX_REQUEST": "Y",
                                    "bitrix_include_areas": "N",
                                },
                            )
                        except TimeoutException:
                            continue
                        else:
                            if response.status_code == 200:
                                data += get_data(response.content)
                                break
                break
        for _data in tqdm(data):
            _image_url = _data.pop('image_url')
            if _image_url:
                image_url = urljoin(settings.URL, _image_url)
                image_response = client.get(image_url)
                if image_response.status_code == 200:
                    f_name = sanitize(_data['name'])
                    image_dir = media_dir / f_name
                    image_dir.mkdir(parents=True, exist_ok=True)
                    image_path = image_dir / f"{f_name}.jpg"
                    image_path.write_bytes(image_response.content)
                    _data['image'] = image_path.relative_to(base_dir).as_posix()
            else:
                _data['image'] = None
    engine = create_engine(settings.DB_URL.encoded_string())
    with Session(engine) as session:
        existing_items_stmt = select(Item)
        existing_items = session.exec(existing_items_stmt).all()
        existing_items_name = [item.name for item in existing_items]
        data_to_insert = list(filter(lambda x: x["name"] not in existing_items_name, data))
        if data_to_insert:
            insert_stmt = insert(Item).values(data_to_insert)
            session.exec(insert_stmt)
            session.commit()
        for item in existing_items:
            for new_data in filter(lambda x: x["name"] == item.name, data):
                if (
                    item.in_stock != new_data["in_stock"]
                    or item.price_value != new_data["price_value"]
                    or item.price_currency != new_data["price_currency"]
                    or item.image != new_data["image"]
                ):
                    item.in_stock = new_data["in_stock"]
                    item.price_value = new_data["price_value"]
                    item.price_currency = new_data["price_currency"]
                    if new_data["image"]:
                        item.image = new_data["image"]
                    session.commit()


@celery_app.task
def test(arg):
    print(arg)

if __name__ == "__main__":
    parse()
