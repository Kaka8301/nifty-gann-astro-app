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
import pandas as pd
import swisseph as swe
import streamlit as st
from datetime import datetime
import pytz

st.set_page_config(page_title="Nifty Gann Astro Forecast", layout="centered")

def get_planet_positions(dt):
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)
    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    positions = {}
    for i, name in zip(range(7), planets):
        pos, _ = swe.calc_ut(jd, i)
        positions[name] = round(pos[0], 2)  # Only longitude
    return positions

# UI: Upload file
st.title("🌟 Nifty Gann + Astrology Forecast System")
st.subheader("Upload 1-min CSV file & get planetary signals")
uploaded_file = st.file_uploader("Upload 1-min Nifty data (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Try to parse datetime
    datetime_col = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
    if datetime_col:
        df['datetime'] = pd.to_datetime(df[datetime_col[0]])
        df = df.sort_values(by='datetime')
        df['planet_positions'] = df['datetime'].apply(get_planet_positions)

        # Extract positions into separate columns
        for planet in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
            df[planet] = df['planet_positions'].apply(lambda x: x[planet])

        df.drop(columns=['planet_positions'], inplace=True)

        st.success("✅ Planetary positions calculated.")
        st.dataframe(df[['datetime', 'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']].head())

        # Optionally: Download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Astro Data CSV", csv, "astro_signals.csv", "text/csv")

    else:
        st.error("Could not find a valid datetime column.")
