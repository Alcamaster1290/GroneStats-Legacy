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
        0: "Sin presión",
        1: "Equipo de altura de local",
        2: "Ambos equipos de altura",
        3: "Equipo de altura de visitante",
        4: "Candidato al título en altura",
        5: "Duelo decisivo entre candidatos al título"
    }

    # Obtener el color correspondiente al valor de pain_points
    color = color_map.get(pain_points, "gray")
    text = indicator_map.get(pain_points)


    # Configuración de columnas en Streamlit
    col1, col2, col3 = st.columns(3)

    # Crear el gráfico indicador
    fig = go.Figure()

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
                    {'range': [2, 3], 'color': 'yellow'},
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



def generar_figura_pain_points(matches_for_team_tournament, selected_team, selected_tournament, selected_year):
    """Genera la figura de Pain Points vs Número de Ronda."""
    fig1 = go.Figure()

    matches_for_team_tournament = matches_for_team_tournament.sort_values(by=['round_number'], ascending=False)

    fig1.add_trace(go.Scatter(
        x=matches_for_team_tournament['round_number'], 
        y=matches_for_team_tournament['pain_points'], 
        mode='lines+markers', 
        marker=dict(color='blue', size=8),
        line=dict(color='blue', width=2),
        name='Pain Points'
    ))

    fig1.update_layout(
        title=f"Necesidad de victoria para {selected_team} en {selected_tournament} {selected_year}",
        xaxis_title="Número de Ronda",
        yaxis_title="Pain Points",
        yaxis=dict(range=[-0.9, 5.1]),
        template="plotly_dark",
        plot_bgcolor="rgb(50, 50, 50)",
        font=dict(color="white"),
        hovermode="closest"
    )
    return fig1

def generar_figura_resultados(matches_for_team_tournament):
    """Genera la figura de Resultados vs Número de Ronda."""
    result_map = {'home': 1, 'draw': 0, 'away': -1}
    matches_for_team_tournament['result_numeric'] = matches_for_team_tournament['result'].map(result_map)

    matches_df = matches_for_team_tournament.sort_values(by=['round_number'], ascending=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=matches_df['round_number'], 
        y=matches_df['result_numeric'], 
        mode='lines+markers', 
        marker=dict(color='blue', size=8),
        line=dict(color='blue', width=2),
        name='Resultado'
    ))

    fig2.update_layout(
        title="Resultados de los partidos por ronda",
        xaxis_title="Número de Ronda",
        yaxis_title="Resultado (1=Home, 0=Draw, -1=Away)",
        yaxis=dict(tickvals=[-1, 0, 1], ticktext=['Away', 'Draw', 'Home']),
        template="plotly_dark",
        plot_bgcolor="rgb(50, 50, 50)",
        font=dict(color="white"),
        hovermode="closest",
    )
    return fig2

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