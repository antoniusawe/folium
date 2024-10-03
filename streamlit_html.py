#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import folium
from folium.plugins import Draw, LocateControl, Geocoder, MarkerCluster
import pandas as pd
from streamlit_folium import st_folium

# Custom CSS styles for the page
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
    }
    h1 {
        color: #4e73df;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 48px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .menu-label {
        font-weight: bold;
        font-size: 18px;
    }
    .stSidebar {
        background-color: #333;
        color: white;
    }
    .stDataframe {
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# Load the data
url = 'https://raw.githubusercontent.com/antoniusawe/folium/main/request-pak-anto-agt%20to%20sep.csv'
df_absen = pd.read_csv(url)

# Function to create the map with selected Name and Date
def create_map(selected_name='all', selected_august_date='all', selected_september_date='all'):
    my_map = folium.Map(location=[-3.845736431317857, 120.44353552425166], tiles='openstreetmap', zoom_start=5, control_scale=True)
    
    # Create a marker cluster
    marker_cluster = MarkerCluster().add_to(my_map)

    # Filter data based on selected_name and selected_date
    filtered_data = df_absen.copy()
    if selected_name != 'all':
        filtered_data = filtered_data[filtered_data['Name'] == selected_name]
    if selected_august_date != 'all':
        filtered_data = filtered_data[filtered_data['Date'] == selected_august_date]
    if selected_september_date != 'all':
        filtered_data = filtered_data[filtered_data['Date'] == selected_september_date]

    # Group data by Work Location and add unique markers
    for location, group in filtered_data.groupby(['Latitude Work Location', 'Longitude Work Location']):
        latitude, longitude = location
        work_location_name = group['Work Location'].iloc[0]  # Take the first entry for Work Location name
        
        folium.Marker(
            location=[latitude, longitude],
            popup=f"Work Location: {work_location_name}",
            icon=folium.Icon(color='blue', icon='building', prefix='fa')
        ).add_to(marker_cluster)

    # Add CircleMarker for other data points
    for _, row in filtered_data.iterrows():
        # Determine the color based on Status Group
        status_group = row['Status Group']
        if status_group in ['Incomplete', 'Lateness']:
            color = 'red'
        else:
            color = '#32CD32'  # Default to green for Duty On
        
        # Check if 'Duty On Lat' and 'Duty On Long' are valid numbers
        if pd.notnull(row['Duty On Lat']) and row['Duty On Lat'] != 'No Data':
            try:
                lat = float(row['Duty On Lat'])
                long = float(row['Duty On Long'])
                duty_on_popup = f"Nama: {row['Name']}<br>Status: {row['Status Group']}<br>Tanggal: {row['Date']}<br>Jam Masuk: {row['Duty On']}<br>CheckIn di: {row['Duty On Address']}<br>Jarak: {row['Duty On Distance']}<br>Note: {row['Distance On Note']}"
                
                folium.CircleMarker(
                    location=[lat, long],
                    radius=5,
                    color=color,
                    fill=True,
                    fill_opacity=0.7,
                    fill_color=color,
                    popup=folium.Popup(duty_on_popup, max_width=300)
                ).add_to(my_map)
            except ValueError:
                continue  # Skip rows with invalid coordinates
            
        # Determine the color for Duty Off
        color = '#800080' if status_group not in ['Incomplete', 'Lateness'] else 'red'
        
        # Check if 'Duty Off Lat' and 'Duty Off Long' are valid numbers
        if pd.notnull(row['Duty Off Lat']) and row['Duty Off Lat'] != 'No Data':
            try:
                lat = float(row['Duty Off Lat'])
                long = float(row['Duty Off Long'])
                duty_off_popup = f"Nama: {row['Name']}<br>Status: {row['Status Group']}<br>Tanggal: {row['Date']}<br>Jam Keluar: {row['Duty Off']}<br>CheckOut di: {row['Duty Off Address']}<br>Jarak: {row['Duty Off Distance']}<br>Note: {row['Distance Off Note']}"
                
                folium.CircleMarker(
                    location=[lat, long],
                    radius=5,
                    color=color,
                    fill=True,
                    fill_opacity=0.7,
                    fill_color=color,
                    popup=folium.Popup(duty_off_popup, max_width=300)
                ).add_to(my_map)
            except ValueError:
                continue  # Skip rows with invalid coordinates

    # Additional layers and controls
    folium.raster_layers.TileLayer(
        tiles='http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite',
        subdomains=['mt0', 'mt1', 'mt2', 'mt3']
    ).add_to(my_map)

    folium.raster_layers.TileLayer(
        tiles='http://mt1.google.com/vt/lyrs=h,traffic&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Traffic',
        subdomains=['mt0', 'mt1', 'mt2', 'mt3']
    ).add_to(my_map)

    Geocoder().add_to(my_map)  # search bar
    folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", name="Google Maps", attr="Dummy Attribution").add_to(my_map)
    folium.LayerControl().add_to(my_map)
    Draw(export=False).add_to(my_map)
    my_map.add_child(folium.ClickForMarker())
    # LocateControl(auto_start=True).add_to(my_map)

    return my_map

# Load and convert date column
df_absen['Date'] = pd.to_datetime(df_absen['Date'], errors='coerce')

# Create dropdowns for name and dates
name_options = ['all'] + df_absen['Name'].dropna().unique().tolist()
august_date_options = ['all'] + sorted(df_absen[df_absen['Date'].dt.to_period('M') == '2024-08']['Date'].dropna().unique().tolist())
september_date_options = ['all'] + sorted(df_absen[df_absen['Date'].dt.to_period('M') == '2024-09']['Date'].dropna().unique().tolist())

# Add a title for the app
st.title("Absen Record and Location")

# Sidebar with two options: 'Data' and 'Map'
menu = st.sidebar.radio("Menu", ("Tampilkan Data", "Tampilkan Visualisasi Map"), key="menu_key")

if menu == "Tampilkan Data":
    st.subheader("Data Absen")
    st.dataframe(df_absen)    

elif menu == "Tampilkan Visualisasi Map":
    # Streamlit UI components for filtering the map
    selected_name = st.selectbox('Nama:', name_options, key="name_select")
    selected_august_date = st.selectbox('August:', august_date_options, key="august_select")
    selected_september_date = st.selectbox('September:', september_date_options, key="september_select")

    st.subheader("Map Visualisation")
    
    # Create and display map based on selection
    my_map = create_map(selected_name, selected_august_date, selected_september_date)

    # Use st_folium to display the map
    st_folium(my_map, width=600, height=600)


# In[ ]:




