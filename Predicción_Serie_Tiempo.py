import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

#Proceso de configuración del periodo de entrenamiento y periodo de evaluación
#--------------------------------------------------------------------------------------
periodos = [
    f"{ano}-{semestre}"
    for ano in range(2020, 2026)
    for semestre in [1, 2]
    if not (ano == 2025 and semestre == 2)]

periodo_evaluacion = "2025-2"
todos_periodos = periodos + [periodo_evaluacion]

#Criterio para agrupación del promedio movil
VENTANA_PM = 3
#--------------------------------------------------------------------------------------

#preparación de los datos de acuerdo a la información de serie temporal SNIES 2020-2025
#----------------------------------------------------------------------------------------------------------------
@st.cache_data
def cargar_datos():

    datos_pronostico = pd.read_csv("Matriz_SNIES_2020_2025.csv", encoding="utf-8-sig")

    datos_pronostico.columns = datos_pronostico.columns.str.strip()
    columnas_numericas = todos_periodos
    datos_pronostico[columnas_numericas] = datos_pronostico[
        columnas_numericas
    ].apply(
        pd.to_numeric,
        errors="coerce")

    return datos_pronostico
#---------------------------------------------------------------------------------------------------------------

#Titulos para la visualización en de información en Streamlit
#---------------------------------------------------------------------------------------------------------------
st.title("Pronóstico de Matrícula Universitaria")

st.markdown("""Comparación de tres técnicas de pronóstico: Naive, Promedio movil y Suavización Exponencial Simple""")
st.markdown("""**Entrenamiento:** 2020-I a 2025-I (11 observaciones).
**Evaluación:** matrícula real de 2025-II.""")

datos_pronostico = cargar_datos()
#----------------------------------------------------------------------------------------------------------------

#Construcción de los filtros para visualización del pronóstico de la carrera universitaria por universidad y departamento
#------------------------------------------------------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

col_departamento = "DEPARTAMENTO DE OFERTA DEL PROGRAMA"
col_universidad = ("INSTITUCION DE EDUCACION SUPERIOR (IES)")
col_programa = "PROGRAMA ACADEMICO"
col_codigo = "CODIGO SNIES DEL PROGRAMA"

with col1:

    departamento = st.selectbox("Seleccione el departamento:", sorted(datos_pronostico[col_departamento].dropna().unique()))

df_departamento = datos_pronostico[datos_pronostico[col_departamento] == departamento]


with col2:

    universidad = st.selectbox("Seleccione la universidad:",
        sorted(df_departamento[col_universidad].dropna().unique()))

df_universidad = df_departamento[df_departamento[col_universidad] == universidad].copy()


# Crear identificador para cada registro académico
# Se conserva el índice para distinguir registros repetidos.

df_universidad["Identificador"] = (df_universidad[col_programa].astype(str)+ " - SNIES "
    + df_universidad[col_codigo].astype(str)+ " - Registro "+ df_universidad.index.astype(str))

with col3:

    programa = st.selectbox("Seleccione el programa académico:", sorted(df_universidad["Identificador"].unique()))


# Procedimiento para seleccionar un solo registro para la visualización en Streamlit
registro = df_universidad[df_universidad["Identificador"] == programa].iloc[0]

#------------------------------------------------------------------------------------------------------------------------

#Definición de las once observaciones temporales para aplicar las técnicas de pronóstico
y = registro[periodos].to_numpy(dtype=float)
#Esta variable guarda el valor de evaluación (2025-20)
valor_real = float(registro[periodo_evaluacion])

#Validación de los datos
#-------------------------------------------------------------
if not np.isfinite(y).all():
    st.error("La serie histórica contiene valores faltantes. "
        "Revise las 11 observaciones antes de pronosticar.")
    st.stop()


if not np.isfinite(valor_real):
    st.warning("No existe un valor real válido para 2025-II. "
        "No es posible calcular los errores de evaluación.")
    st.stop()
#-------------------------------------------------------------

#=============================================================================================================
#Técnicas de pronósticos para la serie de tiempo de estudiantes matriculados

