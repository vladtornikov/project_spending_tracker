import logging
import signal
import sys
import time
from collections.abc import Awaitable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Callable

import uvicorn
from fastapi import FastAPI, Request, Response

from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

sys.path.append(str(Path(__file__).parents[1]))

from internal.config import settings
from internal.logger import configure_logging
from internal.controllers_API.auth_API import router as auth_router

logger = logging.getLogger(__name__)
configure_logging()


def handle_shutdown_signal(signum, frame):
	logging.info("received shutdown signal: %s %s", signum, format)


@asynccontextmanager
async def lifespan(app: FastAPI):
	signal.signal(signal.SIGINT, handle_shutdown_signal)
	signal.signal(signal.SIGBREAK, handle_shutdown_signal)
	logging.info("Start the application")
	yield
	logging.info("Shutdown the application")


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)


@app.middleware("http")
async def add_process_time_to_request(
	request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
	logger.info("New request %s to %s", request.method, request.url)

	start_time = time.perf_counter()
	response = await call_next(request)
	process_time = time.perf_counter() - start_time

	logger.info(
		"Handled request %s %s in %.3f sec, status code is %s",
		request.method,
		request.url,
		process_time,
		response.status_code,
	)
	response.headers["X-Process-Time"] = f"{process_time:.3f}"
	return response


@app.get("/")
def root():
	return "Hello!"



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
	return {"token": token}

if __name__ == "__main__":
	uvicorn.run(
		"main:app",
		host=settings.yaml.server.host,
		port=settings.yaml.server.port,
		reload=settings.yaml.server.reload,
	)
