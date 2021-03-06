import typing as t
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from qs.database.types import Index
from qs.cache.cache import Cache
from qs.cache.errors import CacheError
from server.misc import (
    present_cache,
    present_db,
    make_database,
    present_error,
    InputModel,
)

database = make_database()
cache = Cache(database)


api = FastAPI()
api.cache = cache
api.db = database

templates = Jinja2Templates(directory="server/templates")


@api.get("/", response_class=HTMLResponse)
def index(
    request: Request,
):
    cache_view = present_cache(request.app.cache)
    db_view = present_db(request.app.db)
    return templates.TemplateResponse(
        "index.html", {"request": request, "db": db_view, "cache": cache_view}
    )


@api.get("/cache")
def load(
    request: Request,
    index: t.Optional[Index],
):
    print(request.app.db.indexes.keys())
    request.app.cache.load(index)
    return {"cache": present_cache(request.app.cache)}


@api.post("/cache")
def insert(
    request: Request,
    body: InputModel,
):
    request.app.cache.insert(value=body.value, parent=body.index)
    return {"cache": present_cache(request.app.cache)}


@api.patch("/cache")
def alter(
    request: Request,
    body: InputModel,
):
    request.app.cache.alter(node_index=body.index, new_value=body.value)
    return {"cache": present_cache(request.app.cache)}


@api.delete("/cache")
def delete(request: Request, index: Index):
    request.app.cache.delete(node_index=index)
    return {"cache": present_cache(request.app.cache)}


@api.post("/cache/apply")
def apply(
    request: Request,
):
    request.app.cache.apply()
    return {"apply": True}


@api.post("/cache/reset")
def reset(request: Request):
    request.app.db = make_database()
    request.app.cache = Cache(request.app.db)


@api.exception_handler(CacheError)
async def cache_exception_handler(request: Request, exc: CacheError):
    return JSONResponse(status_code=400, content=present_error(exc.message))
