from http import HTTPStatus

from fastapi import APIRouter, Header, HTTPException, Request
from lumina.github import webhooks
from lumina.schema.github import GitHubWebhook

router = APIRouter()


@router.post(
    "/webhook",
    responses={
        int(HTTPStatus.BAD_REQUEST): {"description": "Missing signature header"},
        int(HTTPStatus.UNAUTHORIZED): {"description": "Signature verification failed"},
    },
)
async def handle_webhook(
    request: Request,
    webhook: GitHubWebhook,
    X_Hub_Signature_256: str | None = Header(None),
):
    if not X_Hub_Signature_256:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Missing signature header"
        )
    if not webhooks.verify_webhook(
        signature=X_Hub_Signature_256, body=await request.body()
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Signature verification failed"
        )
    webhooks.handle_webhook(webhook)
