from services.utils.helpers import build_result
from services.utils.validators import file_kind


def inspect_media(uploaded_file):
    kind = file_kind(uploaded_file)
    size_mb = uploaded_file.size / (1024 * 1024)
    name = uploaded_file.name.lower()
    score = 20
    signals = []

    if kind == 'unknown':
        score += 35
        signals.append('Тип файла не похож на стандартное фото или видео.')
    if size_mb > 25:
        score += 10
        signals.append('Файл крупный, для точной проверки лучше подключить модель анализа кадров.')
    if any(token in name for token in ('deepfake', 'face_swap', 'ai', 'generated')):
        score += 20
        signals.append('Имя файла содержит признаки синтетического происхождения.')
    if kind == 'image':
        signals.append('Для MVP выполнена базовая проверка метаданных изображения.')
    if kind == 'video':
        score += 10
        signals.append('Видео требует покадрового анализа, текущий результат предварительный.')

    if not signals:
        signals.append('Файл принят. Подключите Hugging Face модель для полноценной детекции дипфейков.')

    return build_result(score, signals)
