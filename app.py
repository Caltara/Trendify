import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Breakout Stock Screener", layout="wide")
st.title("📈 Breakout Stock Screener Dashboard")

st.markdown("Enter a list of stock tickers and Caltara will scan for bullish breakout signals.")

# --- Input Tickers ---
default_tickers = "AAPL,TSLA,NVDA,MSFT,AMD,META,GOOG,AMZN"
tickers_input = st.text_input("Enter comma-separated tickers:", default_tickers)
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

results = []

with st.spinner("📡 Analyzing tickers..."):
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="6mo", interval="1d")
            if df.empty:
                continue

            df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
            df['MACD'] = ta.trend.MACD(df['Close']).macd()
            df['Volume_SMA'] = df['Volume'].rolling(10).mean()
            df['High20'] = df['Close'].rolling(20).max()

            last = df.iloc[-1]

            breakout = (
                last['Close'] > df['High20'].iloc[-2] and
                last['Volume'] > last['Volume_SMA'] and
                50 < last['RSI'] < 70 and
                last['MACD'] > 0
            )

            results.append({
                "Ticker": ticker,
                "Close Price": round(last['Close'], 2),
                "RSI": round(last['RSI'], 1),
                "MACD": round(last['MACD'], 2),
                "Volume": int(last['Volume']),
                "Breakout?": "🚀 Yes" if breakout else "No"
            })
        except Exception as e:
            st.warning(f"Error analyzing {ticker}: {e}")

# --- Display Results ---
if results:
    st.subheader("📊 Screener Results")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results.sort_values(by="Breakout?", ascending=False), use_container_width=True)
else:
    st.info("No valid tickers to analyze.")
