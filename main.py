from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, create_engine, func

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
templates.env.globals.update({'title': settings.TITLE, 'description': settings.DESCRIPTION})


@app.get("/")
async def get_all_items(request: Request, page: Optional[int] = 1) -> HTMLResponse:
    start = (page - 1) * settings.ITEMS_PER_PAGE
    engine = create_engine(settings.DB_URL.encoded_string())
    last_page = 1
    # Считаем максимальное количество страниц
    with Session(engine) as session:
        stmt = select(func.count() // settings.ITEMS_PER_PAGE + 1).select_from(Item)
        last_page = session.exec(stmt).first()
    if page > last_page:
        raise HTTPException(status_code=404)
    with Session(engine) as session:
        statement = (
            select(Item).order_by(Item.id).limit(settings.ITEMS_PER_PAGE).offset(start)
        )
        items = session.exec(statement).all()
    return templates.TemplateResponse(
        request, "items.html", {"items": items, "page": page, 'last_page': last_page}
    )


@app.get("/search")
async def get_search(request: Request, search: Optional[str] = ""):
    engine = create_engine(settings.DB_URL.encoded_string())
    with Session(engine) as session:
        statement = select(Item).order_by(Item.id).where(Item.name.contains(search))
        items = session.exec(statement).all()
    return templates.TemplateResponse(request, "search_result.html", {"items": items})


@app.get("/items/{item_name}")
async def get_item(request: Request, item_name: str):
    engine = create_engine(settings.DB_URL.encoded_string())
    with Session(engine) as session:
        statement = select(Item).order_by(Item.id).where(Item.name == item_name)
        item = session.exec(statement).first()
    return templates.TemplateResponse(request, "detail.html", {"item": item})


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
