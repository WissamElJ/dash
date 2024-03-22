import streamlit as st
import altair as alt
import plotly.express as px
import numpy as np
import pandas as pd
from streamlit_folium import st_folium
import folium
from utils import *
import random
alt.themes.enable("dark")
column_names = [
    'id', 'date', 'store_nbr', 'family', 'sales', 'onpromotion', 'year', 'month', 'day', 'city', 'state', 'type', 
    'cluster', 'Full_Address', 'latitude', 'longitude'
]
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, header=None)
    return df

    # Page config
st.set_page_config(
    page_title="Interactive Map 🗺️ ",

    layout="wide",
    initial_sidebar_state="expanded")

######## Load data ###########
df = load_data('train_final.csv')
df.columns = column_names
#df.drop('id',axis=1,inplace=True)

######## Filter Dataframe ###########
year_options = ["Select All"] + sorted(df['year'].unique().tolist())
month_options = ["Select All"] + sorted(df['month'].unique().tolist())
address_options = ["Select All"] + sorted(df['Full_Address'].unique().tolist())

if "selected_years" not in st.session_state:
    st.session_state["selected_years"] = year_options[1:]
if "selected_months" not in st.session_state:
    st.session_state["selected_months"] = month_options[1:]
if "selected_addresses" not in st.session_state:
    st.session_state["selected_addresses"] = address_options[1:]

def filter_select():
    if "selected_years" in st.session_state:
        if "Select All" in st.session_state["selected_years"]:
            st.session_state["selected_years"] = year_options[1:]
        if "Select All" in st.session_state["selected_months"]:
            st.session_state["selected_months"] = month_options[1:]
        if "Select All" in st.session_state["selected_addresses"]:
            st.session_state["selected_addresses"] = address_options[1:]

with st.sidebar:
    
    selected_years = st.multiselect(
        label="Select year",
        options=year_options,
        key="selected_years",
        on_change=filter_select,
        format_func=lambda x: "All" if x == "Select All" else f"{x}",
    )
    
    selected_months = st.multiselect(
        label="Select month",
        options=month_options,
        key="selected_months",
        on_change=filter_select,
        format_func=lambda x: "All" if x == "Select All" else f"{x}",
    )
    
    selected_addresses = st.multiselect(
        label="Select address",
        options=address_options,
        key="selected_addresses",
        on_change=filter_select,
        format_func=lambda x: "All" if x == "Select All" else f"{x}",
    )

# Filter DataFrame based on selected filters
filtered_df = filter_df(df,selected_years, selected_months, selected_addresses)

###### MAP
grouped_df = filtered_df.groupby(['Full_Address','latitude','longitude','family', 'store_nbr','year','month']).agg({
    'sales': ['sum', 'count'],   # Aggregating sales
    'store_nbr': 'nunique'       # Counting unique stores
})
grouped_df = grouped_df.reset_index()
grouped_df.columns = grouped_df.columns.get_level_values(0)
grouped_df.columns = ['Full_Address', 'latitude', 'longitude','family','Store #','year','month', 'sales', 'transactions','selling stores']
grouped_df['sales'] = np.ceil(grouped_df['sales']).astype(int)
grouped_df['Store #']= grouped_df['Store #'].astype(str) + ' ' + grouped_df['Full_Address']
###
st.write('Click on the marker for more info!')
#initiate map
map = folium.Map(location=[-2, -78.5], zoom_start=7, scrollWheelZoom=False, tiles='CartoDB positron')

#get marker coords
latitude_coordinates= grouped_df.latitude.unique()
longitude_coordinates= grouped_df.longitude.unique()

for lat, lon in zip(latitude_coordinates, longitude_coordinates):
    # Add marker to the map for each coordinate pair
    current_data = grouped_df[(grouped_df['latitude'] == lat) & (grouped_df['longitude'] == lon)]
    # Compute summary statistics for the current coordinate
    sum_sales = current_data['sales'].sum()
   
    family_data = current_data[current_data['sales'] > 0]
    unique_product_categories = family_data['family'].nunique()
    location_name = current_data['Full_Address'].iloc[0]

    popup_html = f"""
    <div style="max-width:400px;">
        <h5>{location_name}</h5>
        <p><strong>Total Sales:</strong> ${sum_sales:,.0f} </p>

        <p><strong>Product categories sold:</strong> {unique_product_categories} </p>
    </div>
    """
    
    # Add marker to the map with the generated popup
    #folium.CircleMarker([lat, lon],radius = current_data['sales'].sum() / 10050000,opacity=0.1,fillColor=address_color_map.get(address),interactive=False, color=address_color_map.get(address),popup=popup_html).add_to(map)
    folium.Marker([lat,lon], popup=popup_html).add_to(map)
st_map = st_folium(map, width=900, height=600)

###### Key Metrics
st.subheader('Total Sales Amount')
total_sum=grouped_df['sales'].sum()
st.write(f'<span style="font-size: 36px;">${total_sum:,.2f}</span>', unsafe_allow_html=True)


col1, col2 = st.columns(2)

with col1:
    st.header("Top 10 Best Sellers")
    bar_chart1 = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X("sales:Q", title="Sales"),
        y=alt.Y(
            "family:N",
            sort=alt.EncodingSortField(field="sales", op="sum", order="descending"),
            title="Product Category"
        )
   
    )
    # Display the first bar chart
    st.altair_chart(bar_chart1, use_container_width=True)


with col2:
    st.header("Top 10 Selling Stores")
    bar_chart2 = alt.Chart(grouped_df).mark_bar().encode(
    x=alt.X("sales:Q", title="Sales"),
    y=alt.Y(
        "Store #:N",
        sort=alt.EncodingSortField(field="sales", op="sum", order="descending"),
        title="Address"
    )
    )
    # Display the first bar chart
    st.altair_chart(bar_chart2, use_container_width=True)   



# fig = px.pie(grouped_df[grouped_df['sales']>0], values='sales', names='family', color_discrete_sequence=px.colors.sequential.RdBu)


# st.plotly_chart(fig)

      