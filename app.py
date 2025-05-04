import streamlit as st
import pandas as pd
import swisseph as swe
from datetime import datetime

# ✅ Must be at the very top
st.set_page_config(page_title="Nifty Gann Astro Forecast", layout="centered")

st.title("🌟 Nifty Gann + Astrology Forecast System")
st.subheader("Upload 1-min CSV file & get planetary signals")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload 1-min Nifty data (CSV)", type=["csv"])

# --- Planet calculation function ---
def get_planet_positions(dt):
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)
    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    positions = {}
    for i, name in zip(range(7), planets):
        pos, _ = swe.calc_ut(jd, i)
        positions[name] = round(pos[0], 2)  # Only longitude
    return positions

# --- If file is uploaded ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Detect datetime column
    datetime_col = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
    if datetime_col:
        df['datetime'] = pd.to_datetime(df[datetime_col[0]])
        df = df.sort_values(by='datetime')

        # Calculate planetary positions
        df['planet_positions'] = df['datetime'].apply(get_planet_positions)

        # Unpack into separate columns
        for planet in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
            df[planet] = df['planet_positions'].apply(lambda x: x[planet])

        df.drop(columns=['planet_positions'], inplace=True)

        st.success("✅ Planetary positions calculated.")
        st.dataframe(df[['datetime', 'close', 'Moon', 'Jupiter', 'Saturn']].head())

        # Add dummy signal logic (can be replaced later)
        def dummy_signal(row):
            if row['Moon'] > 180:
                return "BUY"
            elif row['Moon'] < 90:
                return "SELL"
            else:
                return "HOLD"

        df['Signal'] = df.apply(dummy_signal, axis=1)

        st.subheader("📌 Sample Signals")
        st.dataframe(df[['datetime', 'close', 'Moon', 'Signal']].head())

        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Astro Signals CSV", csv, "nifty_astro_signals.csv", "text/csv")

    else:
        st.error("Could not find a valid datetime column in uploaded CSV.")
