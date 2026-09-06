# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
import os
from dotenv import load_dotenv

# Import our custom domain architectural layers
from vehicle_db import POPULAR_INDIAN_EVS
from api_client import get_coordinates, get_route_with_elevation, get_weather_data
from physics_engine import simulate_ev_journey

# Load secret API Keys
load_dotenv()
ORS_KEY = os.getenv("ORS_API_KEY")
OWM_KEY = os.getenv("OWM_API_KEY")

# Page Configuration
st.set_page_config(
    page_title="Smart EV Route Planner & Cost Optimizer",
    page_icon="⚡",
    layout="wide"
)

dropdown_options = list(POPULAR_INDIAN_EVS.keys()) + ["Custom EV (Manual Override)"]

# ─── SESSION STATE STORAGE MEMORY ──────────────────────────────────
if "route_coords" not in st.session_state:
    st.session_state.route_coords = None
if "distance" not in st.session_state:
    st.session_state.distance = 0
if "duration" not in st.session_state:
    st.session_state.duration = 0
if "wind" not in st.session_state:
    st.session_state.wind = 0
if "temperature" not in st.session_state:
    st.session_state.temperature = 25
if "raining_status" not in st.session_state:
    st.session_state.raining_status = "Clear"
if "soc_profile" not in st.session_state:
    st.session_state.soc_profile = None
if "total_kwh_used" not in st.session_state:
    st.session_state.total_kwh_used = 0
if "charging_stops" not in st.session_state:
    st.session_state.charging_stops = []

# ─── WEB APP USER INTERFACE ────────────────────────────────────────
st.title("⚡ Smart EV Route Planner & Cost Optimizer")
st.caption("Optimize your route using real-time physics, elevation, and weather data.")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("📍 Journey Configuration")
source = st.sidebar.text_input("Starting Point", value="Palakkad")
destination = st.sidebar.text_input("Destination", value="Kodaikanal")

st.sidebar.markdown("---")
st.sidebar.header("🚗 EV Specifications")
ev_model = st.sidebar.selectbox("Select EV Model", dropdown_options)

if ev_model == "Custom EV (Manual Override)":
    st.sidebar.caption("⚙️ Manual Vehicle Design Input")
    batt_cap = st.sidebar.number_input("Battery Capacity (kWh)", value=45.0, step=1.0)
    weight = st.sidebar.number_input("Total Weight (kg)", value=1450, step=10)
    drag_c = st.sidebar.number_input("Drag Coefficient (Cd)", value=0.30, step=0.01)
    area = st.sidebar.number_input("Frontal Area (m²)", value=2.3, step=0.1)
else:
    specs = POPULAR_INDIAN_EVS[ev_model]
    batt_cap = specs["battery_capacity"]
    weight = specs["weight"]
    drag_c = specs["drag_coeff"]
    area = specs["frontal_area"]
    
    st.sidebar.text(f"🔋 Battery Size: {batt_cap} kWh")
    st.sidebar.text(f"⚖️ Curb Weight: {weight} kg")
    st.sidebar.text(f"💨 Aero Drag: {drag_c} Cd")

initial_soc = st.sidebar.slider("Current Battery Charge (%)", 10, 100, 80)
target_soc = st.sidebar.slider("Desired Destination Battery Charge (%)", 10, 50, 20)

plan_route = st.sidebar.button("Calculate Optimal Route 🚀", width="stretch")

