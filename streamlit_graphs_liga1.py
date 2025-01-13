import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
from streamlit_cache_funcs_liga1 import get_team_id
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.legend import Legend
from mplsoccer.pitch import VerticalPitch , Pitch
from scipy.interpolate import CubicSpline

def crear_grafico_score(selected_score, opponent_score, team_name, opponent, pain_points):
    """
    Crea un gráfico indicador utilizando Plotly y muestra los pain points en un indicador central tipo gauge.
    """
    selected_id = get_team_id(team_name)
    opponent_id = get_team_id(opponent)

    # Mapeo de color según el valor de 'pain_points'
    color_map = {
        0: "green",
        1: "darkgreen",
        2: "yellowgreen",
        3: "orange",
        4: "orangered",
        5: "darkred"
    }
    
    indicator_map = {
        0: "Localía de contendiente por el título",
        1: "Equipo de altura de local",
        2: "Ambos equipos de altura",
        3: "Local juega en llano",
        4: "Partido clave para el local",
        5: "Duelo decisivo entre candidatos al título"
    }

    # Obtener el color correspondiente al valor de pain_points
    color = color_map.get(pain_points, "gray")
    text = indicator_map.get(pain_points)

    # Crear el gráfico indicador
    fig = go.Figure()

    # Centrar la imagen en la columna usando Streamlit
    c1, c2, c3, c4, c5, c6 ,c7,= st.columns(7, gap='medium', vertical_alignment='center')
    with c3:
        with st.container():
            st.image(f"GRONESTATS 1.0/Liga 1 Peru/images/teams/{selected_id}.png", width=100, use_container_width=True)
    with c4:
        with st.container():
            st.image(f"GRONESTATS 1.0/vs.png", width=100, use_container_width=True)
    with c5:
        with st.container():
            st.image(f"GRONESTATS 1.0/Liga 1 Peru/images/teams/{opponent_id}.png", width=100, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    # Goles equipo seleccionado
    with col1:
        fig.add_trace(go.Indicator(
            mode="number",
            value=selected_score,
            title={"text": f"{team_name}"},
            domain={'x': [0, 0.33], 'y': [0, 1]}  # Ajustar la columna a la izquierda
        ))
    # Goles equipo oponente
    with col3:
        fig.add_trace(go.Indicator(
            mode="number",
            value=opponent_score,
            title={"text": f"{opponent}"},
            domain={'x': [0.67, 1], 'y': [0, 1]}  # Ajustar la columna a la derecha
        ))



    # Indicador de Pain Points en el centro con gauge (col2) y color dinámico
    with col2:
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=pain_points,
            title={"text": text, "font": {"size": 16}},
            domain={'x': [0.34, 0.66], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 5]},  # Definir el rango de la escala de 0 a 5
                'bar': {'color': 'darkblue'},  # Color del indicador
                'steps': [
                    {'range': [0, 1], 'color': 'green'},
                    {'range': [1, 2], 'color': 'darkgreen'},
                    {'range': [2, 3], 'color': 'goldenrod'},
                    {'range': [3, 4], 'color': 'orangered'},
                    {'range': [4, 5], 'color': 'darkred'}
                ],
                'threshold': {
                    'line': {'color': 'black', 'width': 4},
                    'thickness': 0.75,
                    'value': pain_points
                }
            },
            number={'font': {'size': 30, 'color': color}}  # Cambiar el color del texto
        ))

    fig.update_layout(
        width=1000,  # Ancho en píxeles
        height=300  # Alto en píxeles (mayor para el gauge)
    )
    
    return fig



