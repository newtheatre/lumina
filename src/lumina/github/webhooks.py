import hmac

import lumina.database.operations
from lumina import ssm
from lumina.database.models import GitHubIssueModel
from lumina.database.operations import ResultNotFound
from lumina.schema.github import GitHubWebhook

HEADER_SIGNATURE = "X-Hub-Signature-256"
HEADER_PREFIX = "sha256="

import logging

log = logging.getLogger(__name__)


def get_webhook_secret() -> str:
    return ssm.get_parameter("/lumina/github/webhook-secret")


"""
Reference Implementation:
    post '/payload' do
      request.body.rewind
      payload_body = request.body.read
      verify_signature(payload_body)
      push = JSON.parse(payload_body)
      "I got some JSON: #{push.inspect}"
    end
    
    def verify_signature(payload_body)
      signature = 'sha256=' + OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new('sha256'), ENV['SECRET_TOKEN'], payload_body)
      return halt 500, "Signatures didn't match!" unless Rack::Utils.secure_compare(signature, request.env['HTTP_X_HUB_SIGNATURE_256'])
    end
"""


def verify_webhook(signature: str, body: bytes) -> bool:
    return hmac.compare_digest(
        signature.removeprefix(HEADER_PREFIX),
        hmac.new(get_webhook_secret().encode(), body, "sha256").hexdigest(),
    )


def update_issue_from_webhook(webhook: GitHubWebhook) -> None:
    if not webhook.issue:
        raise ValueError("Webhook does not contain an issue")
    try:
        lumina.database.operations.update_submission_github_issue(
            webhook.issue.number, GitHubIssueModel(**webhook.issue.dict())
        )
    except ResultNotFound:
        log.exception("Could not update issue as not found in db")


def handle_webhook(webhook: GitHubWebhook) -> None:
    if webhook.issue:
        update_issue_from_webhook(webhook)
