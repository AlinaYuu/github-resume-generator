from collections import Counter
from typing import List, Dict, Optional

def build_prompt(username: str, repos: List[Dict], profile: Dict = None, all_repos: Optional[List[Dict]] = None) -> str:
    lines = []

    # --- Личная информация ---
    personal_info = []
    if profile:
        if profile.get("name"):
            personal_info.append(f"Имя: {profile['name']}")
        if profile.get("email"):
            personal_info.append(f"Email: {profile['email']}")
        if profile.get("location"):
            personal_info.append(f"Город: {profile['location']}")
        if profile.get("company"):
            personal_info.append(f"Компания/учёба: {profile['company']}")
        if profile.get("github_url"):
            personal_info.append(f"GitHub: {profile['github_url']}")

        other_links = [link for link in [profile.get("blog"), profile.get("twitter")] if link]
        if other_links:
            personal_info.append(f"Другие ссылки: {', '.join(other_links)}")

    if personal_info:
        lines.append("Личная информация")
        lines.extend(personal_info)
        lines.append("")

    # --- Основные навыки (по all_repos, до фильтрации) ---
    skills = []
    source_repos = all_repos if all_repos is not None else repos
    for r in source_repos:
        if isinstance(r.get("languages"), dict):
            skills.extend(r["languages"].keys())
        elif r.get("language"):
            skills.append(r["language"])
        if isinstance(r.get("topics"), list):
            skills.extend(r["topics"])

    skill_counts = Counter([s.lower() for s in skills if isinstance(s, str)]).most_common()

    if skill_counts:
        lines.append("Основные навыки")
        lines.append("Технологии и инструменты: " + ", ".join(skill for skill, _ in skill_counts))
        lines.append("")

    # --- Опыт проектов (по уже отфильтрованным repos) ---
    project_lines = []
    for repo in repos:
        name = repo.get("name")
        if not name:
            continue

        lang = repo.get("language")
        desc = (repo.get("description") or "").strip()
        readme = (repo.get("readme") or "").strip()

        if not desc and readme:
            lines_from_readme = [line.strip() for line in readme.splitlines() if line.strip()]
            desc = " ".join(lines_from_readme[:2])

        if not desc:
            desc = "Описание отсутствует"

        line = f"{len(project_lines) + 1}. {name}"
        if lang:
            line += f"\n   Язык: {lang}"
        line += f"\n   Краткое описание: {desc}"
        project_lines.append(line)

    if project_lines:
        lines.append("Опыт проектов")
        lines.extend(project_lines)
        lines.append("")

    # --- Инструкция для LLM: "О себе" ---
    lines.append(
        "О себе\nНапиши этот раздел от первого лица. Используй только ту информацию, которая представлена (в профиле GitHub, списке репозиториев и описаниях). "
        "Не добавляй ничего от себя, не выдумывай навыки, интересы или цели. Не обобщай, не пиши шаблонных фраз. "
        "Основа — только факты из предоставленных данных."
    )

    lines.append(
        "Ты профессиональный составитель резюме. Используя данные из GitHub-профиля (включая список репозиториев и содержимое README), "
        "составь качественное, официальное резюме в текстовой форме на русском языке. Не используй markdown и списки, только обычный текст."
        "\n\nСтруктура:\n1. Личная информация\n2. Основные навыки\n3. Опыт проектов (укажи максимум проектов из предоставленного списка)\n4. О себе (от первого лица)"
        "\n\nВажно:\n- Пиши весь текст на русском языке.\n- Не оставляй английские фразы, кроме названий технологий (Java, Spring и т.п.).\n- Никаких шаблонных фраз или домыслов.\n- Только достоверные данные из входа. Не выдумывай вклад или описание."
    )

    return "\n".join(lines)
