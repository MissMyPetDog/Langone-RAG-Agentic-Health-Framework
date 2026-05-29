"""NYU Kong GPT-4o client (OpenAI SDK compatible)."""
from openai import OpenAI
from . import config


def get_client():
    return OpenAI(
        base_url=config.BASE_URL,
        api_key=config.KONG_API_KEY,
        default_headers={"api-key": config.KONG_API_KEY},
    )


def chat(client, system, user):
    resp = client.chat.completions.create(
        model=config.MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content