#A. Pronóstico con la técnica Naive (Pronóstico histórico de un paso hacia adelante)
#-------------------------------------------------------------------------------------
naive_historico = np.full(len(y), np.nan)
naive_historico[1:] = y[:-1]

# Pronóstico para 2025-II
pronostico_naive = float(y[-1])
#-------------------------------------------------------------------------------------

#B. Promedio móvil simple
#-------------------------------------------------------------------------------------
serie_y = pd.Series(y)
pm_historico = (serie_y
    .shift(1)
    .rolling(window=VENTANA_PM)
    .mean()
    .to_numpy())

# Pronóstico para 2025-II
pronostico_pm = float(np.mean(y[-VENTANA_PM:]))
#-------------------------------------------------------------------------------------

#C. Suavización exponencial simple
#--------------------------------------------------------------------------------------
modelo_ses = SimpleExpSmoothing(y,initialization_method="estimated")
ajuste_ses = modelo_ses.fit(optimized=True)

# Calculo recursivo de la formula de suavización exponencial
ses_historico = np.asarray(ajuste_ses.fittedvalues,dtype=float)

# Pronóstico para 2025-II
pronostico_ses = float(np.asarray(ajuste_ses.forecast(1))[0])

# Parámetro de suavización
alpha = ajuste_ses.params["smoothing_level"]
#--------------------------------------------------------------------------------------

#Comparación de las tres técnicas con el dato de evaluación (2025-20)
resultados = pd.DataFrame({"Método": ["Naive","Promedio móvil (3)","Suavizamiento exponencial (SES)"],

    "Pronóstico 2025-II": [pronostico_naive,pronostico_pm,pronostico_ses]
})

#Se establece el valor real para la comparación
resultados["Valor real 2025-II"] = valor_real

#Calculo del error del pronóstico
resultados["Error"] = (resultados["Valor real 2025-II"]- resultados["Pronóstico 2025-II"])

#Obtención del Error absoluto
resultados["Error absoluto"] = (resultados["Error"].abs())

#Obtención del Error Cuadrático
resultados["Error cuadrático"] = (resultados["Error"] ** 2)

#Comparación de métricas para seleccionar la mejor técnica de pronósticos para la proyección de matriculados

resultados = resultados.sort_values(by=["Error absoluto", "Error cuadrático"],
    ascending=True).reset_index(drop=True)

mejor_metodo = resultados.iloc[0]["Método"]

mejor_pronostico = resultados.iloc[0]["Pronóstico 2025-II"]

# Redondear el pronóstico al número entero de estudiantes
mejor_pronostico_entero = int(np.floor(mejor_pronostico + 0.5))

#Se selecciona por el mejor valor de error abosluto
mejor_error = resultados.iloc[0]["Error absoluto"]

#Se desempata considerando el error cuadrático
metodos_empatados = resultados[
    np.isclose(
        resultados["Error absoluto"],
        mejor_error)
]["Método"].tolist()

#=============================================================================================================


#Información de los pronósticos para visualización en Streamlit
#-------------------------------------------------------------------------------------------------------------
st.divider()

st.subheader("Resultados del pronóstico")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric("Matrícula real 2025-II",f"{valor_real:,.0f}")

with col2:

    st.metric("Mejor pronóstico",f"{mejor_pronostico_entero:,}")

with col3:

    st.metric("Menor error absoluto",f"{mejor_error:,.2f}")


st.subheader("Comparación de técnicas")

st.dataframe(resultados.round(2),use_container_width=True,hide_index=True)

if len(metodos_empatados) == 1:

    st.success(
        f"El método con menor error absoluto "
        f"en 2025-II fue: {mejor_metodo}. "
        f"Pronóstico: {mejor_pronostico:,.2f} estudiantes.")

else:

    st.info(
        "Se presentó un empate en el menor error "
        "absoluto entre: "+ ", ".join(metodos_empatados))

st.caption(
    f"Parámetro estimado del suavizamiento "
    f"exponencial simple: α = {alpha:.4f}")
st.caption(
    f"Se consideró un agrupamiento de: k= {VENTANA_PM}"
    f"para el promedio movil simple")
#-------------------------------------------------------------------------------------------------------------

