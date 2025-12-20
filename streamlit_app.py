import streamlit as st 
import requests
import json
from datetime import datetime, timedelta
import pandas as pd 
import plotly.express as px

with open('secrets.json') as f:
    secrets = json.load(f)

api_key = secrets['openaq-api-key']

def get_parameters(api_key):
    url = "https://api.openaq.org/v3/parameters"
    headers = { "X-API-Key": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        return None
df_parameters = pd.DataFrame(get_parameters(api_key))
print("Parameter Definitions: ")
print(df_parameters)

from geopy.geocoders import Nominatim
import requests


def get_coordinates(address): # 1 request per sec is accepted
    geolocator = Nominatim(user_agent="air_quality_tracker")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        print("Address not found.")
        return None, None

def get_nearby_locations(lat,lon,api_key,radius,limit):    
    url = "https://api.openaq.org/v3/locations"
    headers = { "X-API-Key": api_key}
    params = {
        "coordinates": f"{lat},{lon}", 
        "radius": radius,                  
        "limit": limit
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        return None
    
def get_sensor_metadata(sensor_id, api_key):
    url = f"https://api.openaq.org/v3/sensors/{sensor_id}"
    headers = { "X-API-Key": api_key }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        return {}

def get_sensors(location_id,api_key):
    url = f"https://api.openaq.org/v3/locations/{location_id}/sensors"
    headers = { "X-API-Key": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        return None


def get_daily_measurements(sensor_id,api_key,date_from,date_to):
    url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements/daily"
    headers = {"X-API-Key": api_key}
    params = {
        "datetime_from": date_from , #format = YYYY-MM-DDTHH:MM:SSZ
        "datetime_to": date_to, #format = YYYY-MM-DDTHH:MM:SSZ
        "limit": 100,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        print(f"Request failed with status code {response.status_code}")

def get_latest_by_locationid(location_id, api_key):
    url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
    headers = {"X-API-Key": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print('failed')
        return None

st.title("Air Quality Dashboard")

address = st.text_input("Enter Address:")
radius = 5000 
st.title("Select Date Range")

date_range = st.date_input("Select Date Range", [])
if isinstance(date_range, tuple) and len(date_range) == 2:
    date_from, date_to = date_range
    st.success(f"Selected range: {date_from} to {date_to}")
else:
    st.warning("Please select a valid start and end date.")

if st.button("Search"):
    with st.spinner("Fetching coordinates..."):
        lat, lon = get_coordinates(address)
    
    if lat is None:
        st.error("Location not found.")
    else:
        with st.spinner("Finding nearest location..."):
            locations = get_nearby_locations(lat, lon, api_key, radius=radius, limit=1)

        if not locations:
            st.warning("No nearby sensor locations found.")
        else:
            location_id = locations[0]['id']
            st.success(f"Using location ID: {location_id}")

            parameters = get_parameters(api_key)
            df_parameters = pd.DataFrame(parameters)
            st.dataframe(df_parameters)

            sensors = get_sensors(location_id, api_key)
            sensor_id_to_param = {s['id']: s['parameter'] for s in sensors}

            latest = get_latest_by_locationid(location_id, api_key)
            df_latest = pd.json_normalize(latest['results'])

            df_latest['utc'] = df_latest['datetime.utc']
            df_latest['local'] = df_latest['datetime.local']
            df_latest['parameter_obj'] = df_latest['sensorsId'].map(sensor_id_to_param)

            df_latest['parameter'] = df_latest['parameter_obj'].apply(
                lambda x: x['name'] if isinstance(x, dict) and 'name' in x else None
            )
            df_latest = df_latest[['parameter', 'value', 'utc', 'local', 'sensorsId']]
            df_latest.dropna(subset=['parameter','value'], inplace=True)

            st.subheader("Latest Air Quality Data")
            if not df_latest.empty:
                fig = px.bar(df_latest, x='parameter', y='value', title='Latest Air Quality by Parameter')
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_latest)
            else:
                st.warning("No valid latest data available.")

            st.subheader("📈 Daily Trends")
            for sensor in sensors:
                sensor_id = sensor['id']
                param_info = sensor['parameter']
                display_name = param_info['displayName'] if isinstance(param_info, dict) else param_info

                st.markdown(f"**Sensor ID: {sensor_id}, Parameter: {display_name}**")
                results = get_daily_measurements(sensor_id, api_key, date_from.isoformat(), date_to.isoformat())
                
                if results:
                    df_daily = pd.json_normalize(results)
                    df_daily['utc'] = pd.to_datetime(df_daily['period.datetimeFrom.utc'])
                    df_daily['value'] = pd.to_numeric(df_daily['value'], errors='coerce')
                    df_daily.dropna(subset=['utc', 'value'], inplace=True)

                    if not df_daily.empty:
                        fig = px.line(df_daily, x='utc', y='value', title=f"{display_name} Daily Trend", markers=True)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No valid trend data.")
                else:
                    st.info("No daily data found.")