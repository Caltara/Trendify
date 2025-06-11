import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Breakout Stock Screener", layout="wide")
st.title("📈 Breakout Stock Screener Dashboard")

st.markdown("Upload a list of stock tickers and Caltara will scan for potential bullish breakouts.")

# --- Input ---
default_tickers = "AAPL,TSLA,NVDA,MSFT,AMD,META,GOOG,AMZN"
tickers_input = st.text_input("Enter comma-separated tickers:", default_tickers)
tickers = [ticker.strip().upper() for ticker in tickers_input.split(",")]

results = []

with st.spinner("Analyzing..."):
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="6mo", interval="1d")
            if df.empty: continue
            df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
            df['MACD'] = ta.trend.MACD(df['Close']).macd()
            df['Volume_SMA'] = df['Volume'].rolling(10).mean()
            df['High20'] = df['Close'].rolling(20).max()

            last = df.iloc[-1]

            breakout = (
                last['Close'] > df['High20'].iloc[-2] and
                last['Volume'] > last['Volume_SMA'] and
                last['RSI'] > 50 and last['RSI'] < 70 and
                last['MACD'] > 0
            )

            results.append({
                "Ticker": ticker,
                "Close": round(last['Close'], 2),
                "RSI": round(last['RSI'], 1),
                "MACD": round(last['MACD'], 2),
                "Volume": int(last['Volume']),
                "Breakout?": "🚀 Yes" if breakout else "No"
            })
        except Exception as e:
            st.warning(f"Error processing {ticker}: {e}")

# --- Results ---
if results:
    st.subheader("📊 Screener Results")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results.sort_values("Breakout?", ascending=False), use_container_width=True)
else:
    st.info("No tickers analyzed yet.")
