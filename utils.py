import pandas as pd
import streamlit as st


# Purpose is to filter out data using a single function so it's easier to integrate
# in streamlit 

def filter_df(df, selected_years, selected_months, selected_addresses):
    filtered_df = df.copy()  # Make a copy of the original DataFrame
    if "Select All" not in selected_years:
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
    if "Select All" not in selected_months:
        filtered_df = filtered_df[filtered_df['month'].isin(selected_months)]
    if "Select All" not in selected_addresses:
        filtered_df = filtered_df[filtered_df['Full_Address'].isin(selected_addresses)]
    return filtered_df



def generate_popup_html(grouped_df):
    html = grouped_df.to_html(classes="table table-striped table-hover table-condensed table-responsive", index=False)
    return html

address_color_map = {
    'Ambato, Tungurahua': '#1e81b0',
    'Babahoyo, Los Rios': '#e5d1d1',
    'Cayambe, Pichincha': '#eeeee4',
    'Cuenca, Azuay': '#eab676',
    'Daule, Guayas': '#e28743',
    'El Carmen, Manabi': '#76b5c5',
    'Esmeraldas, Esmeraldas': '#873e23',
    'Guaranda, Bolivar': '#063970',
    'Guayaquil, Guayas': '#982828',
    'Ibarra, Imbabura': '#467c48',
    'Latacunga, Cotopaxi': '#a0d0bf',
    'Libertad, Guayas': '#a5fb62',
    'Loja, Loja': '#91ffe1',
    'Machala, El Oro': '#82b1bd',
    'Manta, Manabi': '#ffcf72',
    'Playas, Guayas': '#006f62',
    'Puyo, Pastaza': '#93cbcb',
    'Quevedo, Los Rios': '#4b0956',
    'Quito, Pichincha': '#fffb00',
    'Riobamba, Chimborazo': '#ff91e6',
    'Salinas, Santa Elena': '#91afff',
    'Santo Domingo, Santo Domingo de los Tsachilas': '#b400bc'
}

def get_color(addr):
    x= address_color_map.get(addr)
    return x