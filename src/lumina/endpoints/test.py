from fastapi import APIRouter

from lumina.config import settings

router = APIRouter()


@router.get("/hello")
def read_hello():
    return {"Hello": "World"}


@router.get("/config")
def read_config():
    return {"config": settings}
