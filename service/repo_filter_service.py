from datetime import datetime
from typing import List, Dict, Optional


ZERO_OK = {"stars", "forks", "open_issues"}


def has_value(key: str, val) -> bool:
    if val is None:
        return False
    if isinstance(val, str) and not val.strip():
        return False
    if isinstance(val, list) and not val:
        return False
    if isinstance(val, int):
        return key in ZERO_OK or val != 0
    return True


def filter_repos(repos: List[Dict], top_n: Optional[int] = None) -> List[Dict]:
    output = []

    for repo in repos:
        if repo.get("fork") or repo.get("is_template"):
            continue

        if not has_value("description", repo.get("description")) and not has_value("readme_excerpt", repo.get("readme_excerpt")):
            continue

        output.append(repo)

    def sort_key(repo: Dict):
        stars = repo.get("stars", 0)
        pushed = repo.get("pushed_at")
        pushed_dt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ") if pushed else datetime.min
        return (stars, pushed_dt)

    output.sort(key=sort_key, reverse=True)

    return output if top_n is None else output[:top_n]



def get_readme_excerpt(readme: Optional[str], lines: int = 5) -> Optional[str]:
    if not readme:
        return None

    excerpt = "\n".join(readme.strip().splitlines()[:lines])
    return excerpt.strip() or None
