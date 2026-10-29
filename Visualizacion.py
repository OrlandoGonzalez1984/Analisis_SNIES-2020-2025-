import streamlit as st
import base64
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from scipy.io import arff
from pathlib import Path

#Paso inicial para la configuración del título principal de visualización
#-------------------------------------------------------------------------------------------
st.set_page_config(page_title="Mineria_Datos",page_icon="👋",layout = "wide")
#-------------------------------------------------------------------------------------------

#Estructura para colocar el fondo deseado en la visualización de Streamlit
#-------------------------------------------------------------------------------------------------------
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string

#Cargar la imagen con manejo de excepciones
try:
    img_base64 = get_base64_image("SNIES Educativa Colombiana en Tonos Suaves.png")

    # 4. Inyectar el CSS usando la imagen codificada
    background_css = f"""
    <style>

    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

except FileNotFoundError:
    st.error(
        "No se encontró el archivo .png. Asegúrate de que esté en la misma carpeta que este script."
    )
#--------------------------------------------------------------------------------------------------------

#Desarrollo del contenido que tendrá la visualización en Streamlite
#--------------------------------------------------------------------------------------------------------
st.title("Minería de Datos para información SNIES")
st.title("Panel Principal")
#--------------------------------------------------------------------------------------------------------
