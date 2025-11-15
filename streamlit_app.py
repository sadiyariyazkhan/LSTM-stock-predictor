# ---------------------------------------------------------
# streamlit_app.py - Portfolio Dashboard using CSV
# ---------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="📈 Stock Portfolio Dashboard", layout="wide")
st.title("📊 Stock Portfolio Dashboard (Wide-format CSV)")

# -------------------------------
# Upload CSV
# -------------------------------
uploaded_file = st.file_uploader("Upload your portfolio_data.csv", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    
    # Sidebar controls
    st.sidebar.header("Portfolio Settings")
    
    # Date filter
    start_date = st.sidebar.date_input("Start Date", df.index.min())
    end_date = st.sidebar.date_input("End Date", df.index.max())
    
    df_filtered = df.loc[(df.index >= pd.to_datetime(start_date)) & 
                         (df.index <= pd.to_datetime(end_date))]

    # Technical indicators toggle
    st.sidebar.header("Technical Indicators")
    show_sma = st.sidebar.checkbox("Simple Moving Average (SMA, 20 days)")
    show_ema = st.sidebar.checkbox("Exponential Moving Average (EMA, 20 days)")
    
    tickers = df_filtered.columns.tolist()

    # -------------------------------
    # Plotting
    # -------------------------------
    fig = go.Figure()
    
    for ticker in tickers:
        fig.add_trace(go.Scatter(
            x=df_filtered.index, y=df_filtered[ticker], 
            name=ticker, mode='lines'
        ))
        
        # SMA
        if show_sma:
            sma = df_filtered[ticker].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=df_filtered.index, y=sma,
                name=f"{ticker} SMA(20)", mode='lines', line=dict(dash='dash')
            ))
        
        # EMA
        if show_ema:
            ema = df_filtered[ticker].ewm(span=20, adjust=False).mean()
            fig.add_trace(go.Scatter(
                x=df_filtered.index, y=ema,
                name=f"{ticker} EMA(20)", mode='lines', line=dict(dash='dot')
            ))
    
    fig.update_layout(
        title="Portfolio Stock Prices",
        xaxis_title="Date",
        yaxis_title="Price",
        legend_title="Ticker",
        template="plotly_white",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # -------------------------------
    # Summary Statistics
    # -------------------------------
    st.header("📑 Summary Statistics")
    st.dataframe(df_filtered.describe())
else:
    st.info("Please upload your portfolio_data.csv file to start.")
