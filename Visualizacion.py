import streamlit as st
import base64
from pathlib import Path
import pandas as pd
#import matplotlib.pyplot as plt
import streamlit.components.v1 as components
#from scipy.io import arff

#Paso inicial para la configuración del título principal de visualización
#-------------------------------------------------------------------------------------------
st.set_page_config(page_title="Mineria_Datos",page_icon="👋",layout = "wide")
#-------------------------------------------------------------------------------------------

#Estructura para colocar el fondo deseado en la visualización de Streamlit
#-------------------------------------------------------------------------------------------------------
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

#Cargar la imagen con manejo de excepciones
try:
    img_base64 = get_base64_image("SNIES_Imagen.png")

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

#Configuración del color de barra de navegación y texto (CSS)
st.markdown(
    """
    <style>

    /* Título principal */
    h1 {color: #000000 !important;}

    /* Encabezados secundarios */
    h2 {color: #000000 !important;}

    /* Subtítulos */
    h3 {color: #000000 !important;}

    /*para los demás textos*/
     p, span, label {color: #000000 !important;}

    /* Fondo claro */
    [data-testid="stSidebar"] {
        background-color: #F0F2F6 !important;}

    </style>
    """,
    unsafe_allow_html=True
)

#========================================================================================================
#Configuración de las páginas y proceso de navegación en Streamlit
#========================================================================================================

#Sobre la página principal del proyecto
pagina_principal = st.Page(
    "pagina_principal.py",
    title="Página Principal",
    icon="🏠",
    default=True
)

# Página de análisis exploratorio
pagina_2 = st.Page(
    "analisis_datos.py",
    title="Análisis Exploratorio",
    icon="📊"
)

#Sobre la página secundaria (Presentación de Grafico de Serie de tiempo)
pagina_3 = st.Page(
    "Estadistica_descrciptiva.py",
    title="Descriptivas",
    icon="📈"
)

pg = st.navigation([
    pagina_principal,
    pagina_2,
    pagina_3
])

pg.run()
