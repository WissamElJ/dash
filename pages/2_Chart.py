import streamlit as st
import altair as alt
import plotly.express as px
import numpy as np
import pandas as pd
import folium
from utils import *
import random
alt.themes.enable("dark")
column_names = [
    'id', 'date', 'store_nbr', 'family', 'sales', 'onpromotion', 'year', 'month', 'day', 'city', 'state', 'type', 
    'cluster', 'Full_Address', 'Latitude', 'Longitude'
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
st.write('ℹ️ The dataset size is reduced to reduce webpage lag')
st.write('💡 Hold and drag the mouse button on the top panel to filter out the date. You can also click on the bars in the bar chart to preview unique addresses.')
######## Load data ###########
df = load_data('train_final.csv')
df.columns = column_names
#df = df3[-200000:]
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

new_df = filtered_df.groupby(['date', 'Full_Address','family'])['sales'].sum().reset_index()
new_df.rename(columns={'Full_Address': 'Address'}, inplace=True)

color = alt.Color('Address:N', scale=alt.Scale(scheme='category20b'))

brush = alt.selection_interval(encodings=['x'])
click = alt.selection_multi(encodings=['color'])

# Top panel is line plot of sum of sales vs date
line = alt.Chart(new_df).mark_line().encode(
    alt.X('date:T', title='Date'),
    alt.Y('sum(sales):Q', title='Total Sales'),
    color=alt.condition(click, color, alt.value('lightgray')),
).properties(
    width=550,
    height=300
).add_selection(
    brush
)

# Bottom panel is a bar chart of sales by Full_Address
bars = alt.Chart(new_df).mark_bar().encode(
    x='sum(sales):Q',
    y=alt.Y('Address:N', title='Address', sort='-x'),
    color=alt.condition(click, color, alt.value('lightgray')),
).transform_filter(
    brush
).properties(
    width=550,
).add_selection(
    click
)

alt_chart = alt.vconcat(line, bars, title="Ecuador store sales")
alt_chart

