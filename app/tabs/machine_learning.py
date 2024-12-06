import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import io


def train_model():

    data_path = "./database/tbl_LEITURA.csv"
    df = pd.read_csv(data_path)

    df["humidity_temperature_ratio"] = df["ltr_UMIDADE"] / (df["ltr_TEMPERATURA"] + 0.1)

    X = df[
        [
            "ltr_UMIDADE",
            "ltr_TEMPERATURA",
            "ltr_PH",
            "ltr_NUTRIENTE_P",
            "ltr_NUTRIENTE_K",
            "humidity_temperature_ratio",
        ]
    ]
    y = df["ltr_STATUS_IRRIGACAO"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred_rf)
    report = classification_report(y_test, y_pred_rf, output_dict=True)
    confusion_matrix_result = confusion_matrix(y_test, y_pred_rf)

    feature_importance = rf_model.feature_importances_

    model_filename = "rf_model.pkl"
    joblib.dump(rf_model, model_filename)

    return (
        accuracy,
        report,
        confusion_matrix_result,
        model_filename,
        X_train,
        X_test,
        y_train,
        y_test,
        feature_importance,
    )


def render():
    st.title("Machine Learning - Treinamento de Modelo")
    st.write("Este modelo utiliza dados de sensores para prever o status de irrigação.")

    with st.expander("Detalhes do Dataset"):
        data_path = "./database/tbl_LEITURA.csv"
        df = pd.read_csv(data_path)

        st.markdown("**Primeiras Linhas do Dataset:**")
        st.dataframe(df.head())

        st.markdown("**Informações do Dataset:**")
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_output = buffer.getvalue()

        st.code(info_output, language="text")

        st.markdown("**Valores Ausentes no Dataset**")
        st.write(df.isnull().sum())

    if st.button("Treinar Modelo"):
        with st.spinner("Treinando o modelo..."):
            (
                accuracy,
                report,
                confusion_matrix_result,
                model_filename,
                X_train,
                X_test,
                y_train,
                y_test,
                feature_importance,
            ) = train_model()
        st.success("Modelo treinado com sucesso!")

        st.subheader("Métricas de Desempenho")
        col1, col2 = st.columns(2)
        col1.metric("Acurácia", f"{accuracy:.2f}")
        col2.metric("Conjunto de Treinamento", f"{X_train.shape[0]} amostras")
        col2.metric("Conjunto de Teste", f"{X_test.shape[0]} amostras")

        st.subheader("Matriz de Confusão (Random Forest)")
        st.write(confusion_matrix_result)

        st.subheader("Relatório de Classificação")
        report_df = pd.DataFrame(report).transpose()
        st.dataframe(report_df.style.format("{:.2f}"))

        st.subheader("Importância das Features")
        feature_importance_df = pd.DataFrame(
            feature_importance, index=X_train.columns, columns=["Importância"]
        )
        st.dataframe(feature_importance_df.style.format("{:.2f}"))

        st.info(f"Modelo treinado e salvo como `{model_filename}`.")

        with open(model_filename, "rb") as file:
            st.download_button(
                label="Baixar Modelo Treinado",
                data=file,
                file_name=model_filename,
                mime="application/octet-stream",
            )
