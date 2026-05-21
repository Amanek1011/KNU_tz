import os
import warnings
from functools import lru_cache

from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted
from google import genai
from google.genai import types

load_dotenv()

DEFAULT_GEMINI_MODEL = 'gemini-2.0-flash'


@lru_cache
def _client():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def analyze_image(uploaded_file, prompt):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None

    data = _read_uploaded_file(uploaded_file)
    mime_type = getattr(uploaded_file, 'content_type', None) or 'image/jpeg'
    model = os.getenv('GEMINI_MODEL', DEFAULT_GEMINI_MODEL)

    try:
        return _analyze_with_google_genai(data, mime_type, prompt, model)
    except ResourceExhausted as exc:
        raise GeminiQuotaError from exc
    except (GoogleAPIError, ValueError, AttributeError):
        return _analyze_with_legacy_sdk(data, mime_type, prompt, model, api_key)


def _read_uploaded_file(uploaded_file):
    uploaded_file.seek(0)
    data = uploaded_file.read()
    uploaded_file.seek(0)
    return data


def _analyze_with_google_genai(data, mime_type, prompt, model):
    client = _client()
    if client is None:
        return None

    image_part = types.Part.from_bytes(data=data, mime_type=mime_type)
    response = client.models.generate_content(
        model=model,
        contents=[prompt, image_part],
        config=types.GenerateContentConfig(
            max_output_tokens=220,
            temperature=0.2,
        ),
    )
    return response.text


def _analyze_with_legacy_sdk(data, mime_type, prompt, model, api_key):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', FutureWarning)
        import google.generativeai as legacy_genai

        legacy_genai.configure(api_key=api_key)
        legacy_model = legacy_genai.GenerativeModel(model)
        response = legacy_model.generate_content([
            prompt,
            {'mime_type': mime_type, 'data': data},
        ])
    return response.text


class GeminiQuotaError(Exception):
    pass
