from fastapi import APIRouter

from lumina.config import settings

router = APIRouter()


@router.get("/hello")
def read_root():
    return {"Hello": "World"}


@router.get("/config")
def read_root():
    return {"config": settings}
