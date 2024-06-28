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

def mostrar_xi_inicial_oponente(id_jornada,df_stats_oponentes,incluir_sustitutos=False):
    
    orden_posicion = {'G': 0, 'D': 1, 'M': 2, 'F': 3}

    df_filtrado_jugadores = df_stats_oponentes[df_stats_oponentes['substitute']==False]
    df_posiciones_prom_op = pd.read_excel(r'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\Aplicacion Final\2024\Posiciones promedio Oponente 2024\Posiciones_Prom_Oponentes_2024.xlsx', sheet_name=id_jornada)
    df_posiciones_prom = df_posiciones_prom_op[df_posiciones_prom_op['name'].isin(df_filtrado_jugadores['name'])]
    df_posiciones_prom.drop(['slug', 'shortName', 'userCount', 'id',  'pointsCount'], axis=1, inplace=True)
    df_posiciones_prom['orden'] = df_posiciones_prom['position'].map(orden_posicion)
    df_posiciones_prom.sort_values(by='orden', inplace=True)
    xi_titular = df_posiciones_prom['name']
    stats_xi_titular = df_filtrado_jugadores

    fig, ax = plt.subplots(figsize=(23, 11))
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    for jugador in xi_titular:
        fila_jugador = df_posiciones_prom[(df_posiciones_prom['name'] == jugador)]
        if not fila_jugador.empty:
            posicion = fila_jugador['position'].values[0]
            equipo = fila_jugador['team'].values[0]
            color = colores_oponentes.get(equipo, 'black')  # Usamos 'black' como color predeterminado si la posición no está en el mapa
            pitch.scatter(100-(fila_jugador['averageX'].values[0]), 100-(fila_jugador['averageY'].values[0]), ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
            ax.text(100-(fila_jugador['averageY'].values[0]),100- (fila_jugador['averageX'].values[0]), fila_jugador['jerseyNumber'].values[0], color='white', ha='center', va='center', fontsize=10, zorder=2)
            ax.set_title(f"Posicion promedio del 11 titular de {equipo}", fontsize=14)

    legend_elements = []

    for _, row in df_posiciones_prom.iterrows():
        color = colores_posicion.get(row['position'], 'black')
        legend_elements.append(Patch(facecolor=color, edgecolor='black', label=f"{row['name']} #{row['jerseyNumber']}"))

    # Añadir la leyenda dentro del mismo gráfico
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)

def mostrar_xi_inicial(id_jornada,df_stats_AL,df_stats_oponentes,incluir_sustitutos=False,incluir_oponentes=True):
    df_filtrado_oponentes = df_stats_oponentes[df_stats_oponentes['substitute']==False]
    df_posiciones_prom_op = pd.read_excel(r'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\Aplicacion Final\2024\Posiciones promedio Oponente 2024\Posiciones_Prom_Oponentes_2024.xlsx', sheet_name=id_jornada)
    df_posiciones_prom_op = df_posiciones_prom_op[df_posiciones_prom_op['name'].isin(df_filtrado_oponentes['name'])]
    df_posiciones_prom_op.drop(['slug', 'shortName', 'userCount', 'id',  'pointsCount'], axis=1, inplace=True)
    orden_posicion = {'G': 0, 'D': 1, 'M': 2, 'F': 3}
    df_sustitutos = df_stats_AL[df_stats_AL['substitute']==True]
    df_filtrado_jugadores = df_stats_AL[df_stats_AL['substitute']==False]
    df_posiciones_prom_AL = pd.read_excel(r'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\Aplicacion Final\2024\Posiciones promedio AL 2024\Posiciones_Prom_AL_2024.xlsx', sheet_name=id_jornada)
    df_pos_sustitutos = df_posiciones_prom_AL[df_posiciones_prom_AL['name'].isin(df_sustitutos['name'])]
    df_posiciones_prom = df_posiciones_prom_AL[df_posiciones_prom_AL['name'].isin(df_filtrado_jugadores['name'])]
    df_posiciones_prom.drop(['slug', 'shortName', 'userCount', 'id', 'firstName', 'lastName', 'pointsCount'], axis=1, inplace=True)
    df_posiciones_prom['orden'] = df_posiciones_prom['position'].map(orden_posicion)
    df_posiciones_prom.sort_values(by='orden', inplace=True)
    xi_titular = df_posiciones_prom['name']
    sustitutos = df_pos_sustitutos['name']
    xi_titular_op = df_posiciones_prom_op['name']

    fig, ax = plt.subplots(figsize=(23, 11))
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    for jugador in xi_titular:
        fila_jugador = df_posiciones_prom[(df_posiciones_prom['name'] == jugador)]
        if not fila_jugador.empty:
            posicion = fila_jugador['position'].values[0]
            color = colores_posicion.get(posicion, 'black')  # Usamos 'black' como color predeterminado si la posición no está en el mapa
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
                color = colores_oponentes.get(equipo, 'black')  # Usamos 'black' como color predeterminado si la posición no está en el mapa
                pitch.scatter(100-(fila_jugador['averageX'].values[0]), 100-(fila_jugador['averageY'].values[0]), ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
                ax.text(100-(fila_jugador['averageY'].values[0]),100- (fila_jugador['averageX'].values[0]), fila_jugador['jerseyNumber'].values[0], color='black', ha='center', va='center', fontsize=10, zorder=2)
                ax.set_title(f"Posicion promedio del 11 titular de {equipo}", fontsize=14)


    legend_elements = []

    for _, row in df_posiciones_prom.iterrows():
        color = colores_posicion.get(row['position'], 'black')
        legend_elements.append(Patch(facecolor=color, edgecolor='black', label=f"{row['name']} #{row['jerseyNumber']}"))

    # Añadir la leyenda dentro del mismo gráfico
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)

