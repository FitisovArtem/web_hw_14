from pathlib import Path

import redis.asyncio as redis
from typing import Callable

from pydantic import ConfigDict

from ipaddress import ip_address
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import config


app = FastAPI()

banned_ips = [ip_address("192.168.255.1"), ip_address("192.168.255.1")]

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

parent = Path(__file__).parent
directory = parent.joinpath("src").joinpath("static")
app.mount("/static", StaticFiles(directory=directory), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.middleware("http")
async def ban_ips(request: Request, call_next: Callable):
    """
    The ban_ips function is a middleware function that checks if the client's IP address
    is in the banned_ips list. If it is, then we return a JSON response with status code 403
    and an error message. Otherwise, we call the next middleware function and return its response.

    :param request: Request: Get the client's ip address
    :param call_next: Callable: Pass the next function in the middleware chain to ban_ips
    :return: A jsonresponse with a status code of 403 and a message
    :doc-author: Trelent
    """
    if config.APP_ENV == "production":
        ip = ip_address(request.client.host)
        if ip in banned_ips:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"}
            )
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like connecting to databases or initializing caches.

    :return: A list of functions that are executed when the application starts
    :doc-author: Trelent
    """
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)


templates = Jinja2Templates(directory="src/templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    The index function is executed when someone visits the root URL of our site:
    http://localhost:8000/
    It returns a TemplateResponse, which contains both a template and data to be used by that template.
    The first argument to the TemplateResponse constructor is the name of the template file we want to use.
    In this case, it's index.html in our templates directory.

    :param request: Request: Pass the request object to the template
    :return: A templateresponse object
    :doc-author: Trelent
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "our": "Build group WebPython #16"}
    )


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by executing a SQL query to check if it can connect to the database and retrieve data.
    If it cannot, then an HTTPException is raised with status code 500 (Internal Server Error) and detail message &quot;Error connection to database&quot;.
    Otherwise, if everything works as expected, then we return {&quot;message&quot;: &quot;Welcome to FastAPI!&quot;}.

    :param db: AsyncSession: Get the database session
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connection to database")
