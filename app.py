import streamlit as st
import pandas as pd
import swisseph as swe
from datetime import datetime, timedelta
import pytz

# Streamlit page config must be first
st.set_page_config(page_title="Nifty Gann Astro Forecast", layout="centered")

st.title("🌟 Nifty Gann + Astrology Forecast System")
st.subheader("Upload 1-min CSV file & get planetary signals")

# ----------- Planet Position Function ------------
def get_planet_positions(dt):
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)
    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    positions = {}
    for i, name in zip(range(7), planets):
        pos, _ = swe.calc_ut(jd, i)
        positions[name] = round(pos[0], 2)
    return positions

# ----------- CSV Upload Section ------------
uploaded_file = st.file_uploader("Upload 1-min Nifty data (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    datetime_col = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
    if datetime_col:
        df['datetime'] = pd.to_datetime(df[datetime_col[0]])
        df = df.sort_values(by='datetime')
        df['planet_positions'] = df['datetime'].apply(get_planet_positions)

        for planet in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
            df[planet] = df['planet_positions'].apply(lambda x: x[planet])
        df.drop(columns=['planet_positions'], inplace=True)

        st.success("✅ Planetary positions calculated.")
        st.dataframe(df[['datetime', 'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']].head())

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Astro Data CSV", csv, "astro_signals.csv", "text/csv")

    else:
        st.error("Could not find a valid datetime column.")


# ----------- FUTURE FORECAST SECTION ------------
st.subheader("🔮 Generate Future Forecast")

future_date = st.date_input("Select forecast date")

if st.button("Generate Forecast"):
    start_time = datetime.combine(future_date, datetime.strptime("09:15", "%H:%M").time())
    times = [start_time + timedelta(minutes=i) for i in range(0, 376)]  # till 15:30

    forecast_df = pd.DataFrame({'datetime': times})
    forecast_df['planet_positions'] = forecast_df['datetime'].apply(get_planet_positions)

    for planet in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
        forecast_df[planet] = forecast_df['planet_positions'].apply(lambda x: x[planet])
    forecast_df.drop(columns=['planet_positions'], inplace=True)

    # Add Gann timing
    gann_times = ['09:15', '09:45', '10:30', '11:45', '13:00', '14:20', '15:10']
    forecast_df['GannTime'] = forecast_df['datetime'].dt.strftime('%H:%M').isin(gann_times)

    # Aspect logic
    def angle_diff(a, b):
        diff = abs(a - b) % 360
        return min(diff, 360 - diff)

    def find_aspect(row, p1='Moon', p2='Saturn'):
        angle = angle_diff(row[p1], row[p2])
        aspects = {
            'Conjunction': 0,
            'Sextile': 60,
            'Square': 90,
            'Trine': 120,
            'Opposition': 180
        }
        for name, deg in aspects.items():
            if abs(angle - deg) <= 3:
                return name
        return None

    forecast_df['Aspect'] = forecast_df.apply(find_aspect, axis=1)

    def generate_signal(row):
        if row['GannTime'] and row['Aspect'] in ['Conjunction', 'Trine']:
            return 'BUY'
        elif row['GannTime'] and row['Aspect'] in ['Square', 'Opposition']:
            return 'SELL'
        elif row['GannTime'] and row['Aspect']:
            return 'REVERSAL'
        else:
            return 'HOLD'

    forecast_df['Signal'] = forecast_df.apply(generate_signal, axis=1)

    st.success("✅ Forecast generated")
    st.dataframe(forecast_df[['datetime', 'Moon', 'Saturn', 'Aspect', 'GannTime', 'Signal']])

    forecast_csv = forecast_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Forecast CSV", forecast_csv, "future_forecast.csv", "text/csv")

