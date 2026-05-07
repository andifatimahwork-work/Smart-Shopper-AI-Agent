from functools import lru_cache

from openai import OpenAI

from .settings import get_settings, require_env


@lru_cache(maxsize=1)
def get_groq_client() -> OpenAI:
    settings = get_settings()
    require_env("GROQ_API_KEY", settings["groq_api_key"])
    return OpenAI(
        api_key=settings["groq_api_key"],
        base_url="https://api.groq.com/openai/v1",
    )


def generate_text(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    settings = get_settings()
    response = get_groq_client().chat.completions.create(
        model=settings["groq_model"],
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""
