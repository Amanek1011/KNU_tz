import json
import random
import uuid

from services.ai.groq_service import ask_groq
from services.ai.prompts import GROQ_SECURITY_SYSTEM, TRAINER_PROMPT

from .scenarios import SCENARIOS


def get_scenario(exclude_id=None):
    generated = _generate_with_groq()
    if generated and generated['id'] != exclude_id:
        return generated

    pool = [item for item in SCENARIOS if item['id'] != exclude_id] or SCENARIOS
    return random.choice(pool)


def _generate_with_groq():
    try:
        raw = ask_groq(TRAINER_PROMPT, system_prompt=GROQ_SECURITY_SYSTEM, temperature=0.8)
    except Exception:
        return None
    if not raw:
        return None

    try:
        start = raw.index('{')
        end = raw.rindex('}') + 1
        data = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        return None

    required = ('title', 'text', 'is_fraud', 'feedback')
    if not all(field in data for field in required):
        return None

    return {
        'id': f'groq-{uuid.uuid4().hex}',
        'title': str(data['title'])[:160],
        'text': str(data['text']),
        'is_fraud': bool(data['is_fraud']),
        'feedback': str(data['feedback']),
    }
