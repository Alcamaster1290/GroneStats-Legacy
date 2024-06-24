import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from mplsoccer.pitch import VerticalPitch
import os

posiciones_map = {
    'G': 'Portero',
    'D': 'Defensa',
    'M': 'Mediocampista',
    'F': 'Delantero'
}

nombres_pos_map = {
    # Portero
    'POR': 'Portero',
    # Defensa
    'DFI': 'Defensa izquierdo',
    'DFD': 'Defensa derecho',
    'DFC': 'Defensa central',
    'LIB': 'Defensa libero',
    'LD': 'Lateral derecho',
    'LI': 'Lateral izquierdo',
    'CRI': 'Carrilero izquierdo',
    'CRD': 'Carrilero derecho',
    # Mediocampista
    'MCD': 'Mediocampista central def.',
    'MCC': 'Mediocampista contencion',
    'VLX': 'Volante mixto',
    'VLD': 'Volante derecho',
    'VLI': 'Volante izquierdo',
    'MCO': 'Mediocampista enganche',
    # Delantero
    'EXI': 'Extremo izquierdo',
    'EXD': 'Extremo derecho',
    'SDC': 'Segundo delantero centro',
    'DLC': 'Delantero centro'
}

Pos_Prim_Map = {
    'POR': 'G',
    'DFI': 'D',
    'DFD': 'D',
    'DFC': 'D',
    'LIB': 'D',
    'LD': 'D',
    'LI': 'D',
    'CRI': 'D',
    'CRD': 'D',
    'MCD': 'D',
    'MCC': 'M',
    'VLX': 'M',
    'VLD': 'M',
    'VLI': 'M',
    'MCO': 'M',
    'EXI': 'F',
    'EXD': 'F',
    'SDC': 'F',
    'DLC': 'F'
}

Pos_Secu_Map = {
    'POR': '0',
    'DFI': '0',
    'DFD': '0',
    'DFC': '0',
    'LIB': '0',
    'LD': 'M',
    'LI': 'M',
    'CRI': 'M',
    'CRD': 'M',
    'MCD': 'M',
    'MCC': 'D',
    'VLX': '0',
    'VLD': '0',
    'VLI': '0',
    'MCO': 'F',
    'EXI': 'M',
    'EXD': 'M',
    'SDC': '0',
    'DLC': '0'
}

def configurar_pagina():
    st.set_page_config(
        page_title="Análisis de jugadores de Alianza Lima Temporada 2024",
        layout='wide',
        page_icon=r'Imagenes\AL.png',
        initial_sidebar_state="expanded")
    titulo, alianza = st.columns([2,1])
    with titulo:
        st.title('GRONESTATS')
        st.subheader('Analisis estadistico de Alianza Lima')
    with alianza:
        st.image(f'Imagenes\AL.png', width=80)

def imprimir_escudo_oponente(equipo_oponente, torneos):
    for torneo in torneos:
        image_path = os.path.join(r'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\Aplicacion Final\Imagenes\Oponentes', torneo, f"{equipo_oponente}.png")
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                st.image(image,width=195,caption=f"{equipo_oponente}")
                return  # Salir de la función si se encuentra la imagen
            except Exception as e:
                st.write(f"Error al abrir la imagen: {e}")
                return
    st.write(f"No se encontró el escudo para {equipo_oponente} en los torneos seleccionados")

def imprimir_escudo_AL():
    image_path = os.path.join(r'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\Gronestats\Aplicacion Final\Imagenes\AL.png')
    if os.path.exists(image_path):
        try:
            image = Image.open(image_path)
            st.image(image,width=151)
            return
        except Exception as e:
            st.write(f"Error al abrir la imagen: {e}")
            return

