import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from mplsoccer.pitch import VerticalPitch
import os

## -------------------------------------------- DICCIONARIOS --------------------------------

posiciones_map = {
    'G': 'Portero',
    'D': 'Defensa',
    'M': 'Mediocampista',
    'F': 'Delantero'
}

colores_oponentes = {
    'Universidad César Vallejo': 'blue',
    'Alianza Atlético de Sullana': 'darkturquoise',
    'Universitario': 'burlywood',
    'Unión Comercio': 'green',
    'Comerciantes Unidos': 'purple',
    'Asociación Deportiva Tarma': 'cyan',
    'Club Sporting Cristal': 'aqua',
    'Cienciano': 'red',
    'Los Chankas CYC': 'brown',
    'Carlos A. Mannucci': 'blue',
    'Club Atlético Grau': 'yellow',
    'Sport Boys': 'pink',
    'Melgar': 'black',
    'Universidad Técnica de Cajamarca': 'brown',
    'Sport Huancayo': 'red',
    'Deportivo Garcilaso': 'crimson',
    'Cusco FC': 'yellow',
    'Fluminense': 'green',
    'Cerro Porteño': 'red',
    'Colo Colo': 'white',
    }

torneos_d = {
    'Apertura Liga 1': 'Apertura',
    'Copa Libertadores': 'CL',
}

rivales_directos_peru = {
    'Universitario de Deportes': True,
    'Sporting Cristal': True,
    'Melgar': True,
    'Cienciano': True,
    'Atlético Grau': False,
    'UTC': False,
    'Universidad Cesar Vallejo': False,
    'Cusco': False,
    'Sport Huancayo': False,
    'ADT': False,
    'Sport Boys': False,
    'Alianza Atlético de Sullana': False,
    'Carlos Manucci': False,
    'Deportivo Garcilaso': False,
    'Unión Comercio': False,
    'Comerciantes Unidos': False,
    'Los Chankas': False, 
}

rivales_directos_copa = {
    'Fluminense': True,
    'Cerro Porteño': True,
    'Colo Colo': True,
}

