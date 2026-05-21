import re

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
        signals.append('В тексте есть ссылка, её нужно проверять отдельно.')
    if any(phrase in lowered for phrase in ('не сообщайте никому', 'сообщите код', 'подтвердите личность', 'limited time')):
        score += 25
        signals.append('Текст пытается получить код, личные данные или торопит с решением.')
    if text.count('!') >= 3 or text.isupper():
        score += 10
        signals.append('Агрессивная подача часто используется для давления на жертву.')

    return build_result(score, signals)
