from groq import Groq

from dotenv import load_dotenv
import os

load_dotenv()


client = Groq(
    api_key=os.getenv('GROQ_API_KEY')
)

def ask_groq(prompt):

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],

        model="llama-3.1-8b-instant",
    )

    return chat_completion.choices[0].message.content