## ----------------------------- ZONA TEST ---------------------------------------

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

colores_posicion = {
        'G': 'red',
        'D': 'green',
        'M': 'purple',
        'F': 'blue'
    }

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
## ----------------------------- MAIN FUNCTION ---------------------------------

def main():

    df_jornadas = pd.read_excel(r'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\Aplicacion Final\2024\Resumen_Partidos_AL_2024.xlsx')
    df_stats_AL = pd.read_excel(r'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\Aplicacion Final\2024\Estadisticas_Jugadores_AL_2024.xlsx')

    configurar_pagina()

    p_resumen , p_equipo , p_jornadas , p_jugadores = st.tabs(["Resumen 2024","Equipo","Jornadas", "Jugadores"])
    with p_resumen:
        promedio_goles_alianza = df_jornadas['Goles Alianza Lima'].mean()
        promedio_goles_oponente = df_jornadas['Goles Oponente'].mean()
        
        st.write("Promedio de Goles A favor:", promedio_goles_alianza)
        st.write("Promedio de Goles Recibidos:", promedio_goles_oponente)


    with p_jornadas:

        p_torneos , p_jornadas = st.columns(2)
        with p_torneos:
            torneos = df_jornadas['Torneo'].unique()
            torneos_seleccionados = st.multiselect("Elegir torneo: ",torneos,default=torneos)
        with p_jornadas:
            if torneos_seleccionados:
                df_jornadas = df_jornadas[df_jornadas['Torneo'].isin(torneos_seleccionados)]
            jornada_seleccionada = st.selectbox('Selecciona una jornada:', df_jornadas['nombre'], key='jornada_selector')
            jornada_filtrada = df_jornadas[df_jornadas['nombre'] == jornada_seleccionada]
        
        # id_jornada, nombre, condicion, equipo oponente, torneo, goles alianza lima, goles oponente
        # resultado, dt alianza lima, dt oponente , puntos obtenidos , puntos acumulados
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

        # Obtener stats de jugadores oponentes
        df_stats_oponentes = pd.read_csv(f'Aplicacion Final/2024/Estadisticas Oponentes 2024/{id_jornada}_stats_jugadores_op.csv')
        # Obtener stats de jugadores de Alianza
        df_stats_AL = df_stats_AL[df_stats_AL['Jornada'] == nombre_jornada]
        # Obtener stats del partido
        df_estadisticas_partidos = pd.read_excel(r'Aplicacion Final\2024\Estadisticas_Partidos_AL_2024.xlsx', sheet_name=id_jornada)

        col1 , col2 , col3 , col4, col5 = st.columns(5)
        with col1:
            imprimir_escudo_AL()
            st.markdown(f"**Resultado de {condicion}:** {resultado} | {goles_alianza_lima} - {goles_oponente}")
            st.write('DT: ', dt_alianza_lima)

            sustitutos = st.checkbox('Incluir sustitutos', value=False)
            check_oponentes = st.checkbox('Incluir oponentes', value=True)

            mostrar_xi_inicial(id_jornada, df_stats_AL, df_stats_oponentes, incluir_sustitutos=sustitutos, incluir_oponentes=check_oponentes)
            
            df_titulares = df_stats_AL[df_stats_AL['substitute']==False]
            minutos_toques = df_titulares[['shortName','position','minutesPlayed','touches']]
            mostrar_grafico_barras(minutos_toques)

            st.dataframe(df_stats_AL)
        with col2:
            imprimir_escudo_oponente(equipo_oponente,torneos_seleccionados)
            st.write('DT: ', dt_oponente)
            sustitutos_op = st.checkbox('Incluir sustitutos op.', value=False)
            check_oponentes = st.checkbox('Incluir jugadores AL', value=False)
            mostrar_xi_inicial_oponente(id_jornada,df_stats_oponentes,incluir_sustitutos=sustitutos_op)

            df_titulares_oponentes = df_stats_oponentes[df_stats_oponentes['substitute']==False]
            minutos_toques_op = df_titulares_oponentes[['shortName','position','minutesPlayed','touches']]
            mostrar_grafico_barras(minutos_toques_op)

            st.dataframe(df_stats_oponentes)
        with col3:
            df_ball_possession = df_estadisticas_partidos[df_estadisticas_partidos['Estadistica'] == 'Ball possession']
            df_pie = pd.melt(df_ball_possession, id_vars=['Estadistica'], value_vars=['Alianza', 'Oponente'],
                var_name='Equipo', value_name='Porcentaje')
            fig = px.pie(df_pie, values='Porcentaje', names='Equipo', title='Posesión de Balón',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(width=400, height=400)
            st.plotly_chart(fig, use_container_width=True)
        with col4:
            
            categoria = st.selectbox("Selecciona una categoría", ["Ataque", "Defensa", "Portero", "Juego General"])
            subcategoria = st.selectbox("Selecciona una subcategoría", ["Creación de Oportunidades", "Remates", "Desbordes y Centros"] if categoria == "Ataque" else 
                                                    ["Recuperación de Balón", "Despejes", "Duelos"] if categoria == "Defensa" else 
                                                    ["Portero"] if categoria == "Portero" else ["Juego General"])
            mostrar_grafico(df_estadisticas_partidos,categoria, subcategoria)
        with col5:
            st.subheader("Rendimiento - Alianza Lima")
            
            df_rendimiento = calcular_rendimiento(df_estadisticas_partidos)
            st.dataframe(df_rendimiento)
            mostrar_grafico_ternario(df_rendimiento, 'Alianza')
            
        
if __name__ == "__main__":
    main()