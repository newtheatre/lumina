from fastapi import FastAPI

from lumina.config import settings
from lumina.router import router

app = FastAPI(title="Lumina", version=settings.vcs_rev, root_path=settings.root_path)
app.include_router(router)
