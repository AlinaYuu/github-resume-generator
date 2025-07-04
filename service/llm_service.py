import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


def ask_llm(prompt: str) -> str:
    try:
        result = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты профессионально формируешь резюме по GitHub-профилю."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return result.choices[0].message.content.strip()

    except Exception as err:
        return f"Не удалось выполнить запрос LLM: {err}"


def format_resume_output(text: str) -> str:
    output = []

    for line in text.splitlines():
        if line.strip().endswith(":"):
            output.append("")
            output.append(line.upper())
        else:
            output.append(line)
    return "\n".join(output)