import streamlit as st
import plotly.graph_objects as go

def crear_grafico_score(selected_score, opponent_score, team_name, opponent, pain_points):
    """
    Crea un gráfico indicador utilizando Plotly y muestra los pain points en un indicador central tipo gauge.
    """
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

    # Configuración de columnas en Streamlit
    col1, col2, col3 = st.columns(3)

    # Indicador para los goles del equipo (col1)
    with col1:
        fig.add_trace(go.Indicator(
            mode="number",
            value=selected_score,
            title={"text": f"{team_name}"},
            domain={'x': [0, 0.33], 'y': [0, 1]}  # Ajustar la columna a la izquierda
        ))

    # Indicador para los goles del oponente (col3)
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
            title={"text": text},
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
        height=250  # Alto en píxeles (mayor para el gauge)
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
        lambda row: round(row['pain_points']*2) if row['result_numeric'] == 1 else
                    (-row['pain_points'] if row['result_numeric'] == 0 else
                     -row['pain_points']*2),
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
    <div style="border: 2px solid #00FF7F; border-radius: 10px; padding: 15px; background-color: #2E2E2E;">
        <h2 style="color: #00FF7F;">Cálculo de Puntos de presión</h2>
        <p style="color: #FFFFFF;">Este cálculo se realiza para ajustar los Puntos de presión en función del resultado del partido. La lógica es la siguiente:</p>
        <ul style="color: #FFFFFF;">
            <li><strong>Victoria:</strong> Los Puntos de presión se multiplican por 2. Refleja un impacto positivo tras una victoria.</li>
            <li><strong>Empate:</strong> Los Puntos de presión juegan en contra de ambos y se restan al total. </li>
            <li><strong>Derrota:</strong> Los Puntos de presión se multiplican por -2. Refleja un impacto negativo considerable tras una derrota.</li>
        </ul>
        <p style="color: #FFFFFF;">Este ajuste permite entender mejor el impacto emocional y psicológico que cada resultado puede tener sobre el equipo al ganar en distintas localías y a rivales directos.</p>
    </div>
    """, unsafe_allow_html=True)