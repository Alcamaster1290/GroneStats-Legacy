import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from mplsoccer.pitch import VerticalPitch
import seaborn as sns
import os
from io import BytesIO

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

def apply_color_based_on_shot_type(shot_type):
    if shot_type == 'block':
        return 'coral'
    elif shot_type == 'miss':
        return 'darkred'
    elif shot_type == 'goal':
        return 'darkgreen'
    elif shot_type in ['save', 'post']:
        return 'darkgoldenrod'
    else:
        return 'gray'

## -------------------------------------- GRAPH FUNCTIONS ------------------------------------------------

## MOMENTUM

def ajuste_polinomial(x, y, grado=8):
    """Realiza un ajuste polinomial de los datos y retorna valores ajustados."""
    coeficientes = np.polyfit(x, y, grado)
    polinomio = np.poly1d(coeficientes)
    return polinomio(x)

def obtener_grafico_match_momentum(df, es_local = True):

    # Procesar los datos para separar los valores positivos y negativos de momentum
    momentum_positivo = df[df['value'] > 0]
    momentum_negativo = df[df['value'] < 0]
    
    # Definir colores según si Alianza Lima es local o visitante
    color_alianza = 'blue' if es_local else 'orange'
    color_oponente = 'orange' if es_local else 'blue'

    # Crear el gráfico de Plotly
    fig = go.Figure()

    # Momentum positivo (Alianza Lima si es_local, de lo contrario Oponente)
    fig.add_trace(go.Bar(
        x=momentum_positivo['minute'],
        y=momentum_positivo['value'],
        name='Alianza Lima' if es_local else 'Oponente',
        marker_color=color_alianza
    ))

    # Momentum negativo (Oponente si es_local, de lo contrario Alianza Lima)
    fig.add_trace(go.Bar(
        x=momentum_negativo['minute'],
        y=momentum_negativo['value'],
        name='Oponente' if es_local else 'Alianza Lima',
        marker_color=color_oponente
    ))

    if not momentum_positivo.empty:
        x_positivo = momentum_positivo['minute']
        y_positivo = momentum_positivo['value']
        y_tendencia_positiva = ajuste_polinomial(x_positivo, y_positivo)
        
        fig.add_trace(go.Scatter(x=x_positivo, y=y_tendencia_positiva, mode='lines', name='Tendencia Local', line=dict(color=color_alianza, width=2)))

    # Añadir línea de tendencia polinomial para el Oponente
    if not momentum_negativo.empty:
        x_negativo = momentum_negativo['minute']
        y_negativo = -momentum_negativo['value']  # Tomar valor absoluto para el ajuste
        y_tendencia_negativa = ajuste_polinomial(x_negativo, y_negativo)
        
        fig.add_trace(go.Scatter(x=x_negativo, y=-y_tendencia_negativa, mode='lines', name='Tendencia Visita', line=dict(color=color_oponente, width=2)))

    # Actualizar layout del gráfico
    fig.update_layout(
        title="Momentum de presión del partido",
        xaxis_title="Minuto",
        yaxis_title="Momentum",
        template="plotly_dark",
        barmode='relative',
        xaxis=dict(
            showgrid=False,      # Ocultar cuadrícula en el eje x
        ),
        yaxis=dict(
            showgrid=False,      # Ocultar cuadrícula en el eje y
            tickmode='array',    # Modo de marcas: array (sin marcas)
            tickvals=[]          # Valores de marcas vacío (ningún valor visible)
        )
    )
    
    # Retornar el gráfico de Plotly
    return fig

