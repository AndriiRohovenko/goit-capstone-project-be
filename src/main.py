"""
Main application file for the FastAPI project.
Sets up the FastAPI app, middleware, routes, and exception handlers.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.users import router as users_router
from src.api.utils import router as utils_router
from src.api.auth import router as auth_router
from src.api.contacts import router as contacts_router
import time
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from src.conf.limiter import limiter


from src.api.exceptions import (
    UserNotFoundError,
    DuplicateEmailError,
    user_not_found_handler,
    duplicate_email_handler,
    ServerError,
    server_error_handler,
)


app = FastAPI()
app.state.limiter = limiter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Hello from FastAPI! Read the docs at /docs"}


app.add_exception_handler(UserNotFoundError, user_not_found_handler)
app.add_exception_handler(DuplicateEmailError, duplicate_email_handler)
app.add_exception_handler(ServerError, server_error_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(users_router, prefix="/api")
app.include_router(utils_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(contacts_router, prefix="/api")
