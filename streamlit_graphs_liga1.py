import streamlit as st
import plotly.graph_objects as go
import numpy as np
import matplotlib.colors as mcolors
from streamlit_cache_funcs_liga1 import get_team_id

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

from scipy.interpolate import CubicSpline

def ajuste_spline_cubico(x, y):
    """
    Realiza un ajuste con spline cúbico de los datos y retorna valores ajustados.
    """
    spline = CubicSpline(x, y)
    return spline(x)
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
        ),
        yaxis=dict(
            showgrid=False,  # Ocultar cuadrícula en el eje y
            tickmode='array',  # Modo de marcas: array (sin marcas)
            tickvals=[],  # Valores de marcas vacío (ningún valor visible)
            range=[-110, 110]  # Fijar la escala del eje y entre -100 y 100
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
