import hmac

from lumina import ssm
from lumina.schema.github import GitHubWebhook

HEADER_SIGNATURE = "X-Hub-Signature-256"
HEADER_PREFIX = "sha256="


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


def handle_webhook(webhook: GitHubWebhook) -> None:
    print(webhook.dict())
