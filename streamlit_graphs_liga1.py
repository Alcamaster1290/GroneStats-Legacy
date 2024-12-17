import streamlit as st
import plotly.graph_objects as go

def crear_grafico_indicador(selected_score, opponent_score, team_name, opponent, pain_points):
    """
    Crea un gráfico indicador utilizando Plotly y muestra los pain points en un indicador central con colores dinámicos.
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

    # Obtener el color correspondiente al valor de pain_points
    color = color_map.get(pain_points, "gray")
    
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

    # Indicador de Pain Points en el centro (col2) con cambio de color
    with col2:
        fig.add_trace(go.Indicator(
            mode="number",
            value=pain_points,
            title={"text": "IMPORTANCIA"},
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'size': 30, 'color': color}}  # Cambiar el color basado en los pain_points
        ))

    fig.update_layout(
            width=1000,  # Ancho en píxeles
            height=230  # Alto en píxeles
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

