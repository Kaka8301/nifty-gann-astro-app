import streamlit as st
import swisseph as swe
from datetime import datetime

# Set Ephemeris path
swe.set_ephe_path('.')

st.title("Nifty Gann + Astrology Forecast")
st.subheader("Planetary Positions using Swiss Ephemeris")

# Date input from user
selected_date = st.date_input("Select a date for prediction", datetime.today())

# Convert to Julian Day
jd = swe.julday(selected_date.year, selected_date.month, selected_date.day)

# Planets to calculate
planets = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu (Mean)": swe.MEAN_NODE,
    "Ketu (Mean)": swe.TRUE_NODE
}

# Show planetary positions
st.write(f"Julian Day: {jd}")
st.write("### Planetary Longitudes:")

for name, planet in planets.items():
    pos, _ = swe.calc_ut(jd, planet)
    st.write(f"{name}: {pos[0]:.2f}°")

st.info("This is the base setup. Gann and trading signal logic to be added next.")
