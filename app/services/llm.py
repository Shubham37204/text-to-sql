from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def load_system_prompt(schema: str) -> str:
    with open("prompts/system.txt", "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(schema=schema)


def generate_sql(question: str, schema: str, history: list[dict] = []) -> str:
    system_prompt = load_system_prompt(schema)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        lines = lines[1:-1]
        content = "\n".join(lines).strip()

    return content.strip()