import os
import json
from functools import lru_cache

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


@lru_cache
def _client():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return None
    return Groq(api_key=api_key)


def ask_groq(prompt, system_prompt=None, temperature=0.2):
    client = _client()
    if client is None:
        return None

    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant'),
        temperature=temperature,
    )
    return chat_completion.choices[0].message.content


def ask_groq_json(prompt, system_prompt=None, temperature=0.1):
    response = ask_groq(prompt, system_prompt=system_prompt, temperature=temperature)
    if not response:
        return None

    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return None
