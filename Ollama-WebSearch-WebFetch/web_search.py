from ollama import Client
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

try:
    client = Client(
        headers={'Authorization': f'Bearer {API_KEY}'}
    )

    response = client.web_search(
        query="What is the capital of France?",
        max_results=3
    )
    
    if hasattr(response, 'results'):
        print(f'Found {len(response.results)} results.')

        for result in response.results:
            print(result.get('title', 'No title'))
            print(result.get('url', 'No URL'))
            if (result.get('content')):
                content_preview = result.get('content')[:200] + '...'
            else:
                content_preview = 'No content preview available'
            print(content_preview)
            print('-' * 40)
    else:
        print("No results found.")
except Exception as e:
    print(f"Error: {e}")
    