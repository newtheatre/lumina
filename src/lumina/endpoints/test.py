from fastapi import APIRouter

from lumina.config import settings

router = APIRouter()


@router.get("/hello")
def hello_world():
    return {"Hello": "World"}


@router.get("/config")
def get_config():
    return settings.dict()
