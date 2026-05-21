GROQ_SECURITY_SYSTEM = (
    'Ты cybersecurity-ассистент CyberShield AI. Анализируй фишинг, scam, fake news, '
    'социальную инженерию и подозрительные сообщения. Отвечай кратко, по-русски, '
    'без советов выполнять опасные действия.'
)

TEXT_ANALYSIS_PROMPT = (
    'Проанализируй текст как email, SMS или scam-сообщение. Найди признаки фишинга, '
    'мошенничества, fake/scam манипуляций и объясни риск простым языком.'
)

TRAINER_PROMPT = (
    'Создай один учебный сценарий для тренажёра cybersecurity: fake email, phishing '
    'scenario или scam simulation. Верни только JSON с полями title, text, is_fraud, feedback.'
)

IMAGE_ANALYSIS_PROMPT = (
    'Проанализируй изображение как возможный scam screenshot, fake screenshot, '
    'подозрительный профиль или мошенническое изображение. Опиши признаки риска, '
    'что проверить вручную и насколько это похоже на обман.'
)
