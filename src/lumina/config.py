from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    environment: str = "dev"
    stage_name: str = "abc"
    vcs_rev: str = "unknown"

    @property
    def root_path(self) -> Optional[str]:
        if self.stage_name in {"dev", "Environment"}:
            return None
        if self.stage_name == "prod":
            return "/api/lumina"
        return f"/{self.stage_name}"


settings = Settings()