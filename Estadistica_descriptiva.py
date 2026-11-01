
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

    return base, periodos

#El objeto base guardar la información que se ha generado en la función preparar estadísticas
base, periodos = preparar_estadisticas()

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

st.dataframe(
    tabla.round(2),
    use_container_width=True,
    hide_index=True,
    height=350,
    column_config={
        "Programa académico": st.column_config.TextColumn(
            "Programa académico",
            width="large"
        ),
        "Código SNIES": st.column_config.NumberColumn(
            "Código SNIES",
            format="%d"
        ),
        "Media": st.column_config.NumberColumn(
            "Media",
            format="%.2f"
        ),
        "CV (%)": st.column_config.NumberColumn(
            "CV (%)",
            format="%.2f %%"
        )
    })

st.caption(
    "Indicadores calculados sobre las observaciones "
    "semestrales de 2020-1 a 2025-1. ")

#Visualización de la gráfica de serie de tiempo para el periodo 2020-I a 2025-I
#-------------------------------------------------------------------------------------------------
st.divider()

st.subheader("Series temporales de matrícula (2020-I a 2025-I)")

# Transformar las 11 columnas en formato reconocible para verse en la gráfica
#----------------------------------------------------------------------------
series_temporales = datos_filtrados.melt(
    id_vars=[
        "CODIGO SNIES DEL PROGRAMA",
        "PROGRAMA ACADEMICO"
    ],
    value_vars=periodos,
    var_name="Periodo",
    value_name="Matriculados")

# Proceso para identificar cada programa académico
series_temporales["Programa"] = (series_temporales["PROGRAMA ACADEMICO"].astype(str)+ " - SNIES "
    + series_temporales["CODIGO SNIES DEL PROGRAMA"].astype(str))

# Orden cronológico de los periodos para visualizar la gráfica

series_temporales["Periodo"] = pd.Categorical(series_temporales["Periodo"],categories=periodos,ordered=True)
series_temporales = series_temporales.sort_values(["Programa", "Periodo"])

# Creación de la gráfica de serie de tiempo
fig_series = px.line(
    series_temporales,
    x="Periodo",
    y="Matriculados",
    color="Programa",
    markers=True,
    title="Evolución semestral de la matrícula",
    labels={
        "Periodo": "Periodo académico",
        "Matriculados": "Estudiantes matriculados",
        "Programa": "Programa académico"})

# Ajustes visualies de la gráfica en Streamlit
fig_series.update_layout(
    height=550,

    font=dict(family="Arial",size=12,color="#000000"),

    title=dict(x=0.5, xanchor="center",
        font=dict(size=18, color="#000000")),

    xaxis=dict(
    title=dict(
        text="Periodo académico",
        font=dict(size=14, color="#000000")
    ),
    type="category",
    categoryorder="array",
    categoryarray=periodos,
    tickfont=dict(size=12, color="#000000")
),

yaxis=dict(
    title=dict(
        text="Número de estudiantes matriculados",
        font=dict(size=14, color="#000000")
    ),
    tickfont=dict(size=12, color="#000000"),
    rangemode="tozero"
),

legend=dict(
    title=dict(
        text="Programas académicos",
        font=dict(size=13, color="#000000")
    ),
    orientation="h",
    y=-0.25,
    x=0,
    font=dict(size=11, color="#000000")
),

    hovermode="x unified",
    plot_bgcolor="rgba(255,255,255,0.85)",
    paper_bgcolor="rgba(255,255,255,0.80)",
    margin=dict(l=60,r=40,t=80,b=80)
)
# Código para que se visualice la gráfica en el espacio de streamlit, debajo de la tabla resumen de estadísticas
st.plotly_chart(fig_series, use_container_width=True)
