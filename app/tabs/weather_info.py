import streamlit as st
from utils.openweathermap import get_weather_data


def render():
    st.title("Informações Meteorológicas")
    st.write("Aqui ficará o conteúdo da aba 'Informações Meteorológicas'.")
    st.markdown("---")

    city = st.text_input(
        "Digite o nome da cidade para buscar dados meteorológicos:", "Sao Paulo"
    )
    weather = get_weather_data(city)

    st.subheader("Dados Meteorológicos")
    if weather:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperatura (°C)", weather["temperature"])
        with col2:
            st.metric("Umidade (%)", weather["humidity"])
        st.write(f"Descrição: {weather['description'].capitalize()}")
    else:
        st.write(
            "Não foi possível obter os dados meteorológicos. Verifique o nome da cidade."
        )
