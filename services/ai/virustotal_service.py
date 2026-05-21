import requests
import os
import time

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VT_API_KEY")

headers = {
    "x-apikey": API_KEY
}


def scan_url(url):

    response = requests.post(

        "https://www.virustotal.com/api/v3/urls",

        headers=headers,

        data={
            "url": url
        }
    )

    analysis_id = response.json()["data"]["id"]

    time.sleep(3)

    result_response = requests.get(

        f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",

        headers=headers
    )

    result = result_response.json()

    stats = result["data"]["attributes"]["stats"]

    return {
        "malicious": stats["malicious"],
        "suspicious": stats["suspicious"],
        "harmless": stats["harmless"],
    }


print(
    scan_url("https://google.com")
)