
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pathlib import Path

#Titulos Principales en la página principal
#----------------------------------------------

st.title("Minería de Datos para información SNIES")
st.header("Panel Principal")

st.subheader("Integrantes del proyecto")
st.write("Maryory Patricia Villamizar Leon: ID 273164")
st.write("Silvia Alejandra Sotelo: ID 326379")
st.write("Orlando Federico Gonzales Casallas: ID 159090")

# ===============================================
# Informe de Análisis Exploratorio de Datos SNIES
# ===============================================

st.divider()
st.header("Informe exploratorio de los datos")
ruta_html = (Path(__file__).resolve().parent/ "Analisis_Exploratorio_Datos_SNIES.html")

if ruta_html.exists():

    with open(ruta_html,"r",encoding="utf-8") as archivo_html:
        html = archivo_html.read()
    
    components.html(html,height=900,scrolling=True)

else:

    st.info("El informe exploratorio HTML "
        "todavía no está disponible.")
