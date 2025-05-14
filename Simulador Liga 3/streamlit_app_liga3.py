import streamlit as st
import pandas as pd
from streamlit_funcs_liga3 import ejecutar_simulacion_liga3  # Importar módulo con la simulación
from graph_parser import generar_dot_desde_log # Importar módulo para parsear el log de playoffs

st.set_page_config(page_title="Simulación Liga 3 2025", layout="wide")

st.title("Simulación Completa de la Liga 3 - Temporada 2025")

st.markdown("""
Esta aplicación simula toda la temporada de la Liga 3, incluyendo fase regular, fase final y playoffs.
Al presionar el botón, se ejecutará la simulación completa y se mostrarán los resultados y todos los partidos jugados.
""")

# Inicialización del estado para controlar si ya se simuló y almacenar resultados
if "simulado" not in st.session_state:
    st.session_state.simulado = False
    st.session_state.resultados = None

def ejecutar_simulacion():
    st.session_state.resultados = ejecutar_simulacion_liga3()
    st.session_state.simulado = True

# Botón para ejecutar la simulación
st.button("Simular Temporada", on_click=ejecutar_simulacion)

# Contenedor para mostrar resultados solo si ya se simuló
with st.container():
    if st.session_state.simulado and st.session_state.resultados is not None:
        resultados = st.session_state.resultados
        st.success("Simulación completada.")
        # Resultado destacado: campeón y subcampeón
        st.header("Resultado de la Simulación")
        st.markdown(
            f"**El resultado de tu simulación de Liga 3 2025 da como campeón a:** 🏆 **{resultados['campeon']}**\n\n"
            f"**Y como subcampeón a:** 🥈 **{resultados['subcampeon']}**"
        )

        # Descensos destacados en dos columnas
        st.header("Equipos Descendidos")
        col1, col2 = st.columns(2)
        descensos_items = list(resultados['descensos'].items())
        for idx, (grupo, equipo) in enumerate(descensos_items):
            with (col1 if idx % 2 == 0 else col2):
                st.markdown(f"- **{equipo}** (Último en {grupo})")

        # Tablas de posiciones fase regular en columnas para mejor legibilidad
        st.header("Tablas de Posiciones - Fase Regular")
        cols = st.columns(2)
        grupos_list = list(resultados['tablas_regulares'].keys())
        for i, grupo in enumerate(grupos_list):
            with cols[i % 2]:
                st.subheader(grupo)
                st.dataframe(resultados['tablas_regulares'][grupo], use_container_width=True)

        # Tabla acumulada fase final
        st.header("Tabla Acumulada - Fase Final")
        st.dataframe(resultados['df_fase_final'], use_container_width=True)

        st.header("Resumen de Playoffs y Eventos")
        col1, col2 = st.columns({3,2})

        with col1:
            st.subheader("Narrativa de Playoffs")
            for evento in resultados['playoffs_log']:
                st.write(evento)

        with col2:
            st.subheader("Visualización de Playoffs")
            dot_code = generar_dot_desde_log(resultados['playoffs_log'])
            st.graphviz_chart(dot_code, use_container_width=True)


        # Separar la exploración de partidos en pestañas
        st.header("Explora los Partidos Jugados")
        tab_filtros, tab_completa = st.tabs(["Partidos con Filtros", "Tabla Completa"])

        with tab_filtros:
            df_partidos = resultados['df_partidos']

            # Opciones de filtro para fase y grupo
            fases = ['Todas'] + sorted(df_partidos['Fase'].dropna().unique())
            grupos_disp = ['Todos'] + sorted(df_partidos['Grupo'].dropna().unique())

            filtro_fase = st.selectbox("Filtrar por Fase", fases, key="filtro_fase")
            filtro_grupo = st.selectbox("Filtrar por Grupo", grupos_disp, key="filtro_grupo")

            df_filtrado = df_partidos.copy()
            if filtro_fase != 'Todas':
                df_filtrado = df_filtrado[df_filtrado['Fase'] == filtro_fase]
            if filtro_grupo != 'Todos':
                df_filtrado = df_filtrado[df_filtrado['Grupo'] == filtro_grupo]

            st.dataframe(df_filtrado.reset_index(drop=True), height=600, use_container_width=True)

        with tab_completa:
            st.dataframe(resultados['df_partidos'].reset_index(drop=True), height=600, use_container_width=True)

    else:
        st.info("Presiona el botón para simular la temporada de la Liga 3 2025.")
