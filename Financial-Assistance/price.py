import json
import requests
from bs4 import BeautifulSoup
from ollama import Client

CHANNEL_USERNAME = "ecogold_ir"
OLLAMA_MODEL = "gpt-oss:20b"
OLLAMA_API_KEY = "***"

# https://t.me/s/ecogold_ir

def fetch_channel_html(username):
    url = f"https://t.me/s/{username}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.text

def find_latest_price_post(html):
    soup = BeautifulSoup(html, "html.parser")    
    posts = soup.select("div.tgme_widget_message_text")
    if not posts:
        return None

    keywords = [
        "طلای ۱۸ عیار", "سکه امامی", "اونس طلا",
        "سکه بهار آزادی", "نیم سکه", "ربع سکه", "تتر"
    ]

    for post in reversed(posts):
        text = post.get_text("\n", strip=True)
        if any(k in text for k in keywords):
            return text

    return posts[-1].get_text("\n", strip=True)

def create_client(api_key):
    return Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"}
    )

def extract_prices(client, text):
    system_prompt = """
        You are an assistant that extracts structured data and writes a short summary.
        Input is a Persian bulletin with prices of gold, coins, and tether.
        Output must be a JSON object with keys:
        {'gold_18k_toman','tether_toman','bahar_azadi_toman','emami_toman',
        'half_toman','quarter_toman','ounce_usd','time_24h','date_jalali'}
        Rules:
        - Valid JSON only
        - Prices as strings with thousand separators
        - Use 'Toman' for Iranian Rial amounts and 'USD' for dollar amounts
        - Missing fields = null
        - Do NOT output Persian currency symbols or text
    """

    user_prompt = f"Extract JSON data from this text:\n{text}"

    while True:
        try:
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return json.loads(response.message.content.strip())
        except json.JSONDecodeError:
            continue

def price_summary(data):
    return "\n".join([
        f"💰 18K Gold: {data.get('gold_18k_toman')}",
        f"💸 Tether: {data.get('tether_toman')}",
        f"🏅 Bahar Azadi: {data.get('bahar_azadi_toman')}",
        f"🥇 Emami Coin: {data.get('emami_toman')}",
        f"🥈 Half Coin: {data.get('half_toman')}",
        f"🥉 Quarter Coin: {data.get('quarter_toman')}",
        f"📈 Ounce Gold: {data.get('ounce_usd')}",
        f"⏰ Time: {data.get('time_24h')}",
        f"📅 Date: {data.get('date_jalali')}"
    ])

def generate_invest_advice(client, prices):
    system_prompt = """
        You are an experienced financial advisor. 
        Provide a short, professional investment advice in English based on 
        the current prices of gold, coins, and Tether (Iranian USD). 
        Consider the global gold price (ounce) 
        and the Tether price as the main reference. 
        Do not create tables. 
        Do not use bold formatting or markdown syntax. 
        Keep the advice concise, clear, and readable as plain text. 
        Mention which assets are worth buying, which are not, 
        and give a brief reasoning for each.
    """

    user_prompt = f"Here are the current prices in JSON:\n{json.dumps(prices)}"

    while True:
        try:
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return response.message.content.strip()
        except Exception:
            continue

def main():
    try:
        html = fetch_channel_html(CHANNEL_USERNAME)
        post = find_latest_price_post(html)
        client = create_client(OLLAMA_API_KEY)
        prices = extract_prices(client, post)
        summary = price_summary(prices)    
        print(summary)

        advice = generate_invest_advice(client, prices)
        print("\n💡 Investment Advice:")
        print(advice)   
    except Exception as e:
        print("Error:", e)
        return


if __name__ == "__main__":
    main()

    
