import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Trendify's Reco Report", layout="wide")
st.title("📈 Trendify's Reco Report Dashboard")

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

            # Make sure we drop NaNs after adding indicators
            df.dropna(inplace=True)

            # Calculate indicators as 1D Series
            rsi = ta.momentum.RSIIndicator(close=df['Close']).rsi()
            macd = ta.trend.MACD(close=df['Close']).macd()
            volume_sma = df['Volume'].rolling(10).mean()
            high_20 = df['Close'].rolling(20).max()

            # Get the last value for breakout logic
            last_close = df['Close'].iloc[-1]
            last_rsi = rsi.iloc[-1]
            last_macd = macd.iloc[-1]
            last_volume = df['Volume'].iloc[-1]
            last_volume_sma = volume_sma.iloc[-1]
            last_high_20 = high_20.iloc[-2]  # Yesterday's high

            breakout = (
                last_close > last_high_20 and
                last_volume > last_volume_sma and
                50 < last_rsi < 70 and
                last_macd > 0
            )

            results.append({
                "Ticker": ticker,
                "Close Price": round(last_close, 2),
                "RSI": round(last_rsi, 1),
                "MACD": round(last_macd, 2),
                "Volume": int(last_volume),
                "Breakout?": "🚀 Yes" if breakout else "No"
            })

        except Exception as e:
            st.warning(f"⚠️ Error analyzing {ticker}: {e}")

# --- Display Results ---
if results:
    st.subheader("📊 Screener Results")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results.sort_values(by="Breakout?", ascending=False), use_container_width=True)
else:
    st.info("No valid tickers to analyze.")
