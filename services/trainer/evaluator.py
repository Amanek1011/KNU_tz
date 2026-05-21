from services.ai.groq_service import ask_groq
from services.ai.prompts import GROQ_SECURITY_SYSTEM

from .scenarios import SCENARIOS


def evaluate_answer(scenario_id, answer, scenario=None):
    scenario = scenario or _find_scenario(scenario_id)
    user_answer = answer == 'fraud'
    is_correct = scenario['is_fraud'] == user_answer
    prefix = 'Верно.' if is_correct else 'Не совсем.'
    feedback = _build_groq_feedback(scenario, user_answer) or scenario['feedback']

    return {
        'title': scenario['title'],
        'text': scenario['text'],
        'correct_answer': scenario['is_fraud'],
        'user_answer': user_answer,
        'is_correct': is_correct,
        'feedback': f'{prefix} {feedback}',
    }


def _find_scenario(scenario_id):
    if scenario_id.startswith('groq-'):
        return {
            'title': 'Сценарий Groq',
            'text': 'Динамический сценарий был сгенерирован Groq.',
            'is_fraud': True,
            'feedback': 'Оценивайте давление, просьбу о кодах, подозрительные ссылки и несоответствие отправителя.',
        }
    return next(item for item in SCENARIOS if item['id'] == scenario_id)


def _build_groq_feedback(scenario, user_answer):
    prompt = (
        'Объясни ответ пользователя в тренажёре cybersecurity. '
        'Верни 1-2 коротких предложения с признаками, почему сценарий опасен или безопасен.\n\n'
        f'Сценарий: {scenario["text"]}\n'
        f'Правильный класс: {"мошенничество" if scenario["is_fraud"] else "безопасно"}\n'
        f'Ответ пользователя: {"мошенничество" if user_answer else "безопасно"}'
    )
    try:
        return ask_groq(prompt, system_prompt=GROQ_SECURITY_SYSTEM)
    except Exception:
        return None
