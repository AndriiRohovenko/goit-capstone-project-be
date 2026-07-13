import uvicorn
from src.conf.config import config


def dev():
    uvicorn.run("src.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)


def prod():
    uvicorn.run("src.main:app", host=config.API_HOST, port=config.API_PORT)
