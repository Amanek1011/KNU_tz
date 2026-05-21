from urllib.parse import urlparse

from services.utils.constants import BRAND_WORDS, SUSPICIOUS_TLDS
from services.utils.helpers import build_result


def inspect_url(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    score = 5
    signals = []

    if parsed.scheme != 'https':
        score += 25
        signals.append('Ссылка использует незащищённый протокол.')
    if '@' in url:
        score += 30
        signals.append('Символ @ может маскировать настоящий домен.')
    if host.count('.') >= 3:
        score += 15
        signals.append('Слишком много поддоменов, это частый приём фишинга.')
    if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS):
        score += 20
        signals.append('Доменная зона часто встречается в одноразовых мошеннических сайтах.')
    if '-' in host:
        score += 10
        signals.append('Дефисы в домене могут имитировать известный бренд.')
    if any(word in host + path for word in BRAND_WORDS) and not host.endswith(('.com', '.kg', '.kz', '.ru')):
        score += 20
        signals.append('В ссылке есть название бренда, но домен выглядит нетипично.')
    if any(token in path for token in ('login', 'verify', 'password', 'bonus', 'gift')):
        score += 15
        signals.append('Путь просит вход, подтверждение или бонус - это стоит проверить вручную.')

    return build_result(score, signals)
