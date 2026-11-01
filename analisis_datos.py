import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

#==================================================================================================================================
#Lectura de datos basado en el archivo Matriz_SNIES_2020_2025.csv para que sea reconocido por Streamlit
#==================================================================================================================================

#diseño de una función principal para obtener la información condensada que se requiere para el análisis exploratorio
#--------------------------------------------------------------------------------------------------------------------
@st.cache_data
def preparar_datos():

    #Caragar la información que está disponible en Matriz_SNIES_2020_2025.csv
    datos_explora = pd.read_csv("Matriz_SNIES_2020_2025.csv",encoding="utf-8-sig")
    datos_explora.columns = datos_explora.columns.str.strip()

    periodos = [f"{ano}-{semestre}"
    for ano in range(2020, 2026)
        for semestre in [1, 2]
    ]

    #Ajuste de membretes para la presentación que se hace en Streamlit
    datos_explora_long = datos_explora.melt(
        id_vars=[
            "DEPARTAMENTO DE OFERTA DEL PROGRAMA",
            "PROGRAMA ACADEMICO"],
        value_vars=periodos,
        var_name="Periodo",
        value_name="Matriculados"
    )

    #Conversión de datos en datos numéricos para poder obtener la suma y promedio de información por departamento y semestre
    datos_explora_long["Matriculados"] = pd.to_numeric(datos_explora_long["Matriculados"],errors="coerce")
    datos_explora_long["Año"] = datos_explora_long["Periodo"].str[:4].astype(int)
    datos_explora_long["Semestre"] = datos_explora_long["Periodo"].str[-1].astype(int)

    datos_explora_long.rename(columns={
        "DEPARTAMENTO DE OFERTA DEL PROGRAMA": "Departamento",
        "PROGRAMA ACADEMICO": "Programa"}, inplace=True)

    # Procedimiento para sumar la matrícula de programas con la misma denominación asociado a un departamento y semestre.
    matricula_semestral = (
        datos_explora_long.groupby(
            ["Departamento", "Programa", "Año", "Semestre"],
            as_index=False
        )["Matriculados"]
        .sum(min_count=1)
    )

    #Se obtiene el promedio semestral de cada año
    matricula_anual = (
        matricula_semestral.groupby(
            ["Departamento", "Programa", "Año"],
            as_index=False
        )["Matriculados"]
        .mean()
    )

    #Se devuelve la información concentrada como objeto matricula_anual
    return matricula_anual

#El objeto matricula_anual contiene toda la ejecución y procedimientos particulares que se declaran en la función preparar_datos
matricula_anual = preparar_datos()
#--------------------------------------------------------------------------------------------------------------------------------

#Visualización del membrete para selección del departamento y año (Pagina 2: Analisis_exploratorio)
#-------------------------------------------------------------------------------------------------------------------------------
st.title("Análisis Exploratorio de Matrícula")

st.markdown("""Distribución de estudiantes matriculados en programas de ingeniería de las instituciones de educación superior
durante el periodo 2020-2025.""")

col1, col2 = st.columns(2)

with col1:
    departamento = st.selectbox("Seleccione el departamento:", sorted(matricula_anual["Departamento"].unique()))

with col2:
    ano = st.selectbox("Seleccione el año:", sorted(matricula_anual["Año"].unique()), index=5)

datos = matricula_anual[(matricula_anual["Departamento"] == departamento) & (matricula_anual["Año"] == ano)].copy()
#--------------------------------------------------------------------------------------------------------------------------------

#Datos resumen que se presentarán una vez se tenga seleccionado el departamento y el año
#---------------------------------------------------------------------------------------------------------------------------------
total_matriculados = datos["Matriculados"].sum()
total_programas = datos["Programa"].nunique()
promedio_matricula = datos["Matriculados"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Matrícula promedio semestral", f"{total_matriculados:,.0f}")

with col2:
    st.metric("Programas académicos",total_programas)

with col3:
    st.metric("Promedio por programa",f"{promedio_matricula:,.1f}")

#----------------------------------------------------------------------------------------------------------------------------

datos = datos.sort_values("Matriculados", ascending=True)

#Creación de un diagrama de barras para mostrar el numéro de matriculados en ingeniería según departamento y año
fig = px.bar(
    datos,
    x="Matriculados",
    y="Programa",
    orientation="h",
    text="Matriculados",
    color="Matriculados",
    color_continuous_scale="Blues",
    title=f"Matrícula en programas de ingeniería - {departamento} ({ano})")

#Estructura de información, membretes y colores en el gráfico generado
fig.update_layout(
    height=max(500, len(datos) * 40),

    # Configuración general de texto
    font=dict(family="Arial",size=13,color="#000000"),
    # Título principal
    title_font=dict(size=20,color="#000000"),
    # Eje horizontal
    xaxis=dict(
        title="Matrícula promedio semestral",
        title_font=dict(size=14, color="#000000"),
        tickfont=dict(size=12, color="#000000"),
        showgrid=True,
        gridcolor="rgba(100,100,100,0.15)"
    ),
    # Eje vertical: nombres de las ingenierías
    yaxis=dict(
        title="Programa académico",
        title_font=dict(size=14, color="#000000"),
        tickfont=dict(
            family="Arial",
            size=12,
            color="#000000"
        ),
        automargin=True
    ),

    # Fondo del gráfico
    plot_bgcolor="rgba(255,255,255,0.75)",
    paper_bgcolor="rgba(255,255,255,0.65)",
    # Ocultar escala de colores
    coloraxis_showscale=False,
    # Márgenes para nombres largos
    margin=dict(l=280,r=70,t=80,b=70)
)


fig.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside")

st.plotly_chart(fig,use_container_width=True)
#--------------------------------------------------------------------------------------------------------------------------
