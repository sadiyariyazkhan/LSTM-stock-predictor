import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

st.title("📈 Stock Price Prediction from CSV")

uploaded_file = st.file_uploader("Upload your CSV", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file, parse_dates=['Date']).sort_values('Date')
    st.write(data.head())

    close_prices = data['Close'].values.reshape(-1,1)
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(close_prices)

    seq_length = 60
    X_test = []
    for i in range(seq_length, len(scaled_data)):
        X_test.append(scaled_data[i-seq_length:i, 0])
    X_test = np.array(X_test).reshape(-1, seq_length, 1)

    model = load_model("/content/lstm_portfolio_model.h5")
    predicted_prices = model.predict(X_test)
    predicted_prices = scaler.inverse_transform(predicted_prices)

    st.line_chart(pd.DataFrame({
        "Actual": data['Close'][seq_length:].values,
        "Predicted": predicted_prices.flatten()
    }))