colores_posicion = {
        'G': 'red',
        'D': 'green',
        'M': 'purple',
        'F': 'blue'
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

## -------------------------------- INITIAL CONFIG -----------------------------------

def configurar_pagina():
    st.set_page_config(
        page_title="Análisis de jugadores de Alianza Lima Temporada 2024",
        layout='wide',
        page_icon=r'Aplicacion Final\Imagenes\AL.png',
        initial_sidebar_state="expanded")
    titulo, alianza = st.columns([2,1])
    with titulo:
        st.title('GRONESTATS')
        st.subheader('Análisis estadístico de Alianza Lima')
    with alianza:
        st.image(f'Aplicacion Final\Imagenes\AL.png', width=80)

def imprimir_escudo_oponente(equipo_oponente, torneos):
    for torneo in torneos:
        image_path = os.path.join(r'Aplicacion Final\Imagenes\Oponentes', torneo, f"{equipo_oponente}.png")
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                st.image(image,width=185)
                return  # Salir de la función si se encuentra la imagen
            except Exception as e:
                st.write(f"Error al abrir la imagen: {e}")
                return
    st.write(f"No se encontró el escudo para {equipo_oponente} en los torneos seleccionados")

def imprimir_escudo_AL():
    image_path = os.path.join(r'Aplicacion Final\Imagenes\AL.png')
    if os.path.exists(image_path):
        try:
            image = Image.open(image_path)
            st.image(image,width=151)
            return
        except Exception as e:
            st.write(f"Error al abrir la imagen: {e}")
            return

## -------------------------------------- GRAPH FUNCTIONS ------------------------------------------------

def mostrar_xi_inicial_oponente(df_titulares_oponente,df_sustitutos_oponente,df_posiciones_prom_op, df_posiciones_prom_AL, incluir_sustitutos=False, incluir_al=False):
    
    orden_posicion = {'G': 0, 'D': 1, 'M': 2, 'F': 3}

    df_posiciones_prom = df_posiciones_prom_op[df_posiciones_prom_op['name'].isin(df_titulares_oponente['name'])]
    df_posiciones_prom.drop(['slug', 'shortName', 'userCount', 'id',  'pointsCount'], axis=1, inplace=True)
    df_posiciones_prom['orden'] = df_posiciones_prom['position'].map(orden_posicion)
    df_posiciones_prom.sort_values(by='orden', inplace=True)
    
    df_pos_sustitutos = df_posiciones_prom_op[df_posiciones_prom_op['name'].isin(df_sustitutos_oponente['name'])]

    xi_titular = df_posiciones_prom['name']
    sustitutos = df_pos_sustitutos['name']
    xi_titular_al = df_posiciones_prom_AL['name']

    fig, ax = plt.subplots(figsize=(23, 13))
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    for jugador in xi_titular:
        fila_jugador = df_posiciones_prom[(df_posiciones_prom['name'] == jugador)]
        if not fila_jugador.empty:
            equipo = fila_jugador['team'].values[0]
            color = colores_oponentes.get(equipo, 'black')  
            pitch.scatter((fila_jugador['averageX'].values[0]), (fila_jugador['averageY'].values[0]), ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
            ax.text((fila_jugador['averageY'].values[0]),(fila_jugador['averageX'].values[0]), fila_jugador['jerseyNumber'].values[0], color='white', ha='center', va='center', fontsize=10, zorder=2)
            ax.set_title(f"Posicion promedio del 11 titular de {equipo}", fontsize=14)

    if incluir_sustitutos:
        for sustituto in sustitutos:
            fila_sustituto = df_pos_sustitutos[(df_pos_sustitutos['name'] == sustituto)]
            if not fila_sustituto.empty:
                pitch.scatter(fila_sustituto['averageX'], fila_sustituto['averageY'], ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)

    if incluir_al:
        for jugador in xi_titular_al:
            fila_jugador = df_posiciones_prom_AL[(df_posiciones_prom_AL['name'] == jugador)]
            if not fila_jugador.empty: 
                pitch.scatter(100-(fila_jugador['averageX'].values[0]), 100-(fila_jugador['averageY'].values[0]), ax=ax, s=200, color='darkblue', edgecolors='black', linewidth=2.5, zorder=1)
                ax.text(100-(fila_jugador['averageY'].values[0]),100- (fila_jugador['averageX'].values[0]), fila_jugador['jerseyNumber'].values[0], color='black', ha='center', va='center', fontsize=10, zorder=2)


    legend_elements = []

    for _, row in df_posiciones_prom.iterrows():
        color = colores_posicion.get(row['position'], 'black')
        legend_elements.append(Patch(facecolor=color, edgecolor='black', label=f"{row['name']} #{row['jerseyNumber']}"))

    # Añadir la leyenda dentro del mismo gráfico
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)

def mostrar_xi_inicial(df_titulares, df_sustitutos, df_posiciones_prom_AL , df_posiciones_prom_op, incluir_sustitutos=False, incluir_oponentes=True):
    
    orden_posicion = {'G': 0, 'D': 1, 'M': 2, 'F': 3}
    
    df_pos_sustitutos = df_posiciones_prom_AL[df_posiciones_prom_AL['name'].isin(df_sustitutos['name'])]
    
    df_posiciones_prom = df_posiciones_prom_AL[df_posiciones_prom_AL['name'].isin(df_titulares['name'])]
    df_posiciones_prom.drop(['slug', 'shortName', 'userCount', 'id', 'firstName', 'lastName', 'pointsCount'], axis=1, inplace=True)
    df_posiciones_prom['orden'] = df_posiciones_prom['position'].map(orden_posicion)
    df_posiciones_prom.sort_values(by='orden', inplace=True)
    df_posiciones_prom = df_posiciones_prom.merge(df_titulares[['name','minutesPlayed', 'captain']], on='name', how='left')

    xi_titular = df_posiciones_prom['name']
    sustitutos = df_pos_sustitutos['name']
    xi_titular_op = df_posiciones_prom_op['name']

    # GRAFICAR CANCHA
    fig, ax = plt.subplots(figsize=(23, 12))
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    for jugador in xi_titular:
        fila_jugador = df_posiciones_prom[(df_posiciones_prom['name'] == jugador)]
        if not fila_jugador.empty:
            posicion = fila_jugador['position'].values[0]
            color = colores_posicion.get(posicion, 'black') 
            pitch.scatter(fila_jugador['averageX'], fila_jugador['averageY'], ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
            ax.text(fila_jugador['averageY'].values[0], fila_jugador['averageX'].values[0], fila_jugador['jerseyNumber'].values[0], color='white', ha='center', va='center', fontsize=12, zorder=2)
            ax.set_title(f"Posicion promedio del 11 titular de Alianza Lima", fontsize=14)
    if incluir_sustitutos:
        for sustituto in sustitutos:
            fila_sustituto = df_pos_sustitutos[(df_pos_sustitutos['name'] == sustituto)]
            if not fila_sustituto.empty:
                pitch.scatter(fila_sustituto['averageX'], fila_sustituto['averageY'], ax=ax, s=200, color='blue', edgecolors='black', linewidth=2.5, zorder=1)

    if incluir_oponentes:
        for jugador in xi_titular_op:
            fila_jugador = df_posiciones_prom_op[(df_posiciones_prom_op['name'] == jugador)]
            if not fila_jugador.empty:
                posicion = fila_jugador['position'].values[0]
                equipo = fila_jugador['team'].values[0]
                color = colores_oponentes.get(equipo, 'black')  
                pitch.scatter(100-(fila_jugador['averageX'].values[0]), 100-(fila_jugador['averageY'].values[0]), ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
                ax.text(100-(fila_jugador['averageY'].values[0]),100- (fila_jugador['averageX'].values[0]), fila_jugador['jerseyNumber'].values[0], color='black', ha='center', va='center', fontsize=10, zorder=2)

    legend_elements = []

    for _, row in df_posiciones_prom.iterrows():
        color = colores_posicion.get(row['position'], 'black')
        legend_elements.append(Patch(facecolor=color, edgecolor='black', label=f"{row['name']} #{row['jerseyNumber']}"))

    # Añadir la leyenda dentro del mismo gráfico
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)

## ------------------------------------------------- ZONA TEST ---------------------------------------

def mostrar_grafico(df_estadisticas_partidos,categoria, subcategoria):
    if categoria == "Ataque":
        if subcategoria == "Creación de Oportunidades":
            stats = ['Big chances', 'Big chances scored', 'Big chances missed', 'Final third entries', 'Fouled in final third']
        elif subcategoria == "Remates":
            stats = ['Total shots', 'Shots on target', 'Shots off target', 'Blocked shots', 'Shots inside box', 'Shots outside box', 'Hit woodwork']
        elif subcategoria == "Desbordes y Centros":
            stats = ['Dribbles', 'Tried Dribbles', 'Crosses', 'Tried Crosses']
    elif categoria == "Defensa":
        if subcategoria == "Recuperación de Balón":
            stats = ['Tackles', 'Tackles won', 'Total tackles', 'Interceptions', 'Recoveries']
        elif subcategoria == "Despejes":
            stats = ['Clearances']
        elif subcategoria == "Duelos":
            stats = ['Duels', 'Ground duels', 'Aerial duels', 'Tried Ground duels', 'Tried Aerial duels', 'Dispossessed']
    elif categoria == "Portero":
        stats = ['Goalkeeper saves', 'Total saves', 'Goal kicks']
    elif categoria == "Juego General":
        stats = ['Passes', 'Accurate passes', 'Long balls', 'Tried Long balls', 'Corner kicks', 'Free kicks', 'Throw-ins', 'Offsides', 'Fouls']
    
    df_filtered = df_estadisticas_partidos[df_estadisticas_partidos['Estadistica'].isin(stats)]
    df_pie = pd.melt(df_filtered, id_vars=['Estadistica'], value_vars=['Alianza', 'Oponente'],
                     var_name='Equipo', value_name='Cantidad')
    
    fig = px.bar(df_pie, x='Cantidad', y='Estadistica', color='Equipo', barmode='relative',
                 orientation='h', title=f'Estadísticas de {subcategoria} en la Categoría {categoria}')
    fig.update_layout(showlegend=False) 
    st.plotly_chart(fig, use_container_width=True)

def calcular_rendimiento(df):
    # Transponer el DataFrame para que las estadísticas estén en columnas
    df_transposed = df.set_index(df.columns[0]).T
    st.dataframe(df_transposed)
    df_transposed['Rendimiento_Ataque'] = df_transposed[['Big chances', 'Total shots', 'Shots on target', 'Dribbles', 'Crosses']].sum(axis=1)
    df_transposed['Rendimiento_Defensa'] = df_transposed[['Tackles', 'Interceptions', 'Clearances', 'Duels']].sum(axis=1)
    df_transposed['Rendimiento_Juego_General'] = df_transposed[['Passes', 'Accurate passes', 'Long balls', 'Fouls']].sum(axis=1)
    
    
    df_result = df_transposed.T.reset_index()
    return df_result

def mostrar_grafico_ternario(df, equipo):
    df = df.set_index(df.columns[0]).T
    fig = px.scatter_ternary(df, a='Rendimiento_Ataque', b='Rendimiento_Defensa', c='Rendimiento_Juego_General',
                             title=f'Gráfico Ternario de Rendimiento - {equipo}')
    st.plotly_chart(fig, use_container_width=True)

def mostrar_grafico_barras(df):
    orden_posicion = {'G': 0, 'D': 1, 'M': 2, 'F': 3}
    df['orden'] = df['position'].map(orden_posicion)
    df.sort_values(by='orden', inplace=True)
    df['color'] = df['position'].map(colores_posicion)

    fig = px.bar(df, x='minutesPlayed', y='shortName', orientation='h',
                 title='Minutos Jugados por Jugador', labels={'minutesPlayed': 'Minutos Jugados', 'shortName': 'Jugador'},
                 color='position', color_discrete_map=colores_posicion, text='minutesPlayed',
                 hover_data={'color': False, 'position': False})
    fig.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig.update_layout(showlegend=False, xaxis_title='Minutos Jugados', yaxis_title='Jugador')  # Ocultar leyenda
    st.plotly_chart(fig, use_container_width=True)
    
    fig2 = px.bar(df, x='touches', y='shortName', orientation='h',
                  title='Toques por Jugador', labels={'touches': 'Toques', 'shortName': 'Jugador'},
                  color='position', color_discrete_map=colores_posicion, text='touches',
                  hover_data={'color': False, 'position': False})
    fig2.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig2.update_layout(showlegend=False, xaxis_title='Toques', yaxis_title='Jugador')  # Ocultar leyenda
    st.plotly_chart(fig2, use_container_width=True)

def mostrar_grafico_posesion(df_estadisticas_partido,condicion):
    df_ball_possession = df_estadisticas_partido[df_estadisticas_partido['Estadistica'] == 'Ball possession']
    if condicion == "Local":
        df_pie = pd.melt(df_ball_possession, id_vars=['Estadistica'], value_vars=['Alianza', 'Oponente'],
                         var_name='Equipo', value_name='Porcentaje')
    else:
        df_ball_possession = df_ball_possession[['Estadistica', 'Oponente', 'Alianza']]
        df_pie = pd.melt(df_ball_possession, id_vars=['Estadistica'], value_vars=['Oponente', 'Alianza'],
                         var_name='Equipo', value_name='Porcentaje')
    
    # Definir colores específicos para cada equipo
    colors = {'Alianza': 'darkblue', 'Oponente': 'cream'}  

    fig = px.pie(df_pie, values='Porcentaje', names='Equipo', title='Posesión de Balón',
                 color='Equipo', color_discrete_map=colors)
    
    fig.update_layout(width=400, height=400)
    st.plotly_chart(fig, use_container_width=True)


## ------------------------------------------------ MAIN FUNCTION ---------------------------------

def main():
    # --------------------------------------------- CARGA RESUMEN Y STATS TOTALES AL -------------------------------------
    df_jornadas = pd.read_excel(r'Aplicacion Final\2024\Resumen_Partidos_AL_2024.xlsx')
    df_stats_AL = pd.read_excel(r'Aplicacion Final\2024\Estadisticas_Jugadores_AL_2024.xlsx')

    configurar_pagina()
    # --------------------------------------------- BARRA LATERAL ----------------------------------------------------
    with st.sidebar:
        torneos = df_jornadas['Torneo'].unique()
        torneos_seleccionados = st.multiselect("Filtra por torneo: ",torneos,default=torneos)
        df_torneos_filtrados = df_jornadas[df_jornadas['Torneo'].isin(torneos_seleccionados)]
        s_goles_al , s_goles_op = st.columns(2)
        with s_goles_al:
            min_goles_alianza, max_goles_alianza = st.slider('Goles Alianza Lima', 
                                                    min_value=int(df_jornadas['Goles Alianza Lima'].min()), 
                                                    max_value=int(df_jornadas['Goles Alianza Lima'].max()), 
                                                    value=(int(df_jornadas['Goles Alianza Lima'].min()), int(df_jornadas['Goles Alianza Lima'].max())))
        with s_goles_op:
            min_goles_oponente, max_goles_oponente = st.slider('Goles Oponente', 
                                                    min_value=int(df_jornadas['Goles Oponente'].min()), 
                                                    max_value=int(df_jornadas['Goles Oponente'].max()), 
                                                    value=(int(df_jornadas['Goles Oponente'].min()), int(df_jornadas['Goles Oponente'].max())))
        df_jornadas_filtradas = df_torneos_filtrados[(df_torneos_filtrados['Goles Alianza Lima'] >= min_goles_alianza) & 
                                    (df_torneos_filtrados['Goles Alianza Lima'] <= max_goles_alianza) & 
                                    (df_torneos_filtrados['Goles Oponente'] >= min_goles_oponente) & 
                                    (df_torneos_filtrados['Goles Oponente'] <= max_goles_oponente)]
        resultados = df_jornadas['Resultado'].unique()
        resultados_seleccionados = st.multiselect("Filtra por resultado:",resultados,default=resultados)
        opciones = df_jornadas['Condicion'].unique()
        localia_seleccionada = st.multiselect("Filtra por localia:", opciones,default=opciones)
        if resultados_seleccionados and localia_seleccionada:
            df_jornadas_filtradas = df_jornadas_filtradas[df_jornadas_filtradas['Resultado'].isin(resultados_seleccionados)]
            df_jornadas_filtradas = df_jornadas_filtradas[df_jornadas_filtradas['Condicion'].isin(localia_seleccionada)]

    ## ----------------------------------------- CUERPO --------------------------------------------------------
    
    p_resumen , p_equipo , p_jornadas , p_jugadores = st.tabs(["Resumen 2024","Equipo","Jornadas", "Jugadores"])
    
    # -------------------------- CARGA DE DATOS TOTALES X TORNEO ----------------------------------
    t = df_torneos_filtrados['Torneo'].map(torneos_d).values[0]
    df_stats_totales_torneo = pd.read_excel(f'Aplicacion Final/2024/Datos totales/Datos_totales_{t}_2024.xlsx',sheet_name='total')
    df_stats_x90_torneo = pd.read_excel(f'Aplicacion Final/2024/Datos totales/Datos_totales_{t}_2024.xlsx',sheet_name='per90')
    # Obtener datos totales de Alianza para el torneo
    df_stats_AL_torneo_total = pd.read_excel(f'Aplicacion Final/2024/Datos totales/Datos_totales_Alianza_Lima_{t}_2024.xlsx',sheet_name='total')
    df_stats_AL_torneo_x90 = pd.read_excel(f'Aplicacion Final/2024/Datos totales/Datos_totales_Alianza_Lima_{t}_2024.xlsx',sheet_name='per90')
    
    with p_resumen:
        promedio_goles_alianza = df_torneos_filtrados['Goles Alianza Lima'].mean()
        promedio_goles_oponente = df_torneos_filtrados['Goles Oponente'].mean()
        
        st.write("Promedio de Goles A favor:", promedio_goles_alianza)
        st.write("Promedio de Goles Recibidos:", promedio_goles_oponente)
        st.dataframe(df_stats_AL_torneo_total)
        st.dataframe(df_stats_AL_torneo_x90)
        st.dataframe(df_stats_totales_torneo)
        st.dataframe(df_stats_x90_torneo)


    with p_jornadas:
        
        jornada_seleccionada = st.selectbox('Selecciona una jornada:', df_jornadas_filtradas['nombre'], key='jornada_selector')
        jornada_filtrada = df_jornadas_filtradas[df_jornadas_filtradas['nombre'] == jornada_seleccionada]
        
        ## DATOS DE RESUMEN
        # id_jornada, nombre, condicion, equipo oponente, torneo, goles alianza lima, goles oponente
        # resultado, dt alianza lima, dt oponente , puntos obtenidos , puntos acumulados
        # Posicion resultante, Importancia,	Puntos1,	Puntos2,	PuntosDif1,	PuntosDif2,	Puntos jugados
        id_jornada = jornada_filtrada['id_jornada'].values[0]
        ## ID JORNADA ENCONTRADO
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
        
        # -------------------------------------- CARGA DE DATOS X JORNADA ------------------------------------------

        # Obtener stats de jugadores de Alianza
        df_stats_AL = df_stats_AL[df_stats_AL['Jornada'] == nombre_jornada]
        # Obtener stats de jugadores del equipo oponente
        df_stats_oponente = pd.read_csv(f'Aplicacion Final/2024/Estadisticas Oponentes 2024/{id_jornada}_stats_jugadores_op.csv')
        # Obtener stats del partido de la jornada
        df_estadisticas_partido = pd.read_excel(r'Aplicacion Final\2024\Estadisticas_Partidos_AL_2024.xlsx', sheet_name=id_jornada)
        # Obtener posicion promedio de Alianza para la jornada
        df_posiciones_prom_AL = pd.read_excel(r'Aplicacion Final\2024\Posiciones promedio AL 2024\Posiciones_Prom_AL_2024.xlsx', sheet_name=id_jornada)
        # Obtener posicion promedio del oponente de la jornada
        df_posiciones_prom_op = pd.read_excel(r'Aplicacion Final\2024\Posiciones promedio Oponente 2024\Posiciones_Prom_Oponentes_2024.xlsx', sheet_name=id_jornada)
        # Obtener mapas de tiro para la jornada
        df_shotmaps = pd.read_excel(r'Aplicacion Final\2024\Mapas de tiro AL 2024\MapaTiros_2024.xlsx', sheet_name=id_jornada)

        # ---------------------------------------------------------------------------------------------
        st.title(f"**Resultado de {condicion}:** {resultado} | {goles_alianza_lima} - {goles_oponente}")
        # XI INICIAL AL
        df_titulares = df_stats_AL[df_stats_AL['substitute']==False]
        df_sustitutos = df_stats_AL[df_stats_AL['substitute']==True]
        # XI INICIAL Oponente
        df_titulares_oponente = df_stats_oponente[df_stats_oponente['substitute']==False]
        df_sustitutos_oponente = df_stats_oponente[df_stats_oponente['substitute']==True]

        df_posprom_titulares_AL = df_posiciones_prom_AL[df_posiciones_prom_AL['name'].isin(df_titulares['name'])]
        df_posprom_titulares_OP = df_posiciones_prom_op[df_posiciones_prom_op['name'].isin(df_titulares_oponente['name'])]

        col1 , col2 , col3 , col4, col5 = st.columns(5)
        with col1:
            imprimir_escudo_AL() 
            st.write('DT: ', dt_alianza_lima)
            # CHECKBOXES
            sustitutos = st.checkbox('Incluir sustitutos', value=False)
            check_oponentes = st.checkbox('Incluir oponentes', value=True)
            mostrar_xi_inicial(df_titulares,df_sustitutos ,df_posiciones_prom_AL , df_posprom_titulares_OP, incluir_sustitutos=sustitutos, incluir_oponentes=check_oponentes)            
            # GRAFICOS DE MINUTOS, TOQUES Y POSESION PERDIDA
            grafico_mtp = df_titulares[['shortName','position','minutesPlayed','touches','possessionLostCtrl']]
            mostrar_grafico_barras(grafico_mtp)
            # ------
            
        with col2:
            imprimir_escudo_oponente(equipo_oponente,torneos_seleccionados)
            st.write('DT: ', dt_oponente)
            # CHECKBOXES
            sustitutos_op = st.checkbox('Incluir sustitutos op.', value=False)
            check_al = st.checkbox('Incluir jugadores AL', value=False)
            mostrar_xi_inicial_oponente(df_titulares_oponente,df_sustitutos_oponente,df_posiciones_prom_op, df_posprom_titulares_AL, incluir_sustitutos=sustitutos_op, incluir_al=check_al)
            # GRAFICOS DE MINUTOS, TOQUES Y POSESION PERDIDA
            grafico_mtp_op = df_titulares_oponente[['shortName','position','minutesPlayed','touches']]
            mostrar_grafico_barras(grafico_mtp_op)
            # ------
            
        with col3:
            # GRAFICO DE POSESION DE BALON 
            mostrar_grafico_posesion(df_estadisticas_partido,condicion)

            st.dataframe(df_stats_AL)
            st.dataframe(df_stats_oponente)
        with col4:
            st.subheader("Estadisticas del Partido")
            # SELECTBOX CATEGORIAS DE JUEGO
            categoria = st.selectbox("Selecciona una categoría", ["Ataque", "Defensa", "Portero", "Creacion de Chances","Juego General", "Balon parado"])
            subcategoria = st.selectbox("Selecciona una subcategoría", ["Remates", "Desbordes y Centros"] if categoria == "Ataque" else 
                                                    ["Creación de Oportunidades"] if categoria == "Creacion de Chances" else
                                                    ["Faltas","Tiros de esquina","Tiros Libres","Otros"]
                                                    ["Recuperación de Balón", "Despejes", "Duelos"] if categoria == "Defensa" else 
                                                    ["Portero"] if categoria == "Portero" else ["Juego General"])
            mostrar_grafico(df_estadisticas_partido,categoria, subcategoria)
        with col5:
            st.subheader("Rendimiento - Alianza Lima")
            df_rendimiento = calcular_rendimiento(df_estadisticas_partido)
            mostrar_grafico_ternario(df_rendimiento, 'Alianza')
            st.dataframe(df_shotmaps)
            
        
if __name__ == "__main__":
    main()