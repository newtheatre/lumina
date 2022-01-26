from lumina.config import settings


def get_content_repo_path(target_type: str, target_id: str) -> str:
    if target_type == "show":
        return f"_shows/{target_id}.md"


def get_content_repo_file_url(path: str, branch: str = "master") -> str:
    return f"https://github.com/{settings.github_owner}/{settings.github_repo}/blob/master/{path}"


def get_content_repo_issue_url(id: int) -> str:
    return (
        f"https://github.com/{settings.github_owner}/{settings.github_repo}/issues/{id}"
    )
