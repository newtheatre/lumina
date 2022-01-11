import humps
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from lumina.endpoints import auth, submissions, test, user

router = APIRouter()
router.include_router(test.router, tags=["test"], prefix="/test")
router.include_router(auth.router, tags=["auth"], prefix="/auth")
router.include_router(user.router, tags=["user"], prefix="/user")
router.include_router(submissions.router, tags=["submissions"], prefix="/sub")


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = humps.camelize(route.name)