## XI INICIAL OPONENTE 
def mostrar_xi_inicial_oponente(df_titulares_oponente, df_sustitutos_oponente, df_posiciones_prom_op, df_posiciones_prom_AL, incluir_sustitutos=False, incluir_al=False, incluir_voronoi=False):
    orden_posicion = {'G': 0, 'D': 1, 'M': 2, 'F': 3}

    df_posiciones_prom = df_posiciones_prom_op[df_posiciones_prom_op['name'].isin(df_titulares_oponente['name'])]
    df_posiciones_prom.drop(['slug', 'shortName', 'userCount', 'id', 'pointsCount'], axis=1, inplace=True)
    df_posiciones_prom['orden'] = df_posiciones_prom['position'].map(orden_posicion)
    df_posiciones_prom.sort_values(by='orden', inplace=True)
    df_posiciones_prom = df_posiciones_prom.merge(df_titulares_oponente[['name', 'minutesPlayed', 'captain', 'out']], on='name', how='left')

    df_pos_sustitutos = df_posiciones_prom_op[df_posiciones_prom_op['name'].isin(df_sustitutos_oponente['name'])]
    if incluir_sustitutos:
        df_posiciones_prom = df_posiciones_prom[df_posiciones_prom['out'] != True]
        df_posiciones_prom = pd.concat([df_posiciones_prom, df_pos_sustitutos], ignore_index=True)

    xi_titular = df_posiciones_prom['name']
    sustitutos = df_pos_sustitutos['name']
    xi_titular_al = df_posiciones_prom_AL['name']

    fig, ax = plt.subplots(figsize=(23, 14))
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    for jugador in xi_titular:
        fila_jugador = df_posiciones_prom[df_posiciones_prom['name'] == jugador]
        if not fila_jugador.empty:
            equipo = fila_jugador['team'].values[0]
            color = colores_oponentes.get(equipo, 'black')  
            pitch.scatter(fila_jugador['averageX'].values[0], fila_jugador['averageY'].values[0], ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
            ax.text(fila_jugador['averageY'].values[0], fila_jugador['averageX'].values[0], int(fila_jugador['jerseyNumber'].values[0]), color='white', ha='center', va='center', fontsize=10, zorder=2)
            ax.set_title(f"Posicion promedio del 11 titular de {equipo}", fontsize=14)

    legend_elements = []

    for _, row in df_posiciones_prom.iterrows():
        color = colores_posicion.get(row['position'], 'black')
        legend_elements.append(Patch(facecolor=color, edgecolor='black', label=f"{row['name']} #{row['jerseyNumber']}"))

    if incluir_sustitutos:
        for sustituto in sustitutos:
            fila_sustituto = df_pos_sustitutos[df_pos_sustitutos['name'] == sustituto]
            if not fila_sustituto.empty:
                equipo = fila_sustituto['team'].values[0]
                color = colores_oponentes.get(equipo, 'blue')  
                pitch.scatter(fila_sustituto['averageX'].values[0], fila_sustituto['averageY'].values[0], ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
                ax.text(fila_sustituto['averageY'].values[0], fila_sustituto['averageX'].values[0], int(fila_sustituto['jerseyNumber'].values[0]), color='white', ha='center', va='center', fontsize=10, zorder=2)

    if incluir_al:
        for jugador in xi_titular_al:
            fila_jugador = df_posiciones_prom_AL[df_posiciones_prom_AL['name'] == jugador]
            if not fila_jugador.empty:
                posicion = fila_jugador['position'].values[0]
                color = colores_posicion.get(posicion, 'black')  
                pitch.scatter(100 - fila_jugador['averageX'].values[0], 100 - fila_jugador['averageY'].values[0], ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
                ax.text(100 - fila_jugador['averageY'].values[0], 100 - fila_jugador['averageX'].values[0], int(fila_jugador['jerseyNumber'].values[0]), color='black', ha='center', va='center', fontsize=10, zorder=2)

    if incluir_voronoi:
        x_all = np.concatenate([df_posiciones_prom['averageX'].values, 100 - df_posiciones_prom_AL['averageX'].values])
        y_all = np.concatenate([df_posiciones_prom['averageY'].values, 100 - df_posiciones_prom_AL['averageY'].values])
        teams_all = np.concatenate([np.ones(len(df_posiciones_prom)), np.zeros(len(df_posiciones_prom_AL))])
        voronoi_data = pitch.voronoi(x_all, y_all, teams_all)
        for team, color in zip(voronoi_data, ['blue', 'red']):
            pitch.polygon(team, ax=ax, fc=color, ec='white', linewidth=3, alpha=.15)

    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, fontsize=12)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    # Crea un botón de descarga en Streamlit
    st.download_button(
        label="Descargar figura",
        data=buf,
        file_name=f"XI Inicial Oponente.png",
        mime="image/png"
    )
    buf = None

## XI INICIAL AL
def mostrar_xi_inicial(df_titulares, df_sustitutos, df_posiciones_prom_AL, df_posiciones_prom_op, incluir_sustitutos=False, incluir_oponentes=True, incluir_voronoi=False):
    orden_posicion = {'G': 0, 'D': 1, 'M': 2, 'F': 3}
    
    df_pos_sustitutos = df_posiciones_prom_AL[df_posiciones_prom_AL['name'].isin(df_sustitutos['name'])]
    df_posiciones_prom = df_posiciones_prom_AL[df_posiciones_prom_AL['name'].isin(df_titulares['name'])]
    df_posiciones_prom.drop(['slug', 'shortName', 'userCount', 'id', 'firstName', 'lastName', 'pointsCount'], axis=1, inplace=True)
    df_posiciones_prom['orden'] = df_posiciones_prom['position'].map(orden_posicion)
    df_posiciones_prom.sort_values(by='orden', inplace=True)
    df_posiciones_prom = df_posiciones_prom.merge(df_titulares[['name', 'minutesPlayed', 'captain', 'out']], on='name', how='left')

    if incluir_sustitutos:
        # Filtrar titulares que no han sido sustituidos
        df_posiciones_prom = pd.concat([df_posiciones_prom, df_pos_sustitutos], ignore_index=True)
        df_posiciones_prom = df_posiciones_prom[df_posiciones_prom['out'] != True]
        
    xi_titular = df_posiciones_prom['name']
    sustitutos = df_pos_sustitutos['name']
    xi_titular_op = df_posiciones_prom_op['name']

    # GRAFICAR CANCHA
    fig, ax = plt.subplots(figsize=(23, 14))
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    for jugador in xi_titular:
        fila_jugador = df_posiciones_prom[df_posiciones_prom['name'] == jugador]
        if not fila_jugador.empty:
            posicion = fila_jugador['position'].values[0]
            color = colores_posicion.get(posicion, 'black') 
            pitch.scatter(fila_jugador['averageX'], fila_jugador['averageY'], ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
            ax.text(fila_jugador['averageY'].values[0], fila_jugador['averageX'].values[0], int(fila_jugador['jerseyNumber'].values[0]), color='white', ha='center', va='center', fontsize=12, zorder=2)
            ax.set_title(f"Posicion promedio del 11 titular de Alianza Lima", fontsize=14)

    legend_elements = []

    for _, row in df_posiciones_prom.iterrows():
        color = colores_posicion.get(row['position'], 'black')
        legend_elements.append(Patch(facecolor=color, edgecolor='black', label=f"{row['name']} #{row['jerseyNumber']}"))

    if incluir_sustitutos:
        for sustituto in sustitutos:
            fila_sustituto = df_pos_sustitutos[df_pos_sustitutos['name'] == sustituto]
            if not fila_sustituto.empty:
                posicion = fila_sustituto['position'].values[0]
                color = colores_posicion.get(posicion, 'blue')
                pitch.scatter(fila_sustituto['averageX'], fila_sustituto['averageY'], ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
                ax.text(fila_sustituto['averageY'].values[0], fila_sustituto['averageX'].values[0], int(fila_sustituto['jerseyNumber'].values[0]), color='white', ha='center', va='center', fontsize=12, zorder=2)

    if incluir_oponentes:
        for jugador in xi_titular_op:
            fila_jugador = df_posiciones_prom_op[df_posiciones_prom_op['name'] == jugador]
            if not fila_jugador.empty:
                posicion = fila_jugador['position'].values[0]
                equipo = fila_jugador['team'].values[0]
                color = colores_oponentes.get(equipo, 'black')  
                pitch.scatter(100 - fila_jugador['averageX'].values[0], 100 - fila_jugador['averageY'].values[0], ax=ax, s=200, color=color, edgecolors='black', linewidth=2.5, zorder=1)
                ax.text(100 - fila_jugador['averageY'].values[0], 100 - fila_jugador['averageX'].values[0], int(fila_jugador['jerseyNumber'].values[0]), color='black', ha='center', va='center', fontsize=10, zorder=2)

    if incluir_voronoi:

        x_all = np.concatenate([df_posiciones_prom['averageX'].values, 100 - df_posiciones_prom_op['averageX'].values])
        y_all = np.concatenate([df_posiciones_prom['averageY'].values, 100 - df_posiciones_prom_op['averageY'].values])
        teams_all = np.concatenate([np.ones(len(df_posiciones_prom)), np.zeros(len(df_posiciones_prom_op))])
        voronoi_data = pitch.voronoi(x_all, y_all, teams_all)
        for team, color in zip(voronoi_data, ['blue', 'red']):
            pitch.polygon(team, ax=ax, fc=color, ec='white', linewidth=3, alpha=.15)

    # Añadir la leyenda dentro del mismo gráfico
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, fontsize=12)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    # Crea un botón de descarga en Streamlit
    st.download_button(
        label="Descargar figura",
        data=buf,
        file_name=f"XI Inicial AL.png",
        mime="image/png"
    )
    buf = None

## POSESION

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

    fig = px.pie(df_pie, values='Porcentaje', names='Equipo', title='% Posesión de balón',
                 color='Equipo', color_discrete_map=colors)
    
    #fig.update_layout(width=200, height=200)
    st.plotly_chart(fig, use_container_width=True)

## SHOTS

def graficar_tiros_al_arco(df_shots_on_target):
    df_coordenadas = df_shots_on_target['goalMouthCoordinates'].reset_index(drop=True)
    dict_list = [eval(coord) for coord in df_coordenadas.tolist()]
    df_goalzone_AL = pd.DataFrame(dict_list)
    df_goalzone_AL['shotType'] = df_shots_on_target['shotType'].values
    df_goalzone_AL['situation'] = df_shots_on_target['situation'].values
    df_goalzone_AL['jerseyNumber'] = df_shots_on_target['jerseyNumber'].values
    df_goalzone_AL['bodyPart'] = df_shots_on_target['bodyPart'].values
    df_goalzone_AL['goalMouthLocation'] = df_shots_on_target['goalMouthLocation'].values
    df_goalzone_AL['time'] = df_shots_on_target['time'].values
    df_goalzone_AL['shortName'] = df_shots_on_target['shortName'].values
    df_goalzone_AL['position'] = df_shots_on_target['position'].values
    df_goalzone_AL['color'] = df_shots_on_target['color'].values
    if 'goalType' in df_shots_on_target.columns:
        df_goalzone_AL['goalType'] = df_shots_on_target['goalType'].values

    fig = px.scatter(df_goalzone_AL, x='y', y='z', title='Ubicación de tiros a puerta', labels={'y': 'y', 'z': 'z'}, color='color',
                     color_discrete_map={'darkgreen': 'darkgreen', 'darkgoldenrod': 'darkgoldenrod', 'coral': 'coral', 'darkred': 'darkred'},
                     hover_data={'shortName': True, 'jerseyNumber': True, 'shotType': True, 'time': True, 'situation': True, 'bodyPart': True, 'goalMouthLocation': True, 
                                 'y': False, 'z': False, 'color': False})

    fig.update_xaxes(autorange="reversed")

    fig.add_shape(type="line", x0=45.4, y0=0, x1=45.4, y1=35.5, line=dict(color="Black", width=5))
    fig.add_shape(type="line", x0=54.5, y0=0, x1=54.5, y1=35.5, line=dict(color="Black", width=5))
    fig.add_shape(type="line", x0=45.4, y0=35.5, x1=54.5, y1=35.5, line=dict(color="Black", width=5))

    fig.update_xaxes(showgrid=False, visible=False)
    fig.update_yaxes(showgrid=False, visible=False)

    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def graficar_posicion_tiros_a_puerta(df_shots_on_target,team):
    pitch = VerticalPitch(
        pitch_type='opta',
        pitch_color='grass',
        half=True,
        goal_type='box',
        linewidth=1.25,
        line_color='black',
        pitch_length=105,
        pitch_width=68
    )

    fig, axs = pitch.grid(figheight=10, title_height=0, endnote_space=0, title_space=0, axis=False, grid_height=0.82, endnote_height=0.03)

    hexmap = pitch.hexbin(x=100-df_shots_on_target['x'], y=100-df_shots_on_target['y'], ax=axs['pitch'], edgecolors='#f4f4f4',
                          gridsize=(6, 6), cmap='PuBu', alpha=.5)
    scatter = pitch.scatter(x=100-df_shots_on_target['x'], y=100-df_shots_on_target['y'], ax=axs['pitch'], 
                            color=df_shots_on_target['color'], s=200, edgecolors='black', zorder=2, alpha=.9)

    for i, row in df_shots_on_target.iterrows():
        axs['pitch'].annotate(row['jerseyNumber'], (100-row['y'], 100-row['x']), color='white', ha='center', va='center',
                              fontsize=10, weight='bold', zorder=3)
    fig.suptitle(f'Posición de tiros a puerta', fontsize=22)

    legend_elements = []
    for _, row in df_shots_on_target.iterrows():
        color = row['color']
        legend_elements.append(Patch(facecolor=color, edgecolor='black', label=f"{row['time']}' {row['bodyPart']} {row['shotType']} #{row['jerseyNumber']} {row['shortName']} - {row['situation']}"))

    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, fontsize=12)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    # Crea un botón de descarga en Streamlit
    st.download_button(
        label=f"Descarga el mapa de tiros a puerta {team} (dona en el QR porfa)",
        data=buf,
        file_name=f"Tiros a puerta.png",
        mime="image/png",
    )

def graficar_tiros_fuera(df_shots_off_target,team):
    pitch = VerticalPitch(
        pitch_type='opta',
        pitch_color='grass',
        half=False,
        goal_type='box',
        linewidth=1.25,
        line_color='black',
        pitch_length=105,
        pitch_width=68
    )

    fig, axs = pitch.grid(figheight=10, title_height=0, endnote_space=0, title_space=0, axis=False, grid_height=0.82, endnote_height=0.03)
    plt.suptitle('Posición de tiros fuera', fontsize=16)

    hexmap = pitch.hexbin(x=100-df_shots_off_target['x'], y=100-df_shots_off_target['y'], ax=axs['pitch'], edgecolors='#f4f4f4',
                          gridsize=(6, 6), cmap='PuBu', alpha=.5)
    scatter = pitch.scatter(x=100-df_shots_off_target['x'], y=100-df_shots_off_target['y'], ax=axs['pitch'], color=df_shots_off_target['color'], s=200, edgecolors='black', zorder=2, alpha=.9)

    for i, row in df_shots_off_target.iterrows():
        axs['pitch'].annotate(row['jerseyNumber'], (100-row['y'], 100-row['x']), color='white', ha='center', va='center',
                              fontsize=10, weight='bold', zorder=3, label=df_shots_off_target['shortName'])

    legend_elements = []
    for _, row in df_shots_off_target.iterrows():
        color = row['color']
        legend_elements.append(Patch(facecolor=color, edgecolor='black', label=f"{row['time']}' #{row['jerseyNumber']} {row['shortName']} - {row['situation']} {row['bodyPart']} | {row['goalMouthLocation']}"))

    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, fontsize=12)    
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    # Crea un botón de descarga en Streamlit
    st.download_button(
        label=f"Descarga el mapa de tiros fuera {team} (dona en el QR porfa)",
        data=buf,
        file_name=f"Tiros fuera.png",
        mime="image/png"
    )


## ------------------------------------------------------DATA PROCCESING-------------------------------------

def procesar_tarjetas_rojas(df_stats_match, df_stats_AL, df_stats_oponente,col3):

    try:
        red_cards_AL, red_cards_Op = df_stats_match['Red cards'].values[:2]
        expulsados = True
    except KeyError:
        red_cards_AL = red_cards_Op = 0
        expulsados = False

    df_cambios_AL = df_stats_AL[(df_stats_AL['minutesPlayed'] != 0) & (df_stats_AL['minutesPlayed'] != 90)].copy()
    df_cambios_Op = df_stats_oponente[(df_stats_oponente['minutesPlayed'] != 0) & (df_stats_oponente['minutesPlayed'] != 90)].copy()

    if expulsados:
        with col3:
            st.subheader("Expulsados")
        df_cambios_AL_exp = df_cambios_AL.copy()
        df_cambios_Op_exp = df_cambios_Op.copy()
        df_cambios_AL_exp.sort_values(by='rating', inplace=True)
        df_cambios_Op_exp.sort_values(by='rating', inplace=True)
        df_expulsados_AL = df_cambios_AL_exp[(df_cambios_AL_exp['rating'] > 0)].head(int(red_cards_AL))
        df_expulsados_Op = df_cambios_Op_exp[(df_cambios_Op_exp['rating'] > 0)].head(int(red_cards_Op))
        nombres_expulsados_AL = df_expulsados_AL['name'].tolist()
        nombres_expulsados_op = df_expulsados_Op['name'].tolist()
        minutos_exp_al = df_expulsados_AL['minutesPlayed'].tolist()
        minutos_exp_op = df_expulsados_Op['minutesPlayed'].tolist()
        df_cambios_AL_exp.reset_index(drop=True, inplace=True)
        df_cambios_Op_exp.reset_index(drop=True, inplace=True)
    else:
        minutos_exp_al = []
        minutos_exp_op = []
        nombres_expulsados_AL = []
        nombres_expulsados_op = []

    df_sustitutos_AL = df_cambios_AL[df_cambios_AL['substitute'] == True].copy()
    df_substituidos_AL = df_cambios_AL[df_cambios_AL['substitute'] == False].copy()
    df_sustitutos_op = df_cambios_Op[df_cambios_Op['substitute'] == True].copy()
    df_substituidos_op = df_cambios_Op[df_cambios_Op['substitute'] == False].copy()

    for nombre , minuto in zip(nombres_expulsados_AL, minutos_exp_al):
        with col3:
            st.write(f'Expulsado en Alianza Lima: {nombre} tras {int(minuto)} minutos de juego')
    for nombre_op , minuto_op in zip(nombres_expulsados_op, minutos_exp_op):
        with col3:
            st.write(f'Expulsado rival: {nombre_op} tras {int(minuto_op)} minutos de juego')

    if expulsados:
        df_substituidos_AL = df_substituidos_AL[~df_substituidos_AL['name'].isin(nombres_expulsados_AL)]
        df_substituidos_op = df_substituidos_op[~df_substituidos_op['name'].isin(nombres_expulsados_op)]

    return df_substituidos_AL, df_sustitutos_AL, df_substituidos_op, df_sustitutos_op

def procesar_tiros(df_shotmaps, condicion):
    df_shotmaps['color'] = df_shotmaps['shotType'].apply(apply_color_based_on_shot_type)
    shots_on_target = ['save', 'goal']
    shots_off_target = ['miss', 'post', 'block']
    df_shots_on_target = df_shotmaps[df_shotmaps['shotType'].isin(shots_on_target)]
    df_shots_off_target = df_shotmaps[df_shotmaps['shotType'].isin(shots_off_target)]
    if condicion == 'Local':
        df_shots_on_target_AL = df_shots_on_target[df_shots_on_target['isHome']]
        df_shots_on_target_Oponente = df_shots_on_target[~df_shots_on_target['isHome']]
        df_shots_off_target_AL = df_shots_off_target[df_shots_off_target['isHome']]
        df_shots_off_target_Oponente = df_shots_off_target[~df_shots_off_target['isHome']]
    else:
        df_shots_on_target_AL = df_shots_on_target[~df_shots_on_target['isHome']]
        df_shots_on_target_Oponente = df_shots_on_target[df_shots_on_target['isHome']]
        df_shots_off_target_AL = df_shots_off_target[~df_shots_off_target['isHome']]
        df_shots_off_target_Oponente = df_shots_off_target[df_shots_off_target['isHome']]
    
    return df_shots_on_target_AL, df_shots_on_target_Oponente, df_shots_off_target_AL, df_shots_off_target_Oponente

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
    df = df[df['minutesPlayed'] > 5]
    orden_posicion = {'G': 0, 'D': 1, 'M': 2, 'F': 3}
    df['orden'] = df['position'].map(orden_posicion)
    df.sort_values(by='orden', inplace=True)
    colores_posicion = {'G': 'cyan', 'D': 'blue', 'M': 'green', 'F': 'red'}
    df['color'] = df['position'].map(colores_posicion)

    fig = px.bar(df, y='minutesPlayed', x='shortName', orientation='v',
                 title='Minutos Jugados por Jugador', labels={'minutesPlayed': 'Minutos Jugados', 'shortName': 'Jugador', 'possessionLostCtrl':'Posesion perdida'},
                 color='position', color_discrete_map=colores_posicion, text='minutesPlayed',
                 hover_data={'color': False, 'position': False, 'possessionLostCtrl':True})
    fig.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig.update_layout(showlegend=False, xaxis_title='Minutos Jugados', yaxis_title='Jugador')  # Ocultar leyenda
    
    fig2 = px.bar(df, y='touches', x='shortName', orientation='v',
                  title='Toques por Jugador', labels={'touches': 'Toques', 'shortName': 'Jugador', 'possessionLostCtrl':'Posesion perdida'},
                  color='position', color_discrete_map=colores_posicion, text='touches',
                  hover_data={'color': False, 'position': False, 'possessionLostCtrl':True})
    fig2.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig2.update_layout(showlegend=False, xaxis_title='Toques', yaxis_title='Jugador')  # Ocultar leyenda
    
    df = df[df['possessionLostCtrl']>0]
    df['touchesxlostposs'] = df['touches'] / df['possessionLostCtrl']
    df['touchesxlostposs'] = df['touchesxlostposs'].astype(float)
    # Gráfico de barras para 'touchesxlostposs'
    fig3 = px.bar(df, y='touchesxlostposs', x='shortName', orientation='v',
                  title='Toques hasta Pérdida de balón', 
                  labels={'touchesxlostposs': 'Toques hasta pérdida', 'shortName': 'Jugador'},
                  color='position', color_discrete_map=colores_posicion,
                  hover_data={'color': False, 'position': False, 'touches': True, 'possessionLostCtrl': True}, text='touchesxlostposs')

    fig3.update_traces(texttemplate='%{text:.2f}', textposition='inside')  
    fig3.update_layout(showlegend=False, xaxis_title='Toques / Pérdidas de Posesión', yaxis_title='Jugador')  # Ocultar leyenda

    fig.update_xaxes(tickangle=45, tickfont=dict(size=10))
    st.plotly_chart(fig, use_container_width=True)

    fig2.update_xaxes(tickangle=45, tickfont=dict(size=10))
    st.plotly_chart(fig2, use_container_width=True)

    fig3.update_xaxes(tickangle=45, tickfont=dict(size=10))
    st.plotly_chart(fig3, use_container_width=True)
    

## ------------------------------------------------ MAIN FUNCTION ---------------------------------

def main():
    # --------------------------------------------- CARGA RESUMEN Y STATS TOTALES AL -------------------------------------
    df_jornadas = pd.read_excel(r'Aplicacion Final\2024\Resumen_Partidos_AL_2024.xlsx')
    df_stats_AL = pd.read_excel(r'Aplicacion Final\2024\Estadisticas_Jugadores_AL_2024.xlsx')

    configurar_pagina()
    # --------------------------------------------- BARRA LATERAL SELECCIONAR TORNEOS ----------------------------------------------------
    with st.sidebar:
        torneos = df_jornadas['Torneo'].unique()
        torneos_seleccionados = st.multiselect("Filtra por torneo: ",torneos,default=torneos)
        df_torneos_filtrados = df_jornadas[df_jornadas['Torneo'].isin(torneos_seleccionados)]

    ## ----------------------------------------- GENERAL TABS --------------------------------------------------------
    
    p_resumen , p_equipo , p_jornadas , p_jugadores = st.tabs(["Resumen 2024","Equipo","Jornadas", "Jugadores"])
    
    # -------------------------- CARGA DE DATOS TOTALES X TORNEO ----------------------------------
    t = df_torneos_filtrados['Torneo'].map(torneos_d).values[0]
    st.session_state.torneo = t
    df_stats_totales_torneo = pd.read_excel(f'Aplicacion Final/2024/Datos totales/Datos_totales_{t}_2024.xlsx',sheet_name='total')
    df_stats_x90_torneo = pd.read_excel(f'Aplicacion Final/2024/Datos totales/Datos_totales_{t}_2024.xlsx',sheet_name='per90')
    # Obtener datos totales de Alianza para el torneo
    df_stats_AL_torneo_total = pd.read_excel(f'Aplicacion Final/2024/Datos totales/Datos_totales_Alianza_Lima_{t}_2024.xlsx',sheet_name='total')
    df_stats_AL_torneo_x90 = pd.read_excel(f'Aplicacion Final/2024/Datos totales/Datos_totales_Alianza_Lima_{t}_2024.xlsx',sheet_name='per90')
    
    ## PESTAÑA RESUMEN
    with p_resumen:
        promedio_goles_alianza = df_torneos_filtrados['Goles Alianza Lima'].mean()
        promedio_goles_oponente = df_torneos_filtrados['Goles Oponente'].mean()
        
        st.write("Promedio de Goles A favor:", promedio_goles_alianza)
        st.write("Promedio de Goles Recibidos:", promedio_goles_oponente)
        st.dataframe(df_stats_AL_torneo_total)
        st.dataframe(df_stats_AL_torneo_x90)
        st.dataframe(df_stats_totales_torneo)
        st.dataframe(df_stats_x90_torneo)


    ## PESTAÑA JORNADAS
    with p_jornadas:
        ## COLUMNA FILTROS LOCALIA(Local/Visita) Y GOLES DE ALIANZA LIMA
        s_goles_al , s_goles_op = st.columns(2)
        with s_goles_al:
            opciones = df_torneos_filtrados['Condicion'].unique()
            localia_seleccionada = st.multiselect("Filtra por localia:", opciones,default=opciones,help="Selecciona al menos una opcion")
            if not localia_seleccionada:
                st.warning("Debe seleccionar al menos una opción. Se han seleccionado valores predeterminados.")
                localia_seleccionada = opciones
            df_torneos_filtrados = df_torneos_filtrados[df_torneos_filtrados['Condicion'].isin(localia_seleccionada)]
            min_goles_alianza, max_goles_alianza = st.slider('Goles Alianza Lima', 
                                                    min_value=int(df_torneos_filtrados['Goles Alianza Lima'].min()), 
                                                    max_value=int(df_torneos_filtrados['Goles Alianza Lima'].max()), 
                                                    value=(int(df_torneos_filtrados['Goles Alianza Lima'].min()), int(df_torneos_filtrados['Goles Alianza Lima'].max())))
        ## COLUMNA FILTROS RESULTADO (W/D/L) Y GOLES OPONENTE
        with s_goles_op:
            resultados = df_torneos_filtrados['Resultado'].unique()
            resultados_seleccionados = st.multiselect("Filtra por resultado:",resultados,default=resultados,help="Selecciona al menos una opcion")
            if not resultados_seleccionados:
                st.warning("Debe seleccionar al menos una opción. Se han seleccionado valores predeterminados.")
                resultados_seleccionados = opciones
            df_torneos_filtrados = df_torneos_filtrados[df_torneos_filtrados['Resultado'].isin(resultados_seleccionados)]
            min_goles_oponente, max_goles_oponente = st.slider('Goles Oponente', 
                                                    min_value=int(df_torneos_filtrados['Goles Oponente'].min()), 
                                                    max_value=int(df_torneos_filtrados['Goles Oponente'].max()), 
                                                    value=(int(df_torneos_filtrados['Goles Oponente'].min()), int(df_torneos_filtrados['Goles Oponente'].max())))
            
        df_jornadas_filtradas = df_torneos_filtrados[(df_torneos_filtrados['Goles Alianza Lima'] >= min_goles_alianza) & 
                                    (df_torneos_filtrados['Goles Alianza Lima'] <= max_goles_alianza) & 
                                    (df_torneos_filtrados['Goles Oponente'] >= min_goles_oponente) & 
                                    (df_torneos_filtrados['Goles Oponente'] <= max_goles_oponente)]

        with st.container():
            jornada_seleccionada = st.selectbox('Selecciona una jornada:', df_jornadas_filtradas['nombre'], key='jornada_selector')
        ## SELECTOR DE JORNADA
        jornada_filtrada = df_jornadas_filtradas[df_jornadas_filtradas['nombre'] == jornada_seleccionada]
    
        ## DATOS DE RESUMEN.XLSX -> DF_JORNADAS
        # id_jornada, nombre, condicion, equipo oponente, torneo, goles alianza lima, goles oponente
        # resultado, dt alianza lima, dt oponente , puntos obtenidos , puntos acumulados
        # Posicion resultante, Importancia,	Puntos1,	Puntos2,	PuntosDif1,	PuntosDif2,	Puntos jugados
        id_jornada = jornada_filtrada['id_jornada'].values[0]
        ##-------------------------------------------------------------------------------------------##
        nombre_jornada = jornada_filtrada['nombre'].values[0]
        equipo_oponente = jornada_filtrada['Equipo Oponente'].values[0]
        condicion = jornada_filtrada['Condicion'].values[0]
        if condicion == 'Local':
            es_local = True
        else:
            es_local = False
        goles_alianza_lima = jornada_filtrada['Goles Alianza Lima'].values[0]
        goles_oponente = jornada_filtrada['Goles Oponente'].values[0]
        torneo = jornada_filtrada['Torneo'].values[0]
        resultado = jornada_filtrada['Resultado'].values[0]
        dt_alianza_lima = jornada_filtrada['DT Alianza Lima'].values[0]
        dt_oponente = jornada_filtrada['DT Oponente'].values[0]
        puntos_obtenidos = jornada_filtrada['Puntos obtenidos'].values[0]
        puntos_acumulados = jornada_filtrada['Puntos acumulados'].values[0]
        pos_resultante = jornada_filtrada['Posicion resultante'].values[0]
        importancia = jornada_filtrada['Importancia'].values[0]
        puntos_jugados = jornada_filtrada['Puntos jugados'].values[0]
        # -------------------------------------- CARGA DE DATOS X JORNADA ------------------------------------------
        ## DATOS DE ESTADISTICAS_JUGADORES_AL.XLSX -> DF_JORNADAS
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
        # Obtener momentum de la jornada
        df_momentum = pd.read_excel(r'Aplicacion Final\2024\Datos totales\Momentum_2024.xlsx', sheet_name=id_jornada)

        # -------------------------------------------------- HEAD ----------------------------------------------------------
        st.title(f"**Resultado de {condicion}:** {resultado} | {goles_alianza_lima} - {goles_oponente}")
        # XI INICIAL Y SUSTITUTOS AL
        df_titulares = df_stats_AL[df_stats_AL['substitute']==False]
        # AGREGAR COLUMNA 'out' que indica si fue sustituido es decir jugo menos de 90 minutos
        df_titulares['out'] = (df_titulares['minutesPlayed'] < 90) & (df_titulares['substitute'] == False) 
        df_sustitutos = df_stats_AL[df_stats_AL['substitute']==True]
        # XI INICIAL Y SUSTITUTOS Oponente
        df_titulares_oponente = df_stats_oponente[df_stats_oponente['substitute']==False]
        # AGREGAR COLUMNA 'out' que indica si fue sustituido es decir jugo menos de 90 minutos
        df_titulares_oponente['out'] = (df_titulares_oponente['minutesPlayed'] < 90) & (df_titulares_oponente['substitute'] == False) 
        df_sustitutos_oponente = df_stats_oponente[df_stats_oponente['substitute']==True]

        # POSICIONES PROMEDIO DE AMBOS EQUIPOS
        df_posprom_titulares_AL = df_posiciones_prom_AL[df_posiciones_prom_AL['name'].isin(df_titulares['name'])]
        df_posprom_titulares_OP = df_posiciones_prom_op[df_posiciones_prom_op['name'].isin(df_titulares_oponente['name'])]


        # PROCESAR TIROS SHOTMAPS
        df_shots_on_target_AL, df_shots_on_target_Oponente, df_shots_off_target_AL, df_shots_off_target_Oponente = procesar_tiros(df_shotmaps, condicion)

        df_stats_match = df_estadisticas_partido.set_index(df_estadisticas_partido.columns[0]).T
        yellow_cards_AL, yellow_cards_Op = df_stats_match['Yellow cards'].values[:2]

        col1 , col2 ,col3  = st.columns([3,3,2])
        with col1:
            imprimir_escudo_AL() 
            st.write('DT: ', dt_alianza_lima)
            # CHECKBOXES
            check_oponentes = st.checkbox(f'Incluir jugadores {equipo_oponente}', value=True)
            check_voronoi = st.checkbox('Incluir diagramas de influencia', value = False)
            sustitutos = st.checkbox('Incluir sustitutos', value=False)
            mostrar_xi_inicial(df_titulares,df_sustitutos ,df_posiciones_prom_AL , df_posprom_titulares_OP, incluir_sustitutos=sustitutos, incluir_oponentes=check_oponentes,incluir_voronoi=check_voronoi)            
        with col2:
            imprimir_escudo_oponente(equipo_oponente,torneos_seleccionados)
            st.write('DT: ', dt_oponente)
            # CHECKBOXES
            check_al = st.checkbox('Incluir jugadores AL', value=False)
            check_voronoi_op = st.checkbox('Incluir diagramas de influencia ', value = False)
            sustitutos_op = st.checkbox(f'Incluir sustitutos {equipo_oponente}', value=False)
            mostrar_xi_inicial_oponente(df_titulares_oponente,df_sustitutos_oponente,df_posiciones_prom_op, df_posprom_titulares_AL, incluir_sustitutos=sustitutos_op, incluir_al=check_al, incluir_voronoi=check_voronoi_op)
            # GRAFICOS DE TARJETAS Y SUSTITUTOS
            df_substituidos_AL, df_sustitutos_AL, df_substituidos_op, df_sustitutos_op = procesar_tarjetas_rojas(df_stats_match,df_stats_AL,df_stats_oponente,col3)            
            with col1:          
                st.write(f'Tarjetas amarillas: {int(yellow_cards_AL)}')
                st.write(f'Alianza Lima hizo {len(df_sustitutos_AL)} cambios')
                st.subheader("Jugadores Sustituidos")
                st.dataframe(df_substituidos_AL)
                st.subheader("Jugadores Sustitutos")
                st.dataframe(df_sustitutos_AL)
                # GRAFICOS DE MINUTOS, TOQUES Y POSESION PERDIDA
                grafico_mtp = df_stats_AL[['shortName','position','minutesPlayed','touches','possessionLostCtrl']]
                mostrar_grafico_barras(grafico_mtp)
            with col2:
                st.write(f'Tarjetas amarillas: {int(yellow_cards_Op)}')
                st.write(f'{equipo_oponente} hizo {len(df_sustitutos_op)} cambios')
                st.subheader(f"Jugadores Sustituidos")
                st.dataframe(df_substituidos_op)
                st.subheader(f"Jugadores Sustitutos")
                st.dataframe(df_sustitutos_op)
                # GRAFICOS DE MINUTOS, TOQUES Y POSESION PERDIDA
                grafico_mtp_op = df_stats_oponente[['shortName','position','minutesPlayed','touches','possessionLostCtrl']]
                mostrar_grafico_barras(grafico_mtp_op)

        with col3:
            st.subheader("Estadisticas del encuentro")
            # MATCH MOMENTUM
            momentum = obtener_grafico_match_momentum(df_momentum,es_local)
            st.plotly_chart(momentum, use_container_width=True)

            # GRAFICO DE POSESION DEL BALON
            mostrar_grafico_posesion(df_estadisticas_partido, condicion)
            
            # SELECTBOX CATEGORIAS DE JUEGO
            categoria = st.selectbox("Selecciona una categoría", ["Ataque", "Defensa", "Portero", "Creacion de Chances","Juego General", "Balon parado"])
            subcategoria = st.selectbox("Selecciona una subcategoría", ["Remates", "Desbordes y Centros"] if categoria == "Ataque" else 
                                                    ["Creación de Oportunidades"] if categoria == "Creacion de Chances" else
                                                    ["Faltas","Tiros de esquina","Tiros Libres","Otros"]
                                                    ["Recuperación de Balón", "Despejes", "Duelos"] if categoria == "Defensa" else 
                                                    ["Portero"] if categoria == "Portero" else ["Juego General"])
            mostrar_grafico(df_estadisticas_partido,categoria, subcategoria)

            df_stats_AL['team'] = 'Alianza Lima'
            df_stats_oponente['team'] = equipo_oponente
            df_combined = pd.concat([df_stats_AL, df_stats_oponente])
            df_combined = df_combined[df_combined['minutesPlayed']>3]
            df_combined = df_combined.sort_values(by='position').reset_index(drop=True)
            df_combined['accPasses'] = (df_combined['accuratePass'] / df_combined['totalPass']) * 100
            fig = px.scatter(df_combined, x='accPasses', y='team', color='team',
                 color_discrete_sequence=px.colors.qualitative.Set2,
                 title='Porcentaje de Pases Precisos por Equipo',
                 labels={'accPasses': 'Porcentaje de Pases Precisos', 'team': 'Equipos'},
                 range_x=[30, 100], orientation='h')

            fig.update_layout(showlegend=False, height = 300)
            fig.update_yaxes(categoryorder='total ascending', tickmode='linear')

            st.plotly_chart(fig, use_container_width=True)

            
            #df_rendimiento = calcular_rendimiento(df_estadisticas_partido)
            #mostrar_grafico_ternario(df_rendimiento, 'Alianza')
            st.dataframe(df_combined)


        st.divider()
        ## SOLO TIROS Y CREACION DE OPORTUNIDADES
        col1 , col2 ,col3  = st.columns([3,3,2])
        with col1:
            st.subheader(f"Tiros a puerta - Alianza Lima")
            graficar_tiros_al_arco(df_shots_on_target_AL)
            graficar_posicion_tiros_a_puerta(df_shots_on_target_AL, 'Alianza Lima')
            st.subheader(f"Tiros fuera - Alianza Lima")
            graficar_tiros_fuera(df_shots_off_target_AL, 'Alianza Lima')
        with col2:
            st.subheader(f"Tiros a puerta - {equipo_oponente}")
            graficar_tiros_al_arco(df_shots_on_target_Oponente)
            graficar_posicion_tiros_a_puerta(df_shots_on_target_Oponente, equipo_oponente)
            st.subheader(f"Tiros fuera - {equipo_oponente}")
            graficar_tiros_fuera(df_shots_off_target_Oponente, equipo_oponente)
            
                    
        
if __name__ == "__main__":
    main()