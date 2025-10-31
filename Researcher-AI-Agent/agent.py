from ollama import Client
from dotenv import load_dotenv
from ddgs import DDGS
import os

# Load Environment Variables
load_dotenv()

API_KEY = os.getenv("OLLAMA_API_KEY", "")
Summarizer_MODEL = os.getenv("OLLAMA_GPT_MODEL", "")
Translator_MODEL = os.getenv("OLLAMA_DEEPSEEK_MODEL", "")

# Ollama Client
client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": f"Bearer {API_KEY}"
    }
)

# Agent 1: Search
def search_agent(topic: str, num_results: int = 3) -> str:
    print(f"🔍 Searching for: {topic}")
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(topic, max_results=num_results):
            results.append(f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n")

    return "\n\n".join(results)

# Agent 2: Summarizer
def summarize_agent(text:str) -> str:
    print("🧩 Summarizing search results...")

    response = client.chat(
        model=Summarizer_MODEL,
        messages=[
            {
                "role":"system", 
                "content" : "You are a helpful summarizer. Return the results as a single, continuous piece of prose; do not use tables."
            },
            {
                "role":"user", 
                "content" : f"Summarize the following search results:\n\n{text}"
            }
        ]
    )

    return response.message.content

# Agent 3: Translator
def translator_agent(english_text: str) -> str:
    print("🌐 Translating summary into Persian...")

    response = client.chat(
        model=Translator_MODEL,
        messages=[
            {
                "role": "system", 
                "content" : "You are a professional translator who translates English to fluent Persian. Use natural, clear Farsi with proper punctuation."
            },
            {
                "role":"user", 
                "content" : f"Translate this text to Persian:\n\n{english_text}"
            }
        ]
    )

    return response.message.content

# Agent 4: Writer
def writer_agent(text: str, filename:str):    
    print(f"💾 Writing Persian summary to {filename}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ File saved successfully!")

# Orchestrator
def main():
    topic = input("Enter a topic to research: ")

    # Agent 1
    search_results = search_agent(topic)

    # Agent 2
    summary = summarize_agent(search_results)
    
    # Agent 3
    translated = translator_agent(summary)

    # Agent 4
    writer_agent(translated, "result.txt")

    print("\n🎉 Done! Persian summary saved to result.txt")

# Run
if __name__ == "__main__":
    main()