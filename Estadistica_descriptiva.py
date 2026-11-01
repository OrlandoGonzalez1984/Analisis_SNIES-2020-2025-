
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import textwrap

@st.cache_data
def preparar_estadisticas():

    base = pd.read_csv("Matriz_SNIES_2020_2025.csv",encoding="utf-8-sig")
    base.columns = base.columns.str.strip()

    # Establecer los oncen datos históricos sin incluir el periodo 2025-2
    periodos = [f"{ano}-{semestre}"
        for ano in range(2020, 2026)
        for semestre in [1, 2]
        if not (ano == 2025 and semestre == 2)]

    base[periodos] = base[periodos].apply(pd.to_numeric,errors="coerce")
    datos = base[periodos]

    # =========================================================
    # Base de descriptivos para los datos de la serie de tiempo
    # =========================================================

    #Contar la cantidad de observaciones
    base["N"] = datos.count(axis=1)

    #Obtneción de la media y mediana de los datos (por registro)
    base["Media"] = datos.mean(axis=1)
    base["Mediana"] = datos.median(axis=1)

    #Obtención del valor mínimo y máximo de los datos (por registro)
    base["Minimo"] = datos.min(axis=1)
    base["Maximo"] = datos.max(axis=1)

    #Obtención del rango, varianza y desviación (dispersión de datos)
    base["Rango"] = base["Maximo"] - base["Minimo"]
    base["Varianza"] = datos.var(axis=1, ddof=1)
    base["Desviacion"] = datos.std(axis=1, ddof=1)

    #Calculo del coeficiente de variación
    base["CV (%)"] = np.where(base["Media"] != 0, base["Desviacion"] / base["Media"] * 100, np.nan)

    #Obtención de los cuartiles y rangos intercuartílicos
    base["Q1"] = datos.quantile(0.25, axis=1)
    base["Q3"] = datos.quantile(0.75, axis=1)
    base["RIC"] = base["Q3"] - base["Q1"]

    return base

#El objeto base guardar la información que se ha generado en la función preparar estadísticas
base = preparar_estadisticas()

#1.Visualización del título y descripción general de la información presentada
#---------------------------------------------------------------------------------------------------------------------------
st.title("Estadística Descriptiva de Matrícula")

st.markdown("""Análisis cuantitativo de estudiantes matriculados en programas académicos de ingeniería de las instituciones
de educación superior.

**Periodo de análisis: 2020-1 a 2025-1.**

Los indicadores se calculan utilizando las once observaciones semestrales de cada registro académico.""")
#---------------------------------------------------------------------------------------------------------------------------

#Filtrado para la visualización de información
col1, col2 = st.columns(2)

with col1:

    departamento = st.selectbox("Seleccione el departamento:",
        sorted(
            base["DEPARTAMENTO DE OFERTA DEL PROGRAMA"].dropna().unique())
    )

# Filtrar universidades del departamento seleccionado
df_departamento = base[base["DEPARTAMENTO DE OFERTA DEL PROGRAMA"] == departamento]

with col2:

    universidad = st.selectbox("Seleccione la universidad:",
        sorted(df_departamento["INSTITUCION DE EDUCACION SUPERIOR (IES)"].dropna().unique())
    )

# Filtrar registros de la universidad
datos_filtrados = df_departamento[
    df_departamento["INSTITUCION DE EDUCACION SUPERIOR (IES)"] == universidad].copy()

#Proceso para generar la presentación de datos descriptivos por universidad
st.divider()

st.subheader("Resumen estadístico institucional")

# Obtención de la cantidad de registros
total_registros = len(datos_filtrados)

# Matrícula media semestral de la universidad
matricula_media = datos_filtrados["Media"].sum()

# Coeficiente de variación promedio de los registros
cv_promedio = datos_filtrados["CV (%)"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Registros académicos",total_registros)

with col2:
    st.metric("Matrícula media semestral",f"{matricula_media:,.1f}")

with col3:
    st.metric("CV promedio de registros",f"{cv_promedio:.2f}%")


# -----------------------------------------------------------
# Presentación Tabla resumen
# -----------------------------------------------------------

st.divider()

st.subheader("Indicadores descriptivos por programa académico")

columnas = [
    "CODIGO SNIES DEL PROGRAMA",
    "PROGRAMA ACADEMICO",
    "N",
    "Media",
    "Mediana",
    "Minimo",
    "Maximo",
    "Rango",
    "Varianza",
    "Desviacion",
    "CV (%)",
    "Q1",
    "Q3",
    "RIC"]

tabla = datos_filtrados[columnas].copy()

tabla.rename(
    columns={
        "CODIGO SNIES DEL PROGRAMA": "Código SNIES",
        "PROGRAMA ACADEMICO": "Programa académico",
        "Minimo": "Mínimo",
        "Maximo": "Máximo",
        "Desviacion": "Desviación estándar"
    }, inplace=True)

st.dataframe(tabla.round(2),use_container_width=True,hide_index=True)

st.caption(
    "Indicadores calculados sobre las observaciones "
    "semestrales de 2020-1 a 2025-1. ")


