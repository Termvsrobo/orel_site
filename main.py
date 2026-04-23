from math import ceil
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, create_engine, func, select

from config import settings
from models import Item
from sitemap import SiteMap

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

sitemap = SiteMap(
    app=app, base_url="https://орелсельхоззапчасть.рф", gzip=True, include_dynamic=True
)

templates = Jinja2Templates(directory="templates")
templates.env.globals.update({'description': settings.DESCRIPTION})


@app.get("/")
async def get_all_items(request: Request, page: Optional[int] = 1) -> HTMLResponse:
    start = (page - 1) * settings.ITEMS_PER_PAGE
    last_page = 1
    pagination_right = 5
    pagination_left = 1
    engine = create_engine(settings.DB_URL.encoded_string())
    # Считаем максимальное количество страниц
    with Session(engine) as session:
        stmt = select(func.count() // settings.ITEMS_PER_PAGE + 1).select_from(Item)
        last_page = session.exec(stmt).first()
        pagination_right = min(ceil(page / 5) * 5, last_page)
        pagination_left = max(pagination_right - 4, 1)
    if page > last_page:
        raise HTTPException(status_code=404)
    with Session(engine) as session:
        statement = (
            select(Item).order_by(Item.id).limit(settings.ITEMS_PER_PAGE).offset(start)
        )
        items = session.exec(statement).all()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "items": items,
            "page": page,
            'last_page': last_page,
            'title': settings.TITLE,
            "pagination_right": pagination_right,
            'pagination_left': pagination_left
        }
    )


@app.get("/search")
async def get_search(request: Request, search: Optional[str] = "", page: Optional[int] = 1):
    start = (page - 1) * settings.ITEMS_PER_PAGE
    last_page = 1
    pagination_right = 5
    pagination_left = 1
    engine = create_engine(settings.DB_URL.encoded_string())
    with Session(engine) as session:
        stmt = select(func.count() // settings.ITEMS_PER_PAGE + 1).select_from(Item).where(Item.name.contains(search))
        last_page = session.exec(stmt).first()
        pagination_right = min(ceil(page / 5) * 5, last_page)
        pagination_left = max(pagination_right - 4, 1)
        statement = select(Item).order_by(Item.id).limit(settings.ITEMS_PER_PAGE).offset(start).where(
            Item.name.contains(search)
        )
        items = session.exec(statement).all()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "items": items,
            'title': f'{settings.TITLE}: Результаты поиска',
            "page": page,
            "last_page": last_page,
            "breadcrumb": {'name': 'Результаты поиска', 'url': f'/search?search={search}'},
            "search": search,
            "pagination_right": pagination_right,
            'pagination_left': pagination_left
        }
    )


@app.get("/items/{item_name}")
async def get_item(request: Request, item_name: str):
    engine = create_engine(settings.DB_URL.encoded_string())
    with Session(engine) as session:
        statement = select(Item).order_by(Item.id).where(Item.name == item_name)
        item = session.exec(statement).first()
    if item:
        return templates.TemplateResponse(
            request,
            "detail.html",
            {
                "item": item,
                'title': f'{settings.TITLE}: {item.name}',
                "breadcrumb": {'name': item.name, 'url': f'/items/{item.name}'}
            }
        )
    else:
        raise HTTPException(status_code=404, detail='Страница не найдена')


@app.get("/robots.txt", response_class=PlainTextResponse)
async def get_robots():
    data = """User-agent: *\nAllow: /\nSitemap:/sitemap.xml"""
    return data


@app.exception_handler(404)
async def page_not_found(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request,
        "not_found.html",
        status_code=404
    )


sitemap.attach()
