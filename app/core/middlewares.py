import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.datastructures import MutableHeaders
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core import logger, settings
from app.core.db import engine


# Middleware Demo 🚀
# @app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


class CustomMiddleware:
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app: ASGIApp = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            if scope["type"] != "http":
                return await self.app(scope, receive, send)

            def send_wrapper(message: Message) -> Awaitable[None]:
                if message["type"] == "http.response.start":
                    # This modifies the "message" Dict in place, which is used by the "send" function below
                    response_headers = MutableHeaders(scope=message)
                    response_headers["X-Process-Time"] = str(time.time() - start_time)
                return send(message)

            start_time = time.time()

            await self.app(scope, receive, send_wrapper)
        except asyncio.CancelledError:
            pass


def use_middlewares(app: FastAPI) -> FastAPI:
    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.add_middleware(
        CustomMiddleware,
    )
    return app


async def startup() -> None:
    logger.info("启动服务，初始化资源")


async def shutdown() -> None:
    logger.info("关闭服务，释放资源")
    # 关闭所有活跃的 publishers
    engine.dispose()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await startup()
    yield
    await shutdown()
