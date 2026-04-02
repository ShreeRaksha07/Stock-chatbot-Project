import streamlit as st
import requests
import yfinance as yf

# -----------------------------------
# Page Config
# -----------------------------------

st.set_page_config(page_title="AI Stock Assistant", page_icon="📈")
st.title("📈 AI Share Market Assistant")
st.write("Ask about stocks, charts, market trends, and news!")

# -----------------------------------
# Chat History
# -----------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------
# Ollama Function
# -----------------------------------

def get_ai_response(user_input):

    url = "http://localhost:11434/api/generate"

    system_prompt = """
    You are a beginner-friendly stock market assistant.
    Explain clearly and simply.
    """

    prompt = system_prompt + "\nUser: " + user_input

    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=60)

        # 🔥 DEBUG PRINT (important)
        print("Status:", response.status_code)
        print("Raw:", response.text)

        if response.status_code == 200:
            data = response.json()

            # 🔥 FIX: correct key handling
            if "response" in data:
                return data["response"]

            else:
                return "⚠️ Model responded but no text found"

        else:
            return f"⚠️ Server error: {response.status_code}"

    except Exception as e:
        return f"⚠️ Connection error: {str(e)}"
# -----------------------------------
# Fetch Stock Price
# -----------------------------------

def get_stock_price(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")

    if not data.empty:
        price = data["Close"].iloc[-1]
        return price
    else:
        return None

# -----------------------------------
# Fetch Stock Chart
# -----------------------------------

def get_stock_chart(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")
    return data

# -----------------------------------
# Simple Intent Detection
# -----------------------------------

def detect_intent(user_input):
    user_input = user_input.lower()

    if "price" in user_input:
        return "price"
    elif "chart" in user_input:
        return "chart"
    elif "news" in user_input:
        return "news"
    else:
        return "ai"

# -----------------------------------
# Extract Stock Symbol (Simple)
# -----------------------------------


def extract_symbol(user_input):
    words = user_input.upper().split()

    # Known common stock symbols
    known_symbols = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", "TCS", "INFY"]

    for word in words:
        if word in known_symbols:
            return word

    # fallback: return last word
    return words[-1]

# -----------------------------------
# Display Chat History
# -----------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------------
# User Input
# -----------------------------------

user_input = st.chat_input("Ask about stocks...")

if user_input:

    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    intent = detect_intent(user_input)
    symbol = extract_symbol(user_input)

    response_text = ""

    # -----------------------------------
    # Handle Price
    # -----------------------------------

    if intent == "price":
        price = get_stock_price(symbol)

        if price:
            response_text = f"📊 Current price of {symbol} is ₹{round(price,2)}"
        else:
            response_text = "⚠️ Could not fetch stock price."

    # -----------------------------------
    # Handle Chart
    # -----------------------------------

    elif intent == "chart":
        data = get_stock_chart(symbol)

        if not data.empty:
            st.line_chart(data["Close"])
            response_text = f"📈 Showing 1-month chart for {symbol}"
        else:
            response_text = "⚠️ Could not fetch chart."

    # -----------------------------------
    # Handle News (Basic Placeholder)
    # -----------------------------------

    elif intent == "news":
        response_text = "📰 Market news feature can be added using News API."

    # -----------------------------------
    # Default → AI Response
    # -----------------------------------

    else:
        response_text = get_ai_response(user_input)

    # Show assistant response
    with st.chat_message("assistant"):
        st.markdown(response_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text
    })
