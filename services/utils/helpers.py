def build_result(score, signals):
    score = max(0, min(100, int(score)))
    if score >= 70:
        verdict = 'Высокий риск'
    elif score >= 40:
        verdict = 'Подозрительно'
    else:
        verdict = 'Низкий риск'

    explanation = ' '.join(signals) if signals else 'Критичных признаков угрозы не найдено.'
    return {'verdict': verdict, 'risk_score': score, 'explanation': explanation}
