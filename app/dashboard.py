import matplotlib.pyplot
import streamlit
import seaborn
import pandas
from database import fetch_sensor_data
from weather import get_weather_data

streamlit.set_page_config(page_title="Farm Tech Solutions")
streamlit.title("Farm Tech Solutions")
streamlit.write(
    "Visualize os dados dos sensores e o status de irrigação ao longo do tempo, agregados por mês."
)
streamlit.markdown("---")

data = fetch_sensor_data()

# Weather Data
city = streamlit.text_input(
    "Digite o nome da cidade para buscar dados meteorológicos:", "Sao Paulo"
)
weather = get_weather_data(city)

streamlit.subheader("Dados Meteorológicos")
if weather:
    col1, col2 = streamlit.columns(2)
    with col1:
        streamlit.metric("Temperatura (°C)", weather["temperature"])
    with col2:
        streamlit.metric("Umidade (%)", weather["humidity"])
    streamlit.write(f"Descrição: {weather['description'].capitalize()}")
else:
    streamlit.write(
        "Não foi possível obter os dados meteorológicos. Verifique o nome da cidade."
    )
streamlit.markdown("---")

# Raw Sensor Data
streamlit.subheader("Dados Brutos dos Sensores")
streamlit.write(
    "Aqui estão todos os dados coletados pelos sensores, mostrando valores de umidade, pH, temperatura e status da irrigação."
)
streamlit.dataframe(data)
monthly_data = data.groupby("month").mean().reset_index()
streamlit.markdown("---")

# Average Monthly Humidity
streamlit.subheader("Média Mensal de Umidade")
streamlit.write(
    "Visualize a média mensal dos níveis de umidade coletados ao longo do tempo."
)
matplotlib.pyplot.figure(figsize=(10, 4))
matplotlib.pyplot.plot(
    monthly_data["month"].astype(str), monthly_data["humidity"], marker="o"
)
matplotlib.pyplot.xlabel("Mês")
matplotlib.pyplot.ylabel("Média de Umidade (%)")
matplotlib.pyplot.xticks(rotation=45)
streamlit.pyplot(matplotlib.pyplot)
streamlit.markdown("---")

# pH Chart by Month
streamlit.subheader("Média Mensal de pH")
streamlit.write("Visualize a média mensal dos níveis de pH coletados.")
matplotlib.pyplot.figure(figsize=(10, 4))
matplotlib.pyplot.plot(
    monthly_data["month"].astype(str), monthly_data["ph"], marker="o", color="orange"
)
matplotlib.pyplot.xlabel("Mês")
matplotlib.pyplot.ylabel("Média de pH")
matplotlib.pyplot.xticks(rotation=45)
streamlit.pyplot(matplotlib.pyplot)
streamlit.markdown("---")

# Irrigation Status by Month
streamlit.subheader("Status Médio de Irrigação por Mês")
streamlit.write("Mostra a média mensal de quando a irrigação foi ativada.")
matplotlib.pyplot.figure(figsize=(10, 4))
matplotlib.pyplot.plot(
    monthly_data["month"].astype(str),
    monthly_data["irrigation_status"],
    marker="o",
    color="green",
)
matplotlib.pyplot.xlabel("Mês")
matplotlib.pyplot.ylabel("Status de Irrigação (1=Ligado, 0=Desligado)")
matplotlib.pyplot.xticks(rotation=45)
streamlit.pyplot(matplotlib.pyplot)
streamlit.markdown("---")

# Distribution of Moisture, pH and Temperature
streamlit.subheader("Distribuição dos Níveis de Umidade, pH e Temperatura")
streamlit.write(
    "Distribuição das medições de umidade, pH e temperatura ao longo do tempo."
)
fig, ax = matplotlib.pyplot.subplots(1, 3, figsize=(15, 4))
seaborn.histplot(data["humidity"], ax=ax[0], kde=True, color="skyblue").set(
    title="Umidade"
)
seaborn.histplot(data["ph"], ax=ax[1], kde=True, color="orange").set(title="pH")
seaborn.histplot(data["temperature"], ax=ax[2], kde=True, color="red").set(
    title="Temperatura"
)
streamlit.pyplot(fig)
streamlit.markdown("---")