if plan_route:
    with st.spinner("Analyzing environment layers & running propulsion math models..."):
        start_pt = get_coordinates(source, ORS_KEY)
        end_pt = get_coordinates(destination, ORS_KEY)
        
        if start_pt and end_pt:
            coords, dist, dur = get_route_with_elevation(start_pt, end_pt, ORS_KEY)
            
            if coords:
                st.session_state.route_coords = coords
                st.session_state.distance = dist
                st.session_state.duration = dur
                
                mid_point = coords[len(coords) // 2]
                wind, temp, is_raining = get_weather_data(lat=mid_point[1], lon=mid_point[0], api_key=OWM_KEY)
                st.session_state.wind = wind
                st.session_state.temperature = temp
                st.session_state.raining_status = "🌧️ Raining" if is_raining else "☀️ No Rain"
                
                # We execute the clean simulation layer module
                df_profile, kwh_used, stops = simulate_ev_journey(
                    coords, weight, drag_c, area, batt_cap, initial_soc, wind, is_raining, target_soc
                )
                st.session_state.soc_profile = df_profile
                st.session_state.total_kwh_used = kwh_used
                st.session_state.charging_stops = stops
        else:
            st.error("Could not locate the cities entered. Please check the spelling.")

# Layout Columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Optimal Eco-Route Map")
    map_center = [10.5, 76.5]
    
    if st.session_state.route_coords:
        folium_coords = [[coord[1], coord[0]] for coord in st.session_state.route_coords]
        map_center = folium_coords[0]
        
        my_map = folium.Map(location=map_center, zoom_start=9)
        folium.PolyLine(folium_coords, color="blue", weight=5).add_to(my_map)
        
        folium.Marker(folium_coords[0], popup="Start", icon=folium.Icon(color='green', icon='play')).add_to(my_map)
        folium.Marker(folium_coords[-1], popup="Destination", icon=folium.Icon(color='red', icon='flag')).add_to(my_map)
        
        for idx, stop in enumerate(st.session_state.charging_stops):
            stop_info = f"Smart Charging Stop #{idx+1}<br>At: {stop['at_km']:.1f} km<br>Arrival Charge: {stop['arrival_soc']:.1f}%"
            folium.Marker(
                location=stop['coord'],
                popup=stop_info,
                tooltip="⚡ Recommended Charging Station",
                icon=folium.Icon(color='orange', icon='flash')
            ).add_to(my_map)
    else:
        my_map = folium.Map(location=map_center, zoom_start=8)
        
    st_folium(my_map, width=700, height=450, key="ev_map")

with col2:
    st.subheader("📊 Environment & Route Insights")
    if st.session_state.route_coords:
        st.metric(label="Total Distance", value=f"{st.session_state.distance:.2f} km")
        st.metric(label="Estimated Travel Time", value=f"{st.session_state.duration:.2f} hours")
        st.metric(label="Midpoint Ambient Temp", value=f"{st.session_state.temperature:.1f} °C")
        st.metric(label="Wind Speed & Precipitation", value=f"{st.session_state.wind} m/s | {st.session_state.raining_status}")
        st.metric(label="Predicted Energy Consumed", value=f"{st.session_state.total_kwh_used:.2f} kWh")
        
        num_stops = len(st.session_state.charging_stops)
        st.info(f"💡 Recommended Charging Stops Required: **{num_stops}**")
    else:
        st.metric(label="Total Distance", value="-- km")
        st.metric(label="Estimated Travel Time", value="-- hours")
        st.metric(label="Midpoint Ambient Temp", value="-- °C")
        st.metric(label="Wind Speed & Precipitation", value="--")
        st.metric(label="Predicted Energy Consumed", value="-- kWh")

st.markdown("---")
col_chart, col_matrix = st.columns([3, 2])

with col_chart:
    st.subheader("📈 Battery State of Charge (%) Profile")
    if st.session_state.soc_profile is not None:
        fig = px.line(st.session_state.soc_profile, x='Distance (km)', y='Battery %')
        fig.update_yaxes(range=[0, 105])
    else:
        mock_data = pd.DataFrame({'Distance (km)': [0, 50, 100], 'Battery %': [initial_soc, initial_soc, initial_soc]})
        fig = px.line(mock_data, x='Distance (km)', y='Battery %')
        fig.update_yaxes(range=[0, 105])
    st.plotly_chart(fig,width="stretch")

with col_matrix:
    st.subheader("💰 Time-of-Day (ToD) Cost Optimization")
    if st.session_state.route_coords:
        energy = st.session_state.total_kwh_used
        
        cost_off_peak = energy * 8.0   
        cost_standard = energy * 15.0  
        cost_peak = energy * 22.0      
        
        cost_data = {
            "Charging Window": ["Off-Peak (11 PM - 5 AM)", "Standard (5 AM - 6 PM)", "Peak Hour (6 PM - 11 PM)"],
            "Tariff Rate": ["₹ 8.00 / kWh", "₹ 15.00 / kWh", "₹ 22.00 / kWh"],
            "Total Trip Expense": [f"₹ {cost_off_peak:.2f}", f"₹ {cost_standard:.2f}", f"₹ {cost_peak:.2f}"]
        }
        df_matrix = pd.DataFrame(cost_data)
        st.table(df_matrix)
        
        savings = cost_peak - cost_off_peak
        st.success(f"🌱 Smart Choice: Charging during Off-Peak windows saves **₹ {savings:.2f}** on this single journey!")
    else:
        st.write("Click 'Calculate Optimal Route' to generate economic analysis reports.")