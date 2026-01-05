from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, create_engine

from config import settings
from models import Item
from sitemap import SiteMap

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

sitemap = SiteMap(
    app=app, base_url="https://example.com", gzip=True, include_dynamic=True
)

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def get_all_items(request: Request, page: Optional[int] = 1) -> HTMLResponse:
    start = (page - 1) * settings.ITEMS_PER_PAGE
    engine = create_engine(settings.DB_URL.encoded_string())
    with Session(engine) as session:
        statement = (
            select(Item).order_by(Item.id).limit(settings.ITEMS_PER_PAGE).offset(start)
        )
        items = session.exec(statement).all()
    return templates.TemplateResponse(
        request, "items.html", {"items": items, "page": page}
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
    data = """User-agent: *\nAllow: /"""
    return data


sitemap.attach()
