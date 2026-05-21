import os
import time

from dotenv import load_dotenv
import requests

load_dotenv()


def scan_url(url):
    api_key = os.getenv('VT_API_KEY')
    if not api_key:
        return None

    headers = {'x-apikey': api_key}
    response = requests.post(
        'https://www.virustotal.com/api/v3/urls',
        headers=headers,
        data={'url': url},
        timeout=15,
    )
    response.raise_for_status()
    analysis_id = response.json()['data']['id']

    time.sleep(3)

    result_response = requests.get(
        f'https://www.virustotal.com/api/v3/analyses/{analysis_id}',
        headers=headers,
        timeout=15,
    )
    result_response.raise_for_status()

    stats = result_response.json()['data']['attributes']['stats']
    return {
        'malicious': stats.get('malicious', 0),
        'suspicious': stats.get('suspicious', 0),
        'harmless': stats.get('harmless', 0),
        'undetected': stats.get('undetected', 0),
    }


def scan_file(uploaded_file):
    api_key = os.getenv('VT_API_KEY')
    if not api_key:
        return None

    headers = {'x-apikey': api_key}
    uploaded_file.seek(0)
    response = requests.post(
        'https://www.virustotal.com/api/v3/files',
        headers=headers,
        files={'file': (uploaded_file.name, uploaded_file.read())},
        timeout=45,
    )
    uploaded_file.seek(0)
    response.raise_for_status()
    analysis_id = response.json()['data']['id']

    time.sleep(5)

    result_response = requests.get(
        f'https://www.virustotal.com/api/v3/analyses/{analysis_id}',
        headers=headers,
        timeout=15,
    )
    result_response.raise_for_status()

    stats = result_response.json()['data']['attributes']['stats']
    return {
        'malicious': stats.get('malicious', 0),
        'suspicious': stats.get('suspicious', 0),
        'harmless': stats.get('harmless', 0),
        'undetected': stats.get('undetected', 0),
        'type_unsupported': stats.get('type-unsupported', 0),
    }
