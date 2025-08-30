import logging
import sys
import time
from collections.abc import Awaitable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Callable

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

sys.path.append(str(Path(__file__).parents[1]))

from internal.config import settings
from internal.controllers_API.auth_API import router as auth_router
from internal.controllers_API.categories_API import router as category_router
from internal.controllers_API.transactions_API import router as transaction_router
from internal.exceptions import AppError
from internal.logger import configure_logging, logger_dep


@asynccontextmanager
async def lifespan(app: FastAPI):
    # добавляем в атрибут state наш логгер для логгирования в middleware, в эндпоинтах будем использовать через DI #noqa: E501
    app.state.logger: logging.Logger = configure_logging()

    def handle_shutdown_signal(signum, frame):
        app.state.logger.info("received shutdown signal: %s %s", signum, format)

    # signal.signal(signal.SIGINT, handle_shutdown_signal)
    # signal.signal(signal.SIGBREAK, handle_shutdown_signal)
    app.state.logger.info("Start the application")
    yield
    app.state.logger.info("Shutdown the application")


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(category_router)
app.include_router(transaction_router)


@app.middleware("http")
async def add_process_time_to_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    app_logger: logging.Logger = request.app.state.logger
    app_logger.info("New request %s to %s", request.method, request.url)

    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    app_logger.info(
        "Handled request %s %s in %.3f sec, status code is %s",
        request.method,
        request.url,
        process_time,
        response.status_code,
    )
    return response


@app.exception_handler(AppError)
async def validation_exception_error(request: Request, exc: AppError):
    headers = {}
    if exc.status_code == 401:
        headers["WWW-Authenticate"] = exc.www_authenticate

    return JSONResponse(
        status_code=exc.status_code,
        headers=headers,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


@app.get("/")
def root(app_logger: logger_dep):  # здесь уже dependency
    app_logger.info("Basic endpoint")
    return "Hello!"


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=True,
    )
