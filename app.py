import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="📈 Breakout Stock Screener", layout="wide")
st.title("📊 Trendify's Breakout Stock Screener")

st.markdown("Enter tickers to identify potential bullish breakouts based on price, volume, RSI, and MACD.")

# Input
default_tickers = "AAPL,TSLA,NVDA,MSFT,AMD,META,GOOG,AMZN"
tickers_input = st.text_input("Enter comma-separated tickers:", default_tickers)
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

results = []

with st.spinner("🔍 Scanning stocks..."):
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="6mo", interval="1d")
            if df.empty or len(df) < 30:
                st.warning(f"Not enough data for {ticker}")
                continue

            # Calculate RSI manually
            delta = df['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # Calculate MACD manually
            ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
            ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = ema_12 - ema_26

            # Add volume average and 20-day high
            df['Volume_SMA'] = df['Volume'].rolling(10).mean()
            df['High_20'] = df['Close'].rolling(20).max()

            df.dropna(inplace=True)

            # Extract scalar values to avoid Series errors
            last_close = df['Close'].iloc[-1].item()
            last_rsi = df['RSI'].iloc[-1].item()
            last_macd = df['MACD'].iloc[-1].item()
            last_volume = df['Volume'].iloc[-1].item()
            last_volume_sma = df['Volume_SMA'].iloc[-1].item()
            yesterday_high_20 = df['High_20'].iloc[-2].item()

            # Breakout logic
            breakout = (
                last_close > yesterday_high_20 and
                last_volume > last_volume_sma and
                50 < last_rsi < 70 and
                last_macd > 0
            )

            results.append({
                "Ticker": ticker,
                "Close": round(last_close, 2),
                "RSI": round(last_rsi, 1),
                "MACD": round(last_macd, 2),
                "Volume": int(last_volume),
                "Breakout?": "🚀 Yes" if breakout else "No"
            })

        except Exception as e:
            st.error(f"⚠️ Error analyzing {ticker}: {e}")

# Display results
if results:
    st.subheader("📋 Results")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results.sort_values(by="Breakout?", ascending=False), use_container_width=True)
else:
    st.info("Enter tickers above to begin.")
