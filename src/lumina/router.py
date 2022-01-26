import humps
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from lumina.endpoints import auth, github, health, member, submissions

router = APIRouter()
router.include_router(auth.router, tags=["auth"], prefix="/auth")
router.include_router(member.router, tags=["member"], prefix="/member")
router.include_router(submissions.router, tags=["submissions"], prefix="/submissions")
router.include_router(github.router, tags=["github"], prefix="/github")
router.include_router(health.router, tags=["health"], prefix="/health")


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = humps.camelize(route.name)
