import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.database import fetch_sensor_data


def render():
    st.title("Dados dos Sensores")
    st.write(
        "Visualize os dados dos sensores e o status de irrigação ao longo do tempo, agregados por mês."
    )
    st.markdown("---")

    data = fetch_sensor_data()

    # Raw Sensor Data
    st.subheader("Dados Brutos dos Sensores")
    st.write(
        "Aqui estão todos os dados coletados pelos sensores, mostrando valores de umidade, pH, temperatura e status da irrigação."
    )
    st.dataframe(data)
    monthly_data = data.groupby("month").mean().reset_index()
    st.markdown("---")

    # Average Monthly Humidity
    monthly_humidity_chart = go.Figure()
    monthly_humidity_chart.add_trace(
        go.Scatter(
            x=monthly_data["month"].astype(str),
            y=monthly_data["ltr_UMIDADE"],
            mode="markers+lines",
            marker=dict(symbol="circle", size=8),
        )
    )
    monthly_humidity_chart.update_layout(
        title="Média de Umidade Mensal",
        xaxis_title="Mês",
        yaxis_title="Média de Umidade (%)",
        xaxis_tickangle=45,
    )
    st.plotly_chart(monthly_humidity_chart)
    st.markdown("---")

    # pH Chart by Month
    monthly_ph_chart = go.Figure()
    monthly_ph_chart.add_trace(
        go.Scatter(
            x=monthly_data["month"].astype(str),
            y=monthly_data["ltr_PH"],
            mode="markers+lines",
            marker=dict(symbol="circle", size=8, color="orange"),
        )
    )
    monthly_ph_chart.update_layout(
        title="Média de pH Mensal",
        xaxis_title="Mês",
        yaxis_title="Média de pH",
        xaxis_tickangle=45,
    )
    st.plotly_chart(monthly_ph_chart)
    st.markdown("---")

    # Irrigation Status by Month
    st.subheader("Status Médio de Irrigação por Mês")
    st.write("Mostra a média mensal de quando a irrigação foi ativada.")
    monthly_irrigation_status_chart = go.Figure()
    monthly_irrigation_status_chart.add_trace(
        go.Scatter(
            x=monthly_data["month"].astype(str),
            y=monthly_data["ltr_STATUS_IRRIGACAO"],
            mode="markers+lines",
            marker=dict(symbol="circle", size=8, color="green"),
        )
    )
    monthly_irrigation_status_chart.update_layout(
        title="Status Médio de Irrigação por Mês",
        xaxis_title="Mês",
        yaxis_title="Status de Irrigação (1=Ligado, 0=Desligado)",
        xaxis_tickangle=45,
        yaxis=dict(tickvals=[0, 1], ticktext=["Desligado", "Ligado"]),
    )
    st.plotly_chart(monthly_irrigation_status_chart)
    st.markdown("---")

    # Distribution of Moisture, pH and Temperature
    st.subheader("Distribuição dos Níveis de Umidade, pH e Temperatura")
    st.write(
        "Distribuição das medições de umidade, pH e temperatura ao longo do tempo."
    )
    humidity_distribution_chart = px.histogram(
        data,
        x="ltr_UMIDADE",
        nbins=30,
        title="Distribuição de Umidade",
        labels={"ltr_UMIDADE": "Umidade (%)"},
        marginal="box",
        color_discrete_sequence=["skyblue"],
    )
    humidity_distribution_chart.update_traces(
        marker=dict(line=dict(width=1, color="blue"))
    )
    st.plotly_chart(humidity_distribution_chart)
    ph_distribution_chart = px.histogram(
        data,
        x="ltr_PH",
        nbins=30,
        title="Distribuição de pH",
        labels={"ltr_PH": "pH"},
        marginal="box",
        color_discrete_sequence=["orange"],
    )
    ph_distribution_chart.update_traces(marker=dict(line=dict(width=1, color="orange")))
    st.plotly_chart(ph_distribution_chart)
    temperature_distribution_chart = px.histogram(
        data,
        x="ltr_TEMPERATURA",
        nbins=30,
        title="Distribuição de Temperatura",
        labels={"ltr_TEMPERATURA": "Temperatura (°C)"},
        marginal="box",
        color_discrete_sequence=["red"],
    )
    temperature_distribution_chart.update_traces(
        marker=dict(line=dict(width=1, color="red"))
    )
    st.plotly_chart(temperature_distribution_chart)
    st.markdown("---")

    # Correlation Matrix
    st.subheader("Matriz de Correlação entre Variáveis")
    st.write(
        "Veja a relação entre diferentes variáveis. Correlações positivas ou negativas podem indicar dependências."
    )
    correlation_matrix_chart = go.Figure(
        data=go.Heatmap(
            z=data[
                [
                    "ltr_UMIDADE",
                    "ltr_TEMPERATURA",
                    "ltr_PH",
                    "ltr_NUTRIENTE_P",
                    "ltr_NUTRIENTE_K",
                ]
            ]
            .corr()
            .values,
            x=[
                "ltr_UMIDADE",
                "ltr_TEMPERATURA",
                "ltr_PH",
                "ltr_NUTRIENTE_P",
                "ltr_NUTRIENTE_K",
            ],
            y=[
                "ltr_UMIDADE",
                "ltr_TEMPERATURA",
                "ltr_PH",
                "ltr_NUTRIENTE_P",
                "ltr_NUTRIENTE_K",
            ],
            colorscale="RdBu",  # Tente usar "RdBu" como alternativa, ou qualquer outra escala válida
            colorbar=dict(title="Correlação"),
            zmin=-1,
            zmax=1,
        )
    )
    correlation_matrix_chart.update_layout(
        title="Matriz de Correlação", xaxis_title="Variáveis", yaxis_title="Variáveis"
    )
    st.plotly_chart(correlation_matrix_chart)
    st.markdown("---")

    # Monthly Irrigation Activation Count
    st.subheader("Contagem Mensal de Ativação da Irrigação")
    st.write(
        "Quantas vezes por mês a irrigação foi ativada. Isso ajuda a entender o consumo de água ao longo do tempo."
    )
    monthly_activation_count = (
        data[data["ltr_STATUS_IRRIGACAO"] == 1].groupby("month").size()
    )
    monthly_activation_count.index = monthly_activation_count.index.astype(str)
    monthly_irrigation_activation_chart = go.Figure()
    monthly_irrigation_activation_chart.add_trace(
        go.Bar(
            x=monthly_activation_count.index,
            y=monthly_activation_count.values,
            marker=dict(color="green"),
        )
    )
    monthly_irrigation_activation_chart.update_layout(
        title="Contagem Mensal de Ativação da Irrigação",
        xaxis_title="Mês",
        yaxis_title="Número de Ativações",
    )
    st.plotly_chart(monthly_irrigation_activation_chart)
    st.markdown("---")

    # Time Trend Analysis
    st.subheader("Tendência de Mudança de Umidade e Temperatura ao Longo do Ano")
    st.write(
        "Linhas de tendência para observar como os níveis de umidade e temperatura mudam ao longo do ano."
    )
    data["ltr_DATA"] = pd.to_datetime(data["ltr_DATA"])
    time_trend_chart = go.Figure()
    time_trend_chart.add_trace(
        go.Scatter(
            x=data["ltr_DATA"],
            y=data["ltr_UMIDADE"],
            mode="lines",
            name="Umidade",
            line=dict(color="blue"),
        )
    )
    time_trend_chart.add_trace(
        go.Scatter(
            x=data["ltr_DATA"],
            y=data["ltr_TEMPERATURA"],
            mode="lines",
            name="Temperatura",
            line=dict(color="red"),
        )
    )
    time_trend_chart.update_layout(
        title="Tendência de Mudança de Umidade e Temperatura ao Longo do Ano",
        xaxis_title="Data",
        yaxis_title="Valores",
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=45),
    )
    st.plotly_chart(time_trend_chart)
    st.markdown("---")

    # Irrigation Efficiency Analysis
    st.subheader("Eficiência do Uso da Água")
    st.write(
        "Comparação dos dias com e sem irrigação ativada ao longo do tempo para avaliar a eficiência no uso da água."
    )
    days_with_irrigation = (
        data[data["ltr_STATUS_IRRIGACAO"] == 1].groupby(data["ltr_DATA"].dt.date).size()
    )
    days_without_irrigation = (
        data[data["ltr_STATUS_IRRIGACAO"] == 0].groupby(data["ltr_DATA"].dt.date).size()
    )
    efficiency_df = pd.DataFrame(
        {
            "Dias com Irrigação": days_with_irrigation,
            "Dias sem Irrigação": days_without_irrigation,
        }
    ).fillna(0)
    efficiency_chart = go.Figure()
    efficiency_chart.add_trace(
        go.Bar(
            x=efficiency_df.index,
            y=efficiency_df["Dias com Irrigação"],
            name="Dias com Irrigação",
            marker=dict(color="green"),
        )
    )
    efficiency_chart.add_trace(
        go.Bar(
            x=efficiency_df.index,
            y=efficiency_df["Dias sem Irrigação"],
            name="Dias sem Irrigação",
            marker=dict(color="red"),
        )
    )
    efficiency_chart.update_layout(
        barmode="stack",
        title="Eficiência do Uso da Água",
        xaxis_title="Data",
        yaxis_title="Número de Dias",
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=45),
    )
    st.plotly_chart(efficiency_chart)
    st.markdown("---")

    # Analysis of Ideal Conditions for Humidity and pH
    st.subheader("Análise de Condições Ideais de Umidade e pH")
    st.write(
        "Aqui você pode visualizar quantos registros estão dentro das condições ideais para o cultivo, "
        "ajudando a monitorar a saúde das suas plantas."
    )

    ideal_humidity = data[(data["ltr_UMIDADE"] >= 40) & (data["ltr_UMIDADE"] <= 60)]
    ideal_ph = data[(data["ltr_PH"] >= 6.0) & (data["ltr_PH"] <= 7.5)]

    st.markdown("### Condições Ideais")
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Registros com Umidade Ideal (40%-60%)", value=len(ideal_humidity)
        )

    with col2:
        st.metric(label="Registros com pH Ideal (6.0-7.5)", value=len(ideal_ph))

    st.write(
        "Essas informações são cruciais para otimizar a irrigação e garantir um ambiente saudável para suas culturas."
    )
