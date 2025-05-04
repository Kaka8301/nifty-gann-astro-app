import streamlit as st
import pandas as pd
import swisseph as swe
from datetime import datetime, timedelta

st.title("📈 Nifty Gann + Astrology Forecast System")
st.subheader("Upload 1-min CSV file & get planetary signals")

# Step 1: Upload file
uploaded_file = st.file_uploader("Upload 1-min Nifty data (CSV)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded!")

    # Assume columns: 'datetime', 'open', 'high', 'low', 'close'
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')
    
    # Step 2: Compute planetary positions
    st.subheader("🪐 Calculating planetary longitudes...")
    planets = ['SUN', 'MOON', 'MERCURY', 'VENUS', 'MARS', 'JUPITER', 'SATURN']
    planet_data = []

    for dt in df['datetime']:
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60)
        row = {'datetime': dt}
        for p in planets:
            lon, _ = swe.calc_ut(jd, getattr(swe, p))[:2]
            row[p] = lon
        planet_data.append(row)

    astro_df = pd.DataFrame(planet_data)
    full_df = pd.merge(df, astro_df, on="datetime")

    st.success("✅ Planetary data added")

    # Step 3: Dummy signal logic (to be replaced with Gann/Astro logic)
    def dummy_signal(row):
        # Example: Buy if Moon > 180 deg
        if row['MOON'] > 180:
            return "BUY"
        elif row['MOON'] < 90:
            return "SELL"
        else:
            return "HOLD"

    full_df['Signal'] = full_df.apply(dummy_signal, axis=1)
    st.subheader("📌 Signals")
    st.dataframe(full_df[['datetime', 'close', 'MOON', 'Signal']])

    # Step 4: Download option
    st.download_button("📥 Download Results", full_df.to_csv(index=False), "nifty_astro_signals.csv", "text/csv")
