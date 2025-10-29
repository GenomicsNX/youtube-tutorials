import os
import requests
from ollama import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OLLAMA_API_KEY")
MODEL = os.getenv("OLLAMA_MODEL")


def get_current_weather(city: str) -> str:
    """Get the current weather in a given city"""
    base_url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(base_url)
    data = response.json()
    return f"The current temperature in {city} is: {data['current_condition'][0]['temp_C']}°C"


def create_text_file(filename: str, content: str):
    """Create a text file with the given content"""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": f"Bearer {API_KEY}"
    }
)

def aks_ollama(prompt: str) -> str:
    """Send a message to the Ollama model to detect tool usage"""
    messages = [
        {
            "role": "system",
            "content": "You are an intelligent assistant that can use available functions to provide more accurate answers.",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city to get the weather for",
                        },
                    },
                    "required": ["city"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_text_file",
                "description": "Create a text file with the given content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The name of the file to create",
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write in the file",
                        },
                    },
                    "required": ["filename", "content"],
                },
            },
        },
    ]

    try:
        result = client.chat(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
    except Exception as e:
        return f"Error: {e}"

    return result
    

def chat(prompt: str) -> str:
    """Send a message to the Ollama model and return the response"""
    response = aks_ollama(prompt)
    
    tools_calls = response.message.tool_calls
    # print(tools_calls)

    if tools_calls:
        for tool_call in tools_calls:
            function_name = tool_call.function.name
            print(function_name)
            arguments = tool_call.function.arguments
            print(arguments)

            if function_name == "get_current_weather":
                city = arguments.get("city")
                weather = get_current_weather(city)
                print(f"🔍 Weather Result: {weather}")

            elif function_name == "create_text_file":
                filename = arguments.get("filename")
                content = arguments.get("content")
                create_text_file(filename, content)
                print(f"📝 File Created: {filename}")

# Test    
chat("What is the weather in Tehran?")
chat("Create a file named 'test.txt' with the content 'Hello, World!'")
chat("Create a file named 'paris.txt' with the content about Paris")