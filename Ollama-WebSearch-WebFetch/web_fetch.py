from ollama import Client
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

try:
    client = Client(
        headers={'Authorization': f'Bearer {API_KEY}'}
    )

    response = client.web_fetch("https://docs.ollama.com/")
    print(response.get('title', 'No title'))
    print(response.get('content', 'No content available')[:200])
    print(response.get('links', 'No links'))

except Exception as e:
    print(f"Error: {e}")
    