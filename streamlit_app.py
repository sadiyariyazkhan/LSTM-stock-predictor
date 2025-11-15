import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

st.title("📈 Multi-Stock Price Prediction from CSV")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Columns in your CSV:", data.columns.tolist())
    
    # Let user select which stock to predict
    stock_column = st.selectbox("Select stock for prediction", data.columns.tolist())
    st.write(f"Predicting stock: **{stock_column}**")
    
    prices = data[stock_column].values.reshape(-1,1)
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(prices)
    
    # Prepare sequences for prediction
    seq_length = 60
    X_test = []
    for i in range(seq_length, len(scaled_data)):
        X_test.append(scaled_data[i-seq_length:i, 0])
    X_test = np.array(X_test).reshape(-1, seq_length, 1)
    
    # Load model (make sure you have a trained model for this stock)
    model_path = f"/content/lstm_model_{stock_column}.h5"
    try:
        model = load_model(model_path)
    except:
        st.error(f"No trained model found for {stock_column}. Please train or provide {model_path}")
        st.stop()
    
    predicted_prices = model.predict(X_test)
    predicted_prices = scaler.inverse_transform(predicted_prices)
    
    # Plot actual vs predicted
    st.line_chart(pd.DataFrame({
        "Actual": data[stock_column][seq_length:].values,
        "Predicted": predicted_prices.flatten()
    }))
