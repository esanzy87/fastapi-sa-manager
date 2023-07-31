import os
from fastapi.applications import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request

# from fastapi.staticfiles import StaticFiles


ENV: str = os.getenv("ENV", "dev")
DEBUG: bool = ENV in ("local", "test", "dev")


if DEBUG:
    ALLOWED_ORIGINS = ["*"]
    OPENAPI_ALLOWED_IPS = ["*"]
else:
    ALLOWED_ORIGINS = []
    OPENAPI_ALLOWED_IPS = []


app = FastAPI(
    debug=DEBUG,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.include_router(api_router, prefix="/api")


def get_remote_ip_addr(request: Request):
    return request.headers.get(
        "X-Real-Ip", request.headers.get("X-Forwarded-For", request.client.host)
    )


async def get_openapi_endpoint(request: Request):
    from fastapi import status
    from fastapi.exceptions import HTTPException
    from fastapi.openapi.utils import get_openapi

    ip_addr = get_remote_ip_addr(request)
    if ip_addr not in OPENAPI_ALLOWED_IPS and "*" not in OPENAPI_ALLOWED_IPS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return JSONResponse(
        get_openapi(
            title="Open API",
            version="1.0.0",
            routes=app.routes,
        )
    )


async def get_documentation(request: Request):
    from fastapi import status
    from fastapi.exceptions import HTTPException
    from fastapi.openapi.docs import get_swagger_ui_html

    ip_addr = get_remote_ip_addr(request)
    if ip_addr not in OPENAPI_ALLOWED_IPS and "*" not in OPENAPI_ALLOWED_IPS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Documentation",
    )


app.add_api_route(
    "/openapi.json",
    get_openapi_endpoint,
    response_class=JSONResponse,
    include_in_schema=False,
)
app.add_api_route(
    "/docs",
    get_documentation,
    response_class=HTMLResponse,
    include_in_schema=False,
)


# 리액트 풀스택인 경우 주석 해제
# async def index(request: Request):
#     from fastapi.templating import Jinja2Templates

#     templates = Jinja2Templates(directory="reactapp/build")
#     return templates.TemplateResponse("index.html", {"request": request})


# if ENV not in ("local", "test"):
#     app.mount("/static", StaticFiles(directory="reactapp/build/static"), name="static")
#     app.mount("/assets", StaticFiles(directory="reactapp/build/assets"), name="assets")
#     app.add_api_route(
#         "/{web_route_path:path}",
#         index,
#         response_class=HTMLResponse,
#         include_in_schema=False,
#     )
