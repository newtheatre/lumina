from fastapi import APIRouter

from lumina.endpoints import test

router = APIRouter()
router.include_router(test.router, tags=["test"], prefix="/test")
