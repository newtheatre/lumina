from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    environment: str = "dev"
    stage_name: str = ""
    vcs_rev: str = "unknown"
    aws_region: str = "eu-west-2"

    github_owner: str = "newtheatre"
    github_repo: str = "lumina-test"

    sentry_dsn: Optional[str] = None

    @property
    def root_path(self) -> Optional[str]:
        if self.stage_name in {"", "dev", "Environment"}:
            return None
        if self.stage_name == "prod":
            return "https://lumina.nthp.wjdp.uk"
        return f"/{self.stage_name}"


settings = Settings()
