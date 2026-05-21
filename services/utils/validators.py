from urllib.parse import urlparse


def normalize_domain(url):
    parsed = urlparse(url)
    return parsed.netloc.lower().removeprefix('www.')


def file_kind(uploaded_file):
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type.startswith('image/'):
        return 'image'
    if content_type.startswith('video/'):
        return 'video'
    return 'unknown'
