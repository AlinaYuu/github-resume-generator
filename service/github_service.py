import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if token:
    HEADERS["Authorization"] = f"Bearer {token}"


def fetch_github_profile(username):
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url, headers=HEADERS) #+++ заголовок
        if response.ok:
            profile = response.json()
            return {
                "name": profile.get("name", ""),
                "email": profile.get("email", ""),
                "blog": profile.get("blog", ""),
                "github_url": profile.get("html_url", ""),
                "location": profile.get("location", ""),
                "company": profile.get("company", ""),
                "bio": profile.get("bio", ""),
                "twitter": f"https://twitter.com/{profile['twitter_username']}" if profile.get(
                    "twitter_username") else "",
                "public_repos": profile.get("public_repos", 0)
            }
    except Exception as e:
        print(f"Ошибка при получении профиля GitHub для пользователя '{username}': {e}")
    return {}


def fetch_github_data(username):
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    headers = {**HEADERS, "Accept": "application/vnd.github.mercy-preview+json"}

    try:
        response = requests.get(url, headers=headers)
        if not response.ok:
            return []

        repos_data = response.json()
        print(f"Всего получено репозиториев: {len(repos_data)}")
        repositories = []

        for repo in repos_data:
            license_name = (repo.get("license") or {}).get("name")
            repositories.append({
                "name": repo.get("name", ""),
                "html_url": repo.get("html_url", ""),
                "description": repo.get("description", ""),
                "homepage": repo.get("homepage", ""),
                "topics": repo.get("topics", []),
                "language": repo.get("language"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "fork": repo.get("fork", False),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "open_issues": repo.get("open_issues_count", 0),
                "license": license_name,
                "is_template": repo.get("is_template", False),
            })

        return repositories
    except Exception as e:
        print(f"Ошибка при получении репозиториев: {e}")
    return []


def fetch_readme(username, repo_name):
    url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    headers = {**HEADERS, "Accept": "application/vnd.github.v3.raw"}
    try:
        response = requests.get(url, headers=headers)
        if response.ok:
            readme_text = response.text.strip()
            if len(readme_text) > 5000:
                return readme_text[:5000] + "\n...\n[truncated]"
            return readme_text
    except Exception as e:
        print(f"Ошибка при получении README для {username}/{repo_name}: {e}")
    return None


def fetch_languages(username, repo_name):
    url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    try:
        response = requests.get(url, headers=HEADERS)
        return response.json() if response.ok else {}
    except Exception as e:
        print(f"Ошибка при получении языков для {username}/{repo_name}: {e}")
        return {}


def enrich_repos_with_details(username, repositories):
    enriched_repos = []

    for repo in repositories:
        readme = fetch_readme(username, repo["name"])
        repo["readme_excerpt"] = "\n".join(readme.splitlines()[:5]) if readme else ""

        languages = fetch_languages(username, repo["name"])
        repo["languages"] = languages

        enriched_repos.append(repo)

    return enriched_repos