def generar_grafico_lineas(matches_for_team_tournament, selected_team, selected_tournament, selected_year, match_details):
    """Genera un gráfico combinado de Pain Points y Resultados con ejes opuestos."""
    selected_id = match_details['selected_id']

    # Crear columna 'result_numeric' adaptada al equipo seleccionado
    def map_result(row):
        if row['home_id'] == selected_id:
            if row['result'] == 'home':
                return 1  # Victoria local
            elif row['result'] == 'draw':
                return 0  # Empate
            else:
                return -1  # Derrota local
        elif row['away_id'] == selected_id:
            if row['result'] == 'away':
                return 1  # Victoria visitante
            elif row['result'] == 'draw':
                return 0  # Empate
            else:
                return -1  # Derrota visitante
        return None

    matches_for_team_tournament['result_numeric'] = matches_for_team_tournament.apply(map_result, axis=1)
    matches_for_team_tournament = matches_for_team_tournament.sort_values(by=['round_number'], ascending=True)

    # Crear figura combinada
    fig = go.Figure()

    # Añadir Pain Points (eje izquierdo)
    fig.add_trace(go.Scatter(
        x=matches_for_team_tournament['round_number'],
        y=matches_for_team_tournament['pain_points'],
        mode='lines+markers',
        marker=dict(color='blue', size=8),
        line=dict(color='blue', width=2),
        name='Presión del local',
        yaxis='y1'
    ))

    # Añadir Resultados (eje derecho)
    colors = matches_for_team_tournament['result_numeric'].map({1: 'green', 0: 'gray', -1: 'red'})
    fig.add_trace(go.Scatter(
        x=matches_for_team_tournament['round_number'],
        y=matches_for_team_tournament['result_numeric'],
        mode='lines+markers',
        marker=dict(color=colors, size=8),
        line=dict(color='orange', width=2),
        name='Resultado',
        yaxis='y2',
        fill='tonexty',  # Llenar el área entre los traces
        fillcolor='rgba(255, 165, 0, 0.3)'  # Color naranja semitransparente para el área
    ))

    # Configuración del diseño
    fig.update_layout(
        title=f"Presión del local vs Resultados de {selected_team} en {selected_tournament} {selected_year}",
        xaxis_title="Número de Ronda",
        yaxis=dict(
            title="Presión de localía",
            titlefont=dict(color="blue"),
            tickfont=dict(color="blue"),
        ),
        xaxis=dict(
            tickmode='array',  # Asegura que los valores del eje X se muestren explícitamente
            tickvals=matches_for_team_tournament['round_number'].unique(),  # Usamos las rondas disponibles
        ),
        yaxis2=dict(
            title="Resultado",
            titlefont=dict(color="orange"),
            tickfont=dict(color="orange"),
            overlaying='y',
            side='right',
            tickvals=[-1, 0, 1],
            ticktext=['Derrota', 'Empate', 'Victoria']
        ),
        template="plotly_dark",
        plot_bgcolor="rgb(50, 50, 50)",
        font=dict(color="white"),
        hovermode="closest",
        legend=dict(
            x=0.5,  # Centrar horizontalmente
            y=1.02,  # Posición vertical encima del gráfico
            xanchor="center",  # Ancla horizontal al centro
            yanchor="bottom",  # Ancla vertical en la parte inferior
            bgcolor="rgba(50, 50, 50, 0.5)",  # Fondo translúcido para la leyenda
            font=dict(color="white")  # Color de texto
        )
    )

    return fig


