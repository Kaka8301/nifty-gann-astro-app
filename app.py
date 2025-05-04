
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import swisseph as swe
from pyswisseph.datetime import Datetime
from pyswisseph.geopos import GeoPos
from pyswisseph import const
import matplotlib.pyplot as plt

# App title
st.set_page_config(page_title="🔮 Nifty Gann + Astrology Predictor", layout="wide")
st.title("🔮 Nifty 1-min Gann + Astrology Forecast")

# Select mode
mode = st.radio("Choose mode:", ["Forecast Future", "Backtest with CSV"])

# Inputs
timezone = '+05:30'
latitude = '19.0760'
longitude = '72.8777'

def get_moon_sign(dt):
    date = Datetime(dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M'), timezone)
    pos = GeoPos(latitude, longitude)
    chart = Chart(date, pos)
    moon = chart.get(const.MOON)
    return moon.sign

def get_gann_times(start_time, intervals=[30,60,90,120,150,180,210]):
    return [start_time + timedelta(minutes=i) for i in intervals]

def generate_signals(start_time, end_time):
    minutes = pd.date_range(start=start_time, end=end_time, freq='1min')
    gann_times = get_gann_times(start_time)
    rows = []

    for t in minutes:
        moon_sign = get_moon_sign(t)
        is_gann = t in gann_times
        signal = ''
        if is_gann and moon_sign in ['ARIES', 'SCORPIO']:
            signal = 'BUY'
        elif is_gann and moon_sign in ['CAPRICORN', 'VIRGO']:
            signal = 'SELL'
        elif is_gann:
            signal = 'REVERSAL'
        if signal:
            rows.append({'Datetime': t, 'Time': t.strftime('%H:%M'), 'Moon Sign': moon_sign, 'Signal': signal})
    return pd.DataFrame(rows)

if mode == "Forecast Future":
    forecast_date = st.date_input("Select forecast date", datetime.today())
    if st.button("Generate Forecast"):
        start_time = datetime.combine(forecast_date, datetime.strptime('09:15', '%H:%M').time())
        end_time = datetime.combine(forecast_date, datetime.strptime('15:30', '%H:%M').time())
        df_forecast = generate_signals(start_time, end_time)
        st.success("✅ Forecast generated")
        st.dataframe(df_forecast)
        csv = df_forecast.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, file_name=f"forecast_{forecast_date}.csv")

elif mode == "Backtest with CSV":
    uploaded_file = st.file_uploader("Upload 1-minute Nifty CSV (with 'Datetime' and 'Close' columns)")
    if uploaded_file:
        df_price = pd.read_csv(uploaded_file)
        df_price['Datetime'] = pd.to_datetime(df_price['Datetime'])
        df_price['Time'] = df_price['Datetime'].dt.strftime('%H:%M')
        start_time = df_price['Datetime'].iloc[0]
        end_time = df_price['Datetime'].iloc[-1]
        df_forecast = generate_signals(start_time, end_time)
        df_merged = pd.merge(df_price, df_forecast, on='Time', how='left')
        df_signals = df_merged[df_merged['Signal'].notnull()]
        st.success("✅ Signals generated and merged with price")
        st.dataframe(df_signals[['Datetime', 'Close', 'Signal']])

        fig, ax = plt.subplots(figsize=(15, 6))
        ax.plot(df_merged['Datetime'], df_merged['Close'], label='NIFTY Price', color='black')
        for _, row in df_signals.iterrows():
            color = {'BUY': 'green', 'SELL': 'red', 'REVERSAL': 'orange'}[row['Signal']]
            marker = {'BUY': '^', 'SELL': 'v', 'REVERSAL': 'x'}[row['Signal']]
            ax.scatter(row['Datetime'], row['Close'], color=color, marker=marker, s=100, label=row['Signal'])
        ax.set_title("NIFTY 1-min Chart with Gann + Astro Signals")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.grid(True)
        st.pyplot(fig)

        csv = df_signals.to_csv(index=False).encode()
        st.download_button("📥 Download Signals CSV", csv, file_name="backtest_signals.csv")
