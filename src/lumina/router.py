from fastapi import APIRouter

from lumina.endpoints import submissions, test, user

router = APIRouter()
router.include_router(test.router, tags=["test"], prefix="/test")
router.include_router(user.router, tags=["user"], prefix="/user")
router.include_router(submissions.router, tags=["submissions"], prefix="/sub")