# Correlation Matrix
streamlit.subheader("Matriz de Correlação entre Variáveis")
streamlit.write(
    "Veja a relação entre diferentes variáveis. Correlações positivas ou negativas podem indicar dependências."
)
fig, ax = matplotlib.pyplot.subplots(figsize=(8, 6))
seaborn.heatmap(
    data[["humidity", "temperature", "ph", "sensor_p", "sensor_k"]].corr(),
    annot=True,
    cmap="coolwarm",
    center=0,
)
streamlit.pyplot(fig)
streamlit.markdown("---")

# Monthly Irrigation Activation Count
streamlit.subheader("Contagem Mensal de Ativação da Irrigação")
streamlit.write(
    "Quantas vezes por mês a irrigação foi ativada. Isso ajuda a entender o consumo de água ao longo do tempo."
)
monthly_activation_count = data[data["irrigation_status"] == 1].groupby("month").size()
matplotlib.pyplot.figure(figsize=(10, 4))
monthly_activation_count.plot(kind="bar", color="green")
matplotlib.pyplot.xlabel("Mês")
matplotlib.pyplot.ylabel("Número de Ativações")
streamlit.pyplot(matplotlib.pyplot)
streamlit.markdown("---")

# Time Trend Analysis
streamlit.subheader("Tendência de Mudança de Umidade e Temperatura ao Longo do Ano")
streamlit.write(
    "Linhas de tendência para observar como os níveis de umidade e temperatura mudam ao longo do ano."
)
fig, ax = matplotlib.pyplot.subplots(figsize=(10, 5))
seaborn.lineplot(data=data, x="created_at", y="humidity", label="Umidade", color="blue")
seaborn.lineplot(
    data=data, x="created_at", y="temperature", label="Temperatura", color="red"
)
matplotlib.pyplot.xlabel("Data")
matplotlib.pyplot.ylabel("Valores")
matplotlib.pyplot.xticks(rotation=45)
streamlit.pyplot(fig)
streamlit.markdown("---")

# Irrigation Efficiency Analysis
streamlit.subheader("Eficiência do Uso da Água")
streamlit.write(
    "Comparação dos dias com e sem irrigação ativada ao longo do tempo para avaliar a eficiência no uso da água."
)
days_with_irrigation = (
    data[data["irrigation_status"] == 1].groupby(data["created_at"].dt.date).size()
)
days_without_irrigation = (
    data[data["irrigation_status"] == 0].groupby(data["created_at"].dt.date).size()
)
efficiency_df = pandas.DataFrame(
    {
        "Dias com Irrigação": days_with_irrigation,
        "Dias sem Irrigação": days_without_irrigation,
    }
).fillna(0)
streamlit.bar_chart(efficiency_df)
streamlit.markdown("---")

# Analysis of Ideal Conditions for Humidity and pH
streamlit.subheader("Análise de Condições Ideais de Umidade e pH")
streamlit.write(
    "Aqui você pode visualizar quantos registros estão dentro das condições ideais para o cultivo, "
    "ajudando a monitorar a saúde das suas plantas."
)

ideal_humidity = data[(data["humidity"] >= 40) & (data["humidity"] <= 60)]
ideal_ph = data[(data["ph"] >= 6.0) & (data["ph"] <= 7.5)]

streamlit.markdown("### Condições Ideais")
col1, col2 = streamlit.columns(2)

with col1:
    streamlit.metric(
        label="Registros com Umidade Ideal (40%-60%)", value=len(ideal_humidity)
    )

with col2:
    streamlit.metric(label="Registros com pH Ideal (6.0-7.5)", value=len(ideal_ph))

streamlit.write(
    "Essas informações são cruciais para otimizar a irrigação e garantir um ambiente saudável para suas culturas."
)