def imprimir_tarjetas(match_details, selected_team):
    """
    Función para imprimir las tarjetas de Streamlit en dos columnas.

    Parámetros:
    - match_details (dict): Diccionario con los detalles del partido seleccionado.
    - selected_team (str): Nombre del equipo seleccionado.
    """
    # Crear dos columnas
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            f"""
            <div style="
                display: flex; 
                align-items: left; 
                justify-content: center; 
                border: 1px solid #444; 
                border-radius: 8px; 
                padding: 10px 20px; 
                background-color: transparent; 
                color: #eee; 
                margin-top: 20px; 
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.6);"
            >
                <h2 style="font-size: 18px; margin: 0; color: #bbb;">{selected_team} en condición de {match_details['condicion_selected']}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                display: flex; 
                align-items: center; 
                justify-content: center; 
                border: 1px solid #444; 
                border-radius: 8px; 
                padding: 10px 20px; 
                background-color: transparent; 
                color: {match_details['color_texto']}; 
                margin-top: 20px; 
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.6);"
            >
                <h2 style="font-size: 18px; margin: 0; color: {match_details['color_texto']};">Resultado: </h2>
                <p style="font-size: 18px; font-weight: bold; margin: 0; color: {match_details['color_texto']};">{match_details['resultado_selected']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

def get_follow_up_graph(matches_for_team_tournament):
    """
    Genera un gráfico de seguimiento de puntos de presión ajustados y puntos tradicionales por ronda.

    Args:
        matches_for_team_tournament (pd.DataFrame): DataFrame con las columnas 'result_numeric' y 'pain_points'.

    Returns:
        go.Figure: Gráfico de seguimiento.
    """
    # Calcular los pain points ajustados fila por fila
    matches_for_team_tournament['pain_points_ajustados'] = matches_for_team_tournament.apply(
        lambda row: row['pain_points']*2 if row['result_numeric'] == 1 else
                    -row['pain_points'] if row['result_numeric'] == 0 else
                     -row['pain_points']*2,
        axis=1
    )

    # Calcular los puntos tradicionales basados en el resultado
    matches_for_team_tournament['result_selected'] = matches_for_team_tournament['result_numeric'].map({
        1: 3,  # Victoria
        0: 1,  # Empate
        -1: 0  # Derrota
    })

    # Crear el gráfico de líneas para el desglose por ronda
    seguimiento_grafico = go.Figure()

    # Línea para pain_points_ajustados
    seguimiento_grafico.add_trace(go.Scatter(
        x=matches_for_team_tournament['round_number'],
        y=matches_for_team_tournament['pain_points_ajustados'],
        mode='lines+markers',
        name='Puntos de Presión',
        line=dict(color='blue', width=2),
        marker=dict(size=6)
    ))

    # Línea para result_selected
    seguimiento_grafico.add_trace(go.Scatter(
        x=matches_for_team_tournament['round_number'],
        y=matches_for_team_tournament['result_selected'],
        mode='lines+markers',
        name='Puntos Tradicionales (0, +1, +3)',
        line=dict(color='green', width=2),
        marker=dict(size=6)
    ))

    # Personalización del gráfico
    seguimiento_grafico.update_layout(
        title="Puntos de Presión y Tradicionales obtenidos por Ronda",
        xaxis_title="Número de Ronda",
        yaxis_title="Puntos",
        legend_title="Tipo de Puntos obtenidos",
        template="plotly_white"
    )

    seguimiento_grafico.update_xaxes(
        tickmode='linear',  # Muestra todos los ticks en escala lineal
        dtick=1,  # Intervalo de ticks
        tickangle=75
    )

    return seguimiento_grafico

def get_accumulated_graph(matches_for_team_tournament):
    """
    Genera un gráfico acumulado de puntos de presión ajustados y puntos tradicionales por ronda.

    Args:
        matches_for_team_tournament (pd.DataFrame): DataFrame con las columnas 'result_numeric' y 'pain_points'.

    Returns:
        go.Figure: Gráfico acumulado.
    """
    # Calcular los pain points ajustados fila por fila
    matches_for_team_tournament['pain_points_ajustados'] = matches_for_team_tournament.apply(
        lambda row: round((row['pain_points'])*2) if row['result_numeric'] == 1 else
                    (-row['pain_points']) if row['result_numeric'] == 0 else
                     (-(row['pain_points'])*2),
        axis=1
    )

    # Calcular los puntos tradicionales basados en el resultado
    matches_for_team_tournament['result_selected'] = matches_for_team_tournament['result_numeric'].map({
        1: 3,  # Victoria
        0: 1,  # Empate
        -1: 0  # Derrota
    })

    # Calcular acumulados
    matches_for_team_tournament['result_selected_acumulado'] = matches_for_team_tournament['result_selected'].cumsum()
    matches_for_team_tournament['pain_points_ajustados_acumulado'] = matches_for_team_tournament['pain_points_ajustados'].cumsum()

    # Crear el gráfico acumulado
    acumulado_grafico = go.Figure()

    # Línea para pain_points_ajustados_acumulado
    acumulado_grafico.add_trace(go.Scatter(
        x=matches_for_team_tournament['round_number'],
        y=matches_for_team_tournament['pain_points_ajustados_acumulado'],
        mode='lines+markers',
        name='Puntos de Presión',
        line=dict(color='blue', width=2),
        marker=dict(size=6)
    ))

    # Línea para result_selected_acumulado
    acumulado_grafico.add_trace(go.Scatter(
        x=matches_for_team_tournament['round_number'],
        y=matches_for_team_tournament['result_selected_acumulado'],
        mode='lines+markers',
        name='Puntos Tradicionales (0, +1, +3)',
        line=dict(color='green', width=2),
        marker=dict(size=6)
    ))

    # Personalización del gráfico
    acumulado_grafico.update_layout(
        title="Puntos Acumulados de Presión y Tradicionales por Ronda",
        xaxis_title="Número de Ronda",
        yaxis_title="Puntos Acumulados",
        legend_title="Tipo de Puntos Acumulados",
        template="plotly_white"
    )

    acumulado_grafico.update_xaxes(
        tickmode='linear',  # Muestra todos los ticks en escala lineal
        dtick=1,  # Intervalo de ticks
        tickangle=75
    )

    return acumulado_grafico

def mostrar_tarjeta_pain_points():
    st.markdown("""
    <div style="border: 2px solid #00FF7F; border-radius: 10px; padding: 20px; background: linear-gradient(145deg, #2E2E2E, #3A3A3A); box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.5);">
        <h2 style="color: #00FF7F; text-align: center; font-size: 1.8em;">Cálculo de Puntos de Presión</h2>
        <p style="color: #DDDDDD; font-size: 1.1em; text-align: justify;">Los <strong>Puntos de Presión</strong> se determinan según la localía, tomando en cuenta factores como favoritos al título o altura del estadio. La lógica es la siguiente:</p>
        <ul style="color: #FFFFFF; font-size: 1.1em; list-style: none; padding-left: 0;">
            <li style="margin-bottom: 10px;">
                <span style="color: #00FF7F; font-size: 1.3em;">✔️</span>
                <strong>Victoria:</strong> Los Puntos de Presión se multiplican por <strong>2</strong>. Refleja un impacto positivo tras una victoria.
            </li>
            <li style="margin-bottom: 10px;">
                <span style="color: #FFD700; font-size: 1.3em;">➖</span>
                <strong>Empate:</strong> Los Puntos de Presión juegan en contra de ambos equipos y se restan del total.
            </li>
            <li>
                <span style="color: #FF4500; font-size: 1.3em;">❌</span>
                <strong>Derrota:</strong> Los Puntos de Presión se multiplican por <strong>-2</strong>. Refleja un impacto negativo considerable tras una derrota.
            </li>
        </ul>
        <p style="color: #DDDDDD; font-size: 1.1em; text-align: justify;">Este ajuste permite entender el impacto en la carrera hacia el título al ganar en distintas localías y entre rivales directos.</p>
    </div>
    """, unsafe_allow_html=True)

# Función para generar el contenido HTML dinámico de las estadísticas
def generar_html_equipo(equipo, stats, color_primario, color_secundario, red_cards, yellow_cards):
    rgb_color = mcolors.hex2color(color_secundario)
    darker_rgb = [c * 0.55 for c in rgb_color] 
    color_secundario = mcolors.to_hex(darker_rgb)
    html = f"""
    <div style="width: 100%; margin: 4px auto; font-family: sans-serif; text-align: center;">
        <h3 style="color: {color_primario}; text-shadow: 1px 1px 1px grey;">{equipo}</h3>
        <p><strong>Tarjetas rojas:</strong> {int(red_cards)}</p>
        <p><strong>Tarjetas amarillas:</strong> {int(yellow_cards)}</p>
    """
    # Agrupar estadísticas por 'group' y generar HTML
    grouped_stats = stats.groupby('group')
    for group, group_data in grouped_stats:
        if group == 'Match overview':
            html += f"<h4 style='color: #2b3ef8; text-shadow: 1px 1px 1px grey;'>{group}</h4>"
            for _, row in group_data.iterrows():
                html += f"<p>{row['name']}: {int(row['Valor'])}</p>"

    for group, group_data in grouped_stats:
        if group != 'Match overview':
            if group == 'Goalkeeping':
                html += f"<h4 style='color: {color_secundario}; text-shadow: 1px 1px 1px grey;'>{group}</h4>"
                for _, row in group_data.iterrows():
                    html += f"<p>{row['name']}: {int(row['Valor'])}</p>"   
            else:
                html += f"<h4 style='color: {color_secundario}; text-shadow: 1px 1px 1px grey;'>{group}</h4>"
                for _, row in group_data.iterrows():
                    html += f"<p>{row['name']}: {int(row['Valor'])}</p>"

    html += "</div>"
    return html


@st.cache_data
def ajuste_spline_cubico(x, y):
    """
    Realiza un ajuste con spline cúbico de los datos y retorna valores ajustados.
    """
    spline = CubicSpline(x, y)
    return spline(x)
@st.cache_data
def get_grafico_match_momentum(df, color_home, color_away, selected_team, opponent_team, condicion_selected):
    """
    Genera un gráfico de momentum del partido con colores y nombres de equipos definidos por parámetros.
    
    Parameters:
        df (DataFrame): DataFrame con datos de momentum.
        color_home (str): Color para el equipo local.
        color_away (str): Color para el equipo visitante.
        selected_team (str): Nombre del equipo seleccionado.
        opponent_team (str): Nombre del equipo oponente.
        condicion_selected (str): Indica si el equipo seleccionado es "Local" o "Visitante".
    """
    # Procesar los datos para separar los valores positivos y negativos de momentum
    momentum_positivo = df[df['value'] > 0]
    momentum_negativo = df[df['value'] < 0]

    # Asignar colores basados en la condición
    color_selected = color_home if condicion_selected == "Local" else color_away
    color_opponent = color_away if condicion_selected == "Local" else color_home
    momentum_selected = momentum_positivo if condicion_selected == "Local" else momentum_negativo
    momentum_opponent = momentum_negativo if condicion_selected == "Local" else momentum_positivo
    # Crear el gráfico de Plotly
    fig = go.Figure()

    # Momentum positivo (equipo seleccionado)
    fig.add_trace(go.Bar(
        x=momentum_selected['minute'],
        y=momentum_selected['value'],
        name=selected_team,
        marker_color=color_selected
    ))

    # Momentum negativo (equipo oponente)
    fig.add_trace(go.Bar(
        x=momentum_opponent['minute'],
        y=momentum_opponent['value'],
        name=opponent_team,
        marker_color=color_opponent
    ))

    # Añadir línea de tendencia polinomial para el equipo seleccionado
    if not momentum_selected.empty:
        x_positivo = momentum_selected['minute']
        y_positivo = momentum_selected['value']
        y_tendencia_positiva = ajuste_spline_cubico(x_positivo, y_positivo)
        
        fig.add_trace(go.Scatter(
            x=x_positivo, 
            y=y_tendencia_positiva, 
            mode='lines', 
            name=f'Tendencia {selected_team}', 
            line=dict(color=color_selected, width=2)
        ))

    # Añadir línea de tendencia polinomial para el equipo oponente
    if not momentum_opponent.empty:
        x_negativo = momentum_opponent['minute']
        y_negativo = -momentum_opponent['value']  # Tomar valor absoluto para el ajuste
        y_tendencia_negativa = ajuste_spline_cubico(x_negativo, y_negativo)
        
        fig.add_trace(go.Scatter(
            x=x_negativo, 
            y=-y_tendencia_negativa, 
            mode='lines', 
            name=f'Tendencia {opponent_team}', 
            line=dict(color=color_opponent, width=2)
        ))

    # Añadir líneas verticales en cada intervalo de 15 minutos, omitiendo 0 y 90, y resaltando el minuto 45
    for minute in range(15, int(df['minute'].max()) + 1, 15):
        if minute != 90:
            color_line = "gold" if minute == 45 else "gray"  # Color ámbar dorado para el minuto 45
            fig.add_vline(
                x=minute,
                line=dict(
                    color=color_line,
                    dash="dash",
                    width=1.5 if minute == 45 else 1  
                ),
                opacity=0.7
            )

    # Agregar la zona gris entre -30 y 30 en el eje Y
    fig.add_shape(
        type="rect",
        x0=0,
        x1=df['minute'].max(),
        y0=-30,
        y1=30,
        fillcolor="gray",
        opacity=0.1,
        line=dict(width=0)
    )

    fig.update_layout(
        title=dict(
            text="Momentum de presión del partido",  # Texto del título
            x=0.5,  # Centrar horizontalmente
            xanchor="center",  # Anclaje al centro
            font=dict(size=18)  # Tamaño del título
        ),
        xaxis_title="Minuto",
        yaxis_title="Momentum",
        #template="plotly_dark",
        barmode='relative',
        xaxis=dict(
            showgrid=False,  # Ocultar cuadrícula en el eje x
            tickvals=list(range(0, int(df['minute'].max()) + 1, 15)),  # Valores de 0 a 15 y de 15 en 15

        ),
        yaxis=dict(
            showgrid=False,  # Ocultar cuadrícula en el eje y
            tickmode='array',  # Modo de marcas: array (sin marcas)
            tickvals=[],  # Valores de marcas vacío (ningún valor visible)
            range=[-100, 100]  # Fijar la escala del eje y entre -100 y 100
        ),
        legend=dict(
            orientation="h",  # Leyenda en horizontal
            yanchor="top",    # Anclada al borde superior
            y=-0.25,           # Colocada debajo del gráfico
            xanchor="center", # Centrada horizontalmente
            x=0.5,            # Posicionada al centro
            font=dict(size=10)  # Reducir tamaño de la fuente
        )
    )

    # Retornar el gráfico de Plotly
    return fig

@st.cache_data
def generar_formacion_basica(formacion, df_xi_titular):
    """
    Genera una representación de la formación en un VerticalPitch con posiciones correctas.

    Args:
        formacion (str): Formación en formato 'D-M-F'.
        df_xi_titular (DataFrame): DataFrame con información de los jugadores.
    
    Returns:
        fig: Figura matplotlib para usar con st.pyplot().
    """
    # Dividir la formación en defensas, mediocampistas y delanteros
    defensas, mediocampistas, delanteros = map(int, formacion.split('-'))

    # Inicializar VerticalPitch
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    fig, ax = pitch.draw(figsize=(8, 12))  # Crear la figura

    # Dividir la cancha en 15 segmentos (5 filas x 3 columnas por mitad)
    y_positions = [20, 40, 60, 80, 100]  # Filas (eje vertical)
    x_positions = [20, 40, 60, 80, 100]  # Columnas (eje horizontal)

    # Asignar posiciones en la cancha
    lineas = [
        (defensas, 20),  # Defensas (cerca del arco propio)
        (mediocampistas, 50),  # Mediocampistas (medio campo)
        (delanteros, 80)  # Delanteros (cerca del arco rival)
    ]

    # Ordenar jugadores por posición
    jugadores_defensa = df_xi_titular[df_xi_titular['position'] == 'D']
    jugadores_medio = df_xi_titular[df_xi_titular['position'] == 'M']
    jugadores_ataque = df_xi_titular[df_xi_titular['position'] == 'F']
    arquero = df_xi_titular[df_xi_titular['position'] == 'G']

    jugadores = {
        'D': jugadores_defensa,
        'M': jugadores_medio,
        'F': jugadores_ataque
    }

    # Colocar al arquero en el centro del arco inferior
    pitch.scatter(5, 50, ax=ax, color='red', s=300)  # Scatter del arquero
    ax.text(50, 8, arquero['name'].iloc[0], color='white', fontsize=10, ha='center', va='center')

    # Asignar jugadores según su posición y formación
    for (cantidad, y), tipo in zip(lineas, ['D', 'M', 'F']):
        jugadores_linea = jugadores[tipo].head(cantidad)
        x_step = len(x_positions) // cantidad if cantidad > 0 else 1
        x_indices = [x_positions[i] for i in range(0, len(x_positions), x_step)][:cantidad]


        if tipo == 'M':
            j=-1
            for i, jugador in enumerate(jugadores_linea.itertuples()):
                x = x_indices[i]
                pitch.scatter(y, x-6, ax=ax, color='blue', s=300)  # Scatter del jugador
                ax.text(x-6, y + 2*j, jugador.name, color='white', fontsize=13, ha='center', va='center')
                j*= -1

        elif tipo == 'F':
            j = -1
            for i, jugador in enumerate(jugadores_linea.itertuples()):
                x = x_indices[i]
                pitch.scatter(y, x+8, ax=ax, color='blue', s=300)
                ax.text(x+8, y + 2*j, jugador.name, color='white', fontsize=13, ha='center', va='center')
                j*= -1
        else:
            j = -1
            for i, jugador in enumerate(jugadores_linea.itertuples()):
                x = x_indices[i]
                pitch.scatter(y, x+8, ax=ax, color='blue', s=300)
                ax.text(x+8, y + 2*j, jugador.name, color='white', fontsize=13, ha='center', va='center')
                j*= -1

    # Ajustar y devolver la figura
    ax.set_title(f"Formación: {formacion}", fontsize=14, color='white')
    return fig

def graficar_posicion_tiros_fuera(df_shots_off_target, condicion):

    # Configuración del pitch
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

    # Crear la figura y el grid
    fig, axs = pitch.grid(
        figheight=10, title_height=0, endnote_space=0, 
        title_space=0, axis=False, grid_height=0.82, 
        endnote_height=0.01, grid_width=0.8,
    )

    # Título del gráfico
    fig.suptitle(f'Posición de tiros fuera del {condicion}', fontsize=22)

    # Crear hexbin y scatter plot
    hexmap = pitch.hexbin(
        x=100 - df_shots_off_target['x'], 
        y=100 - df_shots_off_target['y'], 
        ax=axs['pitch'], 
        edgecolors='#f4f4f4',
        gridsize=(6, 6), 
        cmap='Reds', 
        alpha=0.5
    )

    scatter = pitch.scatter(
        x=100 - df_shots_off_target['x'], 
        y=100 - df_shots_off_target['y'], 
        ax=axs['pitch'], 
        color=df_shots_off_target['color'], 
        s=200, 
        edgecolors='black', 
        zorder=2, 
        alpha=0.9
    )

    # Anotar los tiempos sobre los puntos
    for _, row in df_shots_off_target.iterrows():
        axs['pitch'].annotate(
            text=row['time'], 
            xy=(100 - row['y'], 100 - row['x']), 
            color='white', 
            ha='center', 
            va='center',
            fontsize=8, 
            weight='bold', 
            zorder=3
        )

    # Crear elementos de la leyenda
    legend_elements = []
    for _, row in df_shots_off_target.iterrows():
        legend_elements.append(Patch(
            facecolor=row['color'], 
            edgecolor='black', 
            label=f"{row['time']}' {row['shortName']} - {row['situation']} | {row['bodyPart']}"
        ))

    # Configuración de la leyenda
    legend = axs['pitch'].legend(
        handles=legend_elements, 
        loc='lower left', 
        bbox_to_anchor=(0.02, 0.02), 
        frameon=True, 
        fontsize=10
    )
    legend.get_frame().set_alpha(0.7)  # Fondo semi-transparente

    # Ajustar diseño y mostrar
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    return fig


def graficar_tiros_al_arco(df_shots_on_target, condicion):
    # Procesar las coordenadas del DataFrame
    df_coordenadas = df_shots_on_target['goalMouthCoordinates'].reset_index(drop=True)
    dict_list = [eval(coord) for coord in df_coordenadas.tolist()]
    df_goalzone = pd.DataFrame(dict_list)
    df_goalzone['shotType'] = df_shots_on_target['shotType'].values
    df_goalzone['situation'] = df_shots_on_target['situation'].values
    df_goalzone['bodyPart'] = df_shots_on_target['bodyPart'].values
    df_goalzone['goalMouthLocation'] = df_shots_on_target['goalMouthLocation'].values
    df_goalzone['time'] = df_shots_on_target['time'].values
    df_goalzone['shortName'] = df_shots_on_target['shortName'].values
    df_goalzone['position'] = df_shots_on_target['position'].values
    df_goalzone['color'] = df_shots_on_target['color'].values
    if 'goalType' in df_shots_on_target.columns:
        df_goalzone['goalType'] = df_shots_on_target['goalType'].values

    # Crear scatter plot mejorado
    fig = px.scatter(
        df_goalzone, 
        x='y', 
        y='z', 
        title=f'Ubicación de tiros a puerta del equipo {condicion}', 
        labels={'y': 'Ancho', 'z': 'Altura'}, 
        color='color',
        color_discrete_map={'darkgreen': 'darkgreen', 'darkgoldenrod': 'darkgoldenrod', 'coral': 'coral', 'darkred': 'darkred'},
        hover_data={'shortName': True, 'shotType': True, 'time': True, 'situation': True, 'bodyPart': True, 'goalMouthLocation': True, 'y': False, 'z': False, 'color': False},
        size_max=20  # Ajustar tamaño máximo de puntos
    )

    # Personalizar los marcadores
    fig.update_traces(marker=dict(size=12, line=dict(width=2, color='black')))

    # Configuración del área de gol
    fig.update_xaxes(autorange="reversed")
    fig.add_shape(type="line", x0=45.4, y0=0, x1=45.4, y1=35.5, line=dict(color="Black", width=2))
    fig.add_shape(type="line", x0=54.5, y0=0, x1=54.5, y1=35.5, line=dict(color="Black", width=2))
    fig.add_shape(type="line", x0=45.4, y0=35.5, x1=54.5, y1=35.5, line=dict(color="Black", width=2))

    # Ajustar ejes y apariencia
    fig.update_xaxes(showgrid=False, visible=False, showticklabels=False, ticks="")
    fig.update_yaxes(showgrid=False, visible=False, showticklabels=False, ticks="")
    fig.update_layout(
        showlegend=False,
    )

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)


def graficar_posicion_tiros_a_puerta(df_shots_on_target, condicion):
    from matplotlib.patches import Patch

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

    fig, axs = pitch.grid(
        figheight=10, title_height=0, endnote_space=0, 
        title_space=0, axis=False, grid_height=0.82, 
        endnote_height=0.01, grid_width=0.8,
    )

    # Dibujar hexbin y scatter
    hexmap = pitch.hexbin(
        x=100-df_shots_on_target['x'], 
        y=100-df_shots_on_target['y'], 
        ax=axs['pitch'], edgecolors='#f4f4f4',
        gridsize=(6, 6), cmap='PuBu', alpha=.5
    )
    scatter = pitch.scatter(
        x=100-df_shots_on_target['x'], 
        y=100-df_shots_on_target['y'], 
        ax=axs['pitch'], 
        color=df_shots_on_target['color'], 
        s=200, edgecolors='black', zorder=2, alpha=.9
    )

    # Anotar los tiempos sobre el gráfico
    for i, row in df_shots_on_target.iterrows():
        axs['pitch'].annotate(
            row['time'], 
            (100-row['y'], 100-row['x']), 
            color='black', ha='center', va='center',
            fontsize=6, weight='bold', zorder=3
        )

    # Título del gráfico
    fig.suptitle(f'Posición de tiros a puerta del {condicion}', fontsize=22)

    # Crear los elementos de la leyenda
    legend_elements = []
    for _, row in df_shots_on_target.iterrows():
        color = row['color']
        legend_elements.append(Patch(
            facecolor=color, edgecolor='black', 
            label=f"{row['time']}' {row['shortName']} - {row['situation']} | {row['bodyPart']}"
        ))

    # Usar plt.legend para agregar la leyenda con fondo transparente
    legend = axs['pitch'].legend(
        handles=legend_elements, loc='lower left', 
        bbox_to_anchor=(0.02, 0.02), frameon=True, fontsize=10
    )
    legend.get_frame().set_alpha(0.7)  # Fondo semi-transparente

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    return fig
