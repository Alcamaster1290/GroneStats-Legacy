import plotly.graph_objects as go

def crear_grafico_indicador(home_score, away_score, pain_points):
    """
    Crea un gráfico indicador utilizando Plotly.
    """
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=home_score,
        title={"text": "Goles Local"},
        delta={'reference': away_score},
        domain={'x': [0, 0.5], 'y': [0, 1]}
    ))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=pain_points,
        title={"text": "Puntos de Dolor"},
        delta={'reference': 0},
        domain={'x': [0.5, 1], 'y': [0, 1]}
    ))

    fig.update_layout(
        grid={'rows': 1, 'columns': 2, 'pattern': "independent"},
        template={"data": {"indicator": [{"title": {"text": "Score"}}]}}
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
        hovermode="closest"
    )
    return fig2

