from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

import lumina.router
from lumina.config import settings

app = FastAPI(title="Lumina", version=settings.vcs_rev, root_path=settings.root_path)

app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://nthp-web.pages.dev"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lumina.router.router)
lumina.router.use_route_names_as_operation_ids(app)
