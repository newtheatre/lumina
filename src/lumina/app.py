from fastapi import FastAPI

import lumina.router
from lumina.config import settings

app = FastAPI(title="Lumina", version=settings.vcs_rev, root_path=settings.root_path)
app.include_router(lumina.router.router)
lumina.router.use_route_names_as_operation_ids(app)
