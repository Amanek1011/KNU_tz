import re

from services.ai.groq_service import ask_groq
from services.ai.groq_service import ask_groq_json
from services.ai.prompts import GROQ_SECURITY_SYSTEM, TEXT_ANALYSIS_PROMPT
from services.utils.constants import URGENT_WORDS
from services.utils.helpers import build_result


def inspect_text(text):
    lowered = text.lower()
    score = 5
    signals = []

    matched = sorted(word for word in URGENT_WORDS if word in lowered)
    if matched:
        score += min(40, len(matched) * 10)
        signals.append(f'Найдены тревожные слова: {", ".join(matched[:5])}.')
    if re.search(r'\b\d{4,8}\b', text):
        score += 15
        signals.append('Сообщение содержит код или числовой идентификатор.')
    if re.search(r'https?://|www\.', lowered):
        score += 15
        signals.append('В тексте есть ссылка, её нужно проверять отдельно через URL Checker.')
    if any(phrase in lowered for phrase in (
        'не сообщайте никому',
        'сообщите код',
        'подтвердите личность',
        'limited time',
    )):
        score += 25
        signals.append('Текст пытается получить код, личные данные или торопит с решением.')
    if text.count('!') >= 3 or text.isupper():
        score += 10
        signals.append('Агрессивная подача часто используется для давления на жертву.')

    groq_result = _ask_groq_for_text_analysis(text)
    if groq_result:
        score = _merge_scores(local_score=score, groq_score=groq_result['risk_score'])
        signals.append(f'Groq: {groq_result["explanation"]}')
    else:
        signals.append('Groq недоступен: использована локальная эвристика анализа текста.')

    return build_result(score, signals)


def _ask_groq_for_text_analysis(text):
    prompt = (
        f'{TEXT_ANALYSIS_PROMPT}\n\n'
        'Верни только JSON без markdown:\n'
        '{\n'
        '  "risk_score": число от 0 до 100,\n'
        '  "verdict": "low" или "medium" или "high",\n'
        '  "explanation": "2-3 коротких предложения по-русски"\n'
        '}\n\n'
        'Оцени риск строго: обычное информативное сообщение без ссылки, давления, кода, '
        'пароля или платежа должно быть 0-25. Просьба назвать код, пароль, перейти по '
        'сомнительной ссылке или срочно оплатить должна быть 70-100.\n\n'
        f'Текст:\n{text}'
    )
    try:
        result = ask_groq_json(prompt, system_prompt=GROQ_SECURITY_SYSTEM)
    except Exception:
        return None

    if not result or 'risk_score' not in result or 'explanation' not in result:
        return None

    return {
        'risk_score': max(0, min(100, int(result['risk_score']))),
        'explanation': str(result['explanation']).strip(),
    }


def _merge_scores(local_score, groq_score):
    if groq_score >= 70 or local_score >= 70:
        return round(max(local_score, groq_score) * 0.75 + min(local_score, groq_score) * 0.25)
    return round(local_score * 0.35 + groq_score * 0.65)
