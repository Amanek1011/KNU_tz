from services.ai.virustotal_service import scan_file
from services.utils.helpers import build_result
from services.utils.validators import file_kind


MAX_DIRECT_SCAN_MB = 32


def inspect_media(uploaded_file):
    kind = file_kind(uploaded_file)
    size_mb = uploaded_file.size / (1024 * 1024)
    name = uploaded_file.name.lower()
    score = 5
    signals = []

    if size_mb > MAX_DIRECT_SCAN_MB:
        score += 20
        signals.append(
            f'Файл больше {MAX_DIRECT_SCAN_MB} MB. Обычная загрузка в VirusTotal может быть недоступна; '
            'проверьте файл вручную или уменьшите размер.'
        )
        return build_result(score, signals)

    vt_stats = _scan_with_virustotal(uploaded_file)
    if vt_stats:
        malicious = vt_stats['malicious']
        suspicious = vt_stats['suspicious']
        score += min(85, malicious * 25 + suspicious * 12)
        signals.append(
            'VirusTotal file scan: '
            f'{malicious} malicious, {suspicious} suspicious, '
            f'{vt_stats["harmless"]} harmless, {vt_stats["undetected"]} undetected.'
        )
    else:
        signals.append('VirusTotal недоступен или не настроен: выполнена локальная проверка файла.')

    if kind == 'unknown':
        score += 15
        signals.append('Тип файла не распознан браузером, проверьте расширение и источник.')
    if any(token in name for token in ('invoice', 'password', 'free', 'bonus', 'gift', 'scam', 'crack')):
        score += 15
        signals.append('Имя файла содержит слова, часто встречающиеся в мошеннических вложениях.')
    if name.endswith(('.exe', '.scr', '.bat', '.cmd', '.js', '.vbs', '.ps1', '.apk')):
        score += 25
        signals.append('Файл имеет исполняемое или потенциально опасное расширение.')

    return build_result(score, signals)


def _scan_with_virustotal(uploaded_file):
    try:
        return scan_file(uploaded_file)
    except Exception:
        return None