def mostrar_xi_inicial(id_jornada,nombre_jornada,df_stats_AL):
    df_filtrado_jugadores = df_stats_AL[df_stats_AL['Jornada'] == nombre_jornada]
    df_filtrado_jugadores = df_filtrado_jugadores[df_filtrado_jugadores['substitute']==False]
    df_posiciones_prom_AL = pd.read_excel(r'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\Aplicacion Final\2024\Posiciones promedio AL 2024\Posiciones_Prom_AL_2024.xlsx', sheet_name=id_jornada)
    df_posiciones_prom_filtradas = df_posiciones_prom_AL[df_posiciones_prom_AL['name'].isin(df_filtrado_jugadores['name'])]
    
    st.dataframe(df_posiciones_prom_filtradas)
    st.dataframe(df_filtrado_jugadores)


def main():

    df_jornadas = pd.read_excel(r'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\Aplicacion Final\2024\Resumen_Partidos_AL_2024.xlsx')
    df_stats_AL = pd.read_excel(r'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\Aplicacion Final\2024\Estadisticas_Jugadores_AL_2024.xlsx')
    
    configurar_pagina()

    p_resumen , p_equipo , p_jornadas , p_jugadores = st.tabs(["Resumen 2024","Equipo","Jornadas", "Jugadores"])
    with p_resumen:
        promedio_goles_alianza = df_jornadas['Goles Alianza Lima'].mean()
        promedio_goles_oponente = df_jornadas['Goles Oponente'].mean()
        
        st.write("Promedio de Goles de Alianza Lima:", promedio_goles_alianza)
        st.write("Promedio de Goles de Oponentes:", promedio_goles_oponente)


    with p_jornadas:



        # id_jornada, nombre, condicion, equipo oponente, torneo, goles alianza lima, goles oponente
        # resultado, dt alianza lima, dt oponente , puntos obtenidos , puntos acumulados
        torneos_seleccionados = st.multiselect("Elegir torneo: ",df_jornadas['Torneo'].unique())
        if torneos_seleccionados:
            df_jornadas = df_jornadas[df_jornadas['Torneo'].isin(torneos_seleccionados)]
            jornada_seleccionada = st.selectbox('Selecciona una jornada:', df_jornadas['nombre'], key='jornada_selector')
            jornada_filtrada = df_jornadas[df_jornadas['nombre'] == jornada_seleccionada]

            id_jornada = jornada_filtrada['id_jornada'].values[0]
            nombre_jornada = jornada_filtrada['nombre'].values[0]
            equipo_oponente = jornada_filtrada['Equipo Oponente'].values[0]
            condicion = jornada_filtrada['Condicion'].values[0]
            goles_alianza_lima = jornada_filtrada['Goles Alianza Lima'].values[0]
            goles_oponente = jornada_filtrada['Goles Oponente'].values[0]
            torneo = jornada_filtrada['Torneo'].values[0]
            resultado = jornada_filtrada['Resultado'].values[0]
            dt_alianza_lima = jornada_filtrada['DT Alianza Lima'].values[0]
            dt_oponente = jornada_filtrada['DT Oponente'].values[0]
            puntos_obtenidos = jornada_filtrada['Puntos obtenidos'].values[0]
            puntos_acumulados = jornada_filtrada['Puntos acumulados'].values[0]
            
            col1 , col2 , col3 , col4, col5 = st.columns(5)
            with col1:
                imprimir_escudo_AL()
                st.markdown(f"**Resultado de {condicion}:** {resultado} | {goles_alianza_lima} - {goles_oponente}")
                st.write('DT: ', dt_alianza_lima)
            with col2:
                imprimir_escudo_oponente(equipo_oponente,torneos_seleccionados)
                st.write('DT: ', dt_oponente)
            with col3:
                st.subheader(f"XI inicial para {nombre_jornada}")
                mostrar_xi_inicial(id_jornada,nombre_jornada,df_stats_AL)

            with col4:
                df_estadisticas_partidos = pd.read_excel(r'Aplicacion Final\2024\Estadisticas_Partidos_AL_2024.xlsx', sheet_name=id_jornada)
                st.dataframe(df_estadisticas_partidos)
            with col5:
                st.subheader(f"Posiciones {torneo}")
                st.write(f"**Puntos obtenidos:** {puntos_obtenidos}")
                st.write(f"**Puntos acumulados:** {puntos_acumulados}")
                
        
if __name__ == "__main__":
    main()