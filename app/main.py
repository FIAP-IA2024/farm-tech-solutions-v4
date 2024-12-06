import streamlit as st
from tabs import sensor_data, weather_info, machine_learning

st.set_page_config(page_title="Farm Tech Solutions")

tab1, tab2, tab3 = st.tabs(
    ["Dados dos Sensores", "Informações Meteorológicas", "Machine Learning"]
)

with tab1:
    sensor_data.render()

with tab2:
    weather_info.render()

with tab3:
    machine_learning.render()