#Construcción de la gráfica comparativa de la serie de tiempo con las trés técnicas
#--------------------------------------------------------------------------------------------------------------
#Información de los datos de la serie y lo obetnido con las técnicas
real_grafico = np.append(y, valor_real)
naive_grafico = np.append(naive_historico,pronostico_naive)
pm_grafico = np.append(pm_historico,pronostico_pm)
ses_grafico = np.append(ses_historico,pronostico_ses)

#Definici´n del gráfico
st.divider()

st.subheader("Comparación gráfica de los modelos de pronóstico")
fig = go.Figure()


# Graficar la serie de tiempo original
fig.add_trace(go.Scatter(
        x=todos_periodos,
        y=real_grafico,
        mode="lines+markers",
        name="Matrícula real",
        line=dict(
            color="#111827",
            width=4),
        marker=dict(size=8)))


# Graficar el pronóstico de un periodo hacia adelante (Naive)
fig.add_trace(go.Scatter(
        x=todos_periodos,
        y=naive_grafico,
        mode="lines+markers",
        name="Naive",
        line=dict(
            color="#2563EB",
            width=2,
            dash="dash")))


# Graficar el pronóstico obtenido con el promedio movil simple
fig.add_trace(go.Scatter(
        x=todos_periodos,
        y=pm_grafico,
        mode="lines+markers",
        name="Promedio móvil (3)",
        line=dict(
            color="#F59E0B",
            width=2,
            dash="dot")))


# Graficar el pronóstico obtenido con la técnica de Suavización Exponencial Simple
fig.add_trace(go.Scatter(
        x=todos_periodos,
        y=ses_grafico,
        mode="lines+markers",
        name="Suavizamiento exponencial",
        line=dict(
            color="#10B981",
            width=3)))


# Línea divisoria entre entrenamiento y evaluación
fig.add_vline(x=10.5,
    line_dash="dash",
    line_color="#6B7280",
    line_width=1)


# Ajustes de visualización de la gráfica
fig.update_layout(

    title=dict(text="Matrícula real y pronósticos semestrales",
        x=0.5,
        font=dict(
            size=18,
            color="#000000")),

    height=600,
    font=dict(
        family="Arial",
        size=12,
        color="#000000"),

    xaxis=dict(
        title="Periodo académico",
        type="category",
        categoryorder="array",
        categoryarray=todos_periodos,
        tickfont=dict(color="#000000"),
        title_font=dict(color="#000000")),

    yaxis=dict(
        title="Estudiantes matriculados",
        tickfont=dict(color="#000000"),
        title_font=dict(color="#000000"),
        rangemode="tozero"),

    legend=dict(
        orientation="h",
        y=-0.25,
        x=0,
        font=dict(color="#000000")),

    hovermode="x unified",
    plot_bgcolor="rgba(255,255,255,0.90)",
    paper_bgcolor="rgba(255,255,255,0.85)",

    margin=dict(l=60,r=40,t=90,b=110)
)

#Visualizar la gráfica final en la página de visualización de Streamlit
st.plotly_chart(fig,use_container_width=True)

st.caption(
    "Las curvas de los modelos representan "
    "predicciones de un semestre adelante. "
    "La línea divisoria separa los datos de "
    "entrenamiento del periodo de evaluación 2025-II.")


#Conclusión final del proceso de predidcción con series de tiempo para estudiantes matriculados
st.divider()

st.subheader("Conclusión del análisis")
st.write(
    f"Para el programa seleccionado, el método "
    f"**{mejor_metodo}** obtuvo uno de los menores "
    f"errores absolutos al pronosticar la matrícula "
    f"del semestre 2025-II.")
st.write(
    f"El valor pronosticado fue de "
    f"**{mejor_pronostico_entero:,} estudiantes**, "
    f"frente a un valor observado de "
    f"**{valor_real:,.0f} estudiantes**.")
st.info(
    "La comparación corresponde a un único "
    "periodo de evaluación. Este resultado no "
    "garantiza que el método seleccionado "
    "sea superior en futuros semestres.")
#--------------------------------------------------------------------------------------------------------------
