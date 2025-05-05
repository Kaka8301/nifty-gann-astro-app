import streamlit as st
import pandas as pd
import swisseph as swe
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Nifty Gann Astro Forecast", layout="wide")

# Define planetary aspects
aspect_angles = {
    'conjunction': 0,
    'opposition': 180,
    'trine': 120,
    'square': 90,
    'sextile': 60
}

def get_planet_positions(dt):
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)
    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    positions = {}
    for i, name in zip(range(7), planets):
        pos, _ = swe.calc_ut(jd, i)
        positions[name] = round(pos[0], 2)
    return positions

def check_aspects(row, orb=1.5):
    moon = row['Moon']
    jupiter = row['Jupiter']
    venus = row['Venus']
    saturn = row['Saturn']
    aspects = []
    for name, angle in aspect_angles.items():
        if abs((moon - jupiter) % 360 - angle) <= orb:
            aspects.append(f"Moon-Jupiter {name}")
        if abs((venus - saturn) % 360 - angle) <= orb:
            aspects.append(f"Venus-Saturn {name}")
    return ", ".join(aspects) if aspects else ""

def generate_signal(row):
    if "Moon-Jupiter trine" in row['Aspects'] or "Venus-Saturn trine" in row['Aspects']:
        return "BUY"
    elif "Moon-Jupiter opposition" in row['Aspects'] or "Venus-Saturn square" in row['Aspects']:
        return "SELL"
    elif row['Aspects']:
        return "REVERSAL"
    else:
        return "HOLD"

# Streamlit UI
st.title("🌟 Nifty Gann + Astrology Forecast System")
st.subheader("Upload 1-min Nifty CSV data & generate signals")

uploaded_file = st.file_uploader("📤 Upload 1-min Nifty data", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    datetime_col = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
    
    if datetime_col:
        df['datetime'] = pd.to_datetime(df[datetime_col[0]])
        df = df.sort_values(by='datetime')
        df['planet_positions'] = df['datetime'].apply(get_planet_positions)

        for planet in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
            df[planet] = df['planet_positions'].apply(lambda x: x[planet])

        df['Aspects'] = df.apply(check_aspects, axis=1)
        df['Signal'] = df.apply(generate_signal, axis=1)
        df.drop(columns=['planet_positions'], inplace=True)

        st.success("✅ Forecast generated.")
        st.dataframe(df[['datetime', 'close', 'Moon', 'Jupiter', 'Venus', 'Saturn', 'Aspects', 'Signal']].head())

        # Plot chart
        fig = px.line(df, x='datetime', y='close', title="Nifty Close Price with Signals")
        for i, row in df.iterrows():
            if row['Signal'] in ["BUY", "SELL", "REVERSAL"]:
                fig.add_vline(x=row['datetime'], line_dash="dot", line_color="red", annotation_text=row['Signal'])
        st.plotly_chart(fig, use_container_width=True)

        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Forecast CSV", csv, "nifty_forecast.csv", "text/csv")
    
    else:
        st.error("No datetime column found in CSV.")
from datetime import timedelta

st.subheader("🔮 Forecast Future Signals (Astro Only)")

with st.form("forecast_form"):
    start_date = st.date_input("Start Date")
    start_time = st.time_input("Start Time")
    end_date = st.date_input("End Date")
    end_time = st.time_input("End Time")
    submit = st.form_submit_button("Generate Forecast")

if submit:
    start_dt = datetime.combine(start_date, start_time)
    end_dt = datetime.combine(end_date, end_time)
    
    forecast_data = []
    current = start_dt
    while current <= end_dt:
        positions = get_planet_positions(current)
        moon = positions['Moon']
        jupiter = positions['Jupiter']
        venus = positions['Venus']
        saturn = positions['Saturn']
        aspects = []

        for name, angle in aspect_angles.items():
            if abs((moon - jupiter) % 360 - angle) <= 1.5:
                aspects.append(f"Moon-Jupiter {name}")
            if abs((venus - saturn) % 360 - angle) <= 1.5:
                aspects.append(f"Venus-Saturn {name}")

        aspect_str = ", ".join(aspects)
        if "trine" in aspect_str:
            signal = "BUY"
        elif "opposition" in aspect_str or "square" in aspect_str:
            signal = "SELL"
        elif aspect_str:
            signal = "REVERSAL"
        else:
            signal = "HOLD"

        forecast_data.append({
            "datetime": current,
            "Moon": moon,
            "Jupiter": jupiter,
            "Venus": venus,
            "Saturn": saturn,
            "Aspects": aspect_str,
            "Signal": signal
        })
        current += timedelta(minutes=1)

    forecast_df = pd.DataFrame(forecast_data)
    st.success("✅ Forecast generated.")
    st.dataframe(forecast_df)

    csv = forecast_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Forecast CSV", csv, "future_forecast.csv", "text/csv")
