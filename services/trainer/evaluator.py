from .scenarios import SCENARIOS


def evaluate_answer(scenario_id, answer):
    scenario = next(item for item in SCENARIOS if item['id'] == scenario_id)
    user_answer = answer == 'fraud'
    is_correct = scenario['is_fraud'] == user_answer
    prefix = 'Верно.' if is_correct else 'Не совсем.'
    return {
        'title': scenario['title'],
        'text': scenario['text'],
        'correct_answer': scenario['is_fraud'],
        'user_answer': user_answer,
        'is_correct': is_correct,
        'feedback': f'{prefix} {scenario["feedback"]}',
    }
