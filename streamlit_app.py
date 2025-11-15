# ---------------------------------------------------------
# streamlit_app.py - Portfolio Dashboard using CSV
# ---------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import talib

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="📊 Stock Portfolio Dashboard",
    layout="wide"
)
st.title("📈 Stock Portfolio Dashboard (CSV)")

# -------------------------------
# Sidebar Inputs
# -------------------------------
st.sidebar.header("Portfolio Settings")

uploaded_file = st.sidebar.file_uploader("Upload your portfolio_data.csv", type=["csv"])
if not uploaded_file:
    st.warning("Please upload your CSV file to continue.")
    st.stop()

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

st.sidebar.subheader("Technical Indicators")
show_sma = st.sidebar.checkbox("SMA (20)", value=True)
show_ema = st.sidebar.checkbox("EMA (20)", value=True)
show_rsi = st.sidebar.checkbox("RSI (14)", value=False)
show_macd = st.sidebar.checkbox("MACD", value=False)

# -------------------------------
# Load CSV
# -------------------------------
@st.cache_data(ttl=3600)
def load_data(file):
    df = pd.read_csv(file, parse_dates=['Date'])
    df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    return df

df = load_data(uploaded_file)
tickers = df['Ticker'].unique()

# -------------------------------
# Technical Indicators
# -------------------------------
def add_indicators(df_stock):
    df_stock = df_stock.sort_values('Date')
    if show_sma:
        df_stock['SMA20'] = df_stock['Close'].rolling(window=20).mean()
    if show_ema:
        df_stock['EMA20'] = df_stock['Close'].ewm(span=20, adjust=False).mean()
    if show_rsi:
        df_stock['RSI'] = talib.RSI(df_stock['Close'], timeperiod=14)
    if show_macd:
        macd, macdsignal, macdhist = talib.MACD(df_stock['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        df_stock['MACD'] = macd
        df_stock['MACD_signal'] = macdsignal
    return df_stock

# -------------------------------
# Main Dashboard
# -------------------------------
portfolio_data = {}
for ticker in tickers:
    df_stock = df[df['Ticker'] == ticker].copy()
    df_stock = add_indicators(df_stock)
    portfolio_data[ticker] = df_stock

# -------------------------------
# Tabs for each stock
# -------------------------------
tabs = st.tabs(tickers)
for i, ticker in enumerate(tickers):
    with tabs[i]:
        df_stock = portfolio_data[ticker]
        st.subheader(f"{ticker} Price Chart")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_stock['Date'], y=df_stock['Close'], name="Close", line=dict(color='blue')))
        if show_sma and 'SMA20' in df_stock.columns:
            fig.add_trace(go.Scatter(x=df_stock['Date'], y=df_stock['SMA20'], name="SMA20", line=dict(color='orange')))
        if show_ema and 'EMA20' in df_stock.columns:
            fig.add_trace(go.Scatter(x=df_stock['Date'], y=df_stock['EMA20'], name="EMA20", line=dict(color='green')))
        fig.update_layout(height=400, xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)

        if show_rsi and 'RSI' in df_stock.columns:
            st.subheader("RSI (14)")
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df_stock['Date'], y=df_stock['RSI'], name="RSI", line=dict(color='purple')))
            fig_rsi.update_layout(height=250, yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig_rsi, use_container_width=True)

        if show_macd and 'MACD' in df_stock.columns:
            st.subheader("MACD")
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=df_stock['Date'], y=df_stock['MACD'], name="MACD", line=dict(color='blue')))
            fig_macd.add_trace(go.Scatter(x=df_stock['Date'], y=df_stock['MACD_signal'], name="Signal", line=dict(color='red')))
            st.plotly_chart(fig_macd, use_container_width=True)

# -------------------------------
# Portfolio Summary
# -------------------------------
st.header("📊 Portfolio Summary")
portfolio_close = pd.DataFrame({ticker: data['Close'].values for ticker, data in portfolio_data.items()},
                               index=portfolio_data[tickers[0]]['Date'])
st.line_chart(portfolio_close)
st.dataframe(portfolio_close.tail())

st.success("✅ Dashboard Loaded Successfully")
