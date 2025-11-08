from ollama import Client

OLLAMA_MODEL = "gpt-oss:120b-cloud"
OLLAMA_API_KEY = "***"

def create_client(api_key):
    return Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"}
    )

def ask_ollama(client, prompt):
    try:
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": """
                        Answer briefly and to the point. 
                        Avoid unnecessary explanations.
                    """
                },
                {"role": "user", "content": prompt}
            ],
        )
        
        return response.message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    client = create_client(OLLAMA_API_KEY)
    
    print("🤖 Type exit to quit")

    while True:
        user_input = input("👤 You: ")
        if user_input.lower() == "exit":
            print("👋 Bye!")
            break

        response = ask_ollama(client, user_input)
        print("🧠 AI:", response)

if __name__ == "__main__":
    main()
        
