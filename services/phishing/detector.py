from .text_analyzer import inspect_text
from .url_analyzer import inspect_url


def analyze_url(url):
    return inspect_url(url)


def analyze_text(text):
    return inspect_text(text)
