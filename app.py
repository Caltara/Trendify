import streamlit as st
import yfinance as yf
import pandas as pd
import requests

st.set_page_config(page_title="Trendify: Breakout Screener", layout="wide")
st.title("🚀 Trendify: Breakout Stock Screener")

@st.cache_data(show_spinner=False)
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(requests.get(url).text)
    return tables[0]["Symbol"].tolist()

def check_breakout(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30:
            return None

        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26

        df['Volume_SMA'] = df['Volume'].rolling(10).mean()
        df['High_20'] = df['Close'].rolling(20).max()

        df.dropna(inplace=True)

        last_close = df['Close'].iloc[-1].item()
        last_rsi = df['RSI'].iloc[-1].item()
        last_macd = df['MACD'].iloc[-1].item()
        last_volume = df['Volume'].iloc[-1].item()
        last_volume_sma = df['Volume_SMA'].iloc[-1].item()
        yesterday_high_20 = df['High_20'].iloc[-2].item()

        breakout = (
            last_close > yesterday_high_20 and
            last_volume > last_volume_sma and
            50 < last_rsi < 70 and
            last_macd > 0
        )

        return {
            "Ticker": ticker,
            "Close": round(last_close, 2),
            "RSI": round(last_rsi, 1),
            "MACD": round(last_macd, 2),
            "Volume": int(last_volume),
            "Breakout?": "🚀 Yes" if breakout else "No"
        }

    except Exception:
        return None

# --- Main UI ---

st.header("🔎 Check a Specific Stock")
user_ticker = st.text_input("Enter stock ticker (e.g. AAPL):").upper()

if user_ticker:
    result = check_breakout(user_ticker)
    if result:
        st.write(f"### Analysis for {user_ticker}")
        st.json(result)
    else:
        st.warning("Could not retrieve data for this ticker. Please check the symbol and try again.")

st.markdown("---")

st.header("🔥 Top 5 Potential Breakout Stocks in S&P 500")
tickers = get_sp500_tickers()

results = []
progress = st.progress(0, text="Scanning S&P 500 for breakouts...")

for i, ticker in enumerate(tickers):
    res = check_breakout(ticker)
    if res and res["Breakout?"] == "🚀 Yes":
        results.append(res)
    progress.progress((i + 1) / len(tickers), text=f"Scanning {ticker} ({i+1}/{len(tickers)})")

if results:
    top5 = sorted(results, key=lambda x: x["Close"], reverse=True)[:5]
    df_top5 = pd.DataFrame(top5)
    st.dataframe(df_top5, use_container_width=True)
else:
    st.info("No breakout candidates found in S&P 500 at this time.")
