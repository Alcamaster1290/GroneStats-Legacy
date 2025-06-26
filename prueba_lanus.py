from LanusStats import SofaScore  # Asegúrate de que tu clase está en sofascore_module.py o como sea tu módulo
import undetected_chromedriver as uc

def obtener_datos_completos_del_partido(URL_match):
    ss = SofaScore()

    print("▶️ Obteniendo datos generales del partido...")
    match_data = ss.get_match_data(URL_match)

    print("▶️ Obteniendo equipos...")
    home_team, away_team = ss.get_team_names(URL_match)
    print(f"📌 Local: {home_team} vs Visitante: {away_team}")

    print("▶️ Obteniendo mapa de tiros...")
    shotmap = ss.get_match_shotmap(URL_match)

    print("▶️ Obteniendo momentum del partido...")
    momentum = ss.get_match_momentum(URL_match)

    print("▶️ Obteniendo alineaciones y estadísticas por jugador...")
    home_players, away_players = ss.get_players_match_stats(URL_match)

    print("▶️ Obteniendo posiciones promedio de los jugadores...")
    avg_pos_home, avg_pos_away = ss.get_players_average_positions(URL_match)

    print("▶️ Obteniendo heatmap por jugador...")
    player_ids = ss.get_player_ids(URL_match)
    heatmaps = {}
    for player in list(player_ids.keys())[:3]:  # Limita a 3 jugadores para no abusar
        try:
            heatmaps[player] = ss.get_player_heatmap(URL_match, player)
        except:
            heatmaps[player] = None
            print(f"⚠️ No se pudo obtener heatmap para {player}")

    return {
        "match_data": match_data,
        "momentum": momentum,
        "shotmap": shotmap,
        "alineacion_local": home_players,
        "alineacion_visita": away_players,
        "posiciones_promedio_local": avg_pos_home,
        "posiciones_promedio_visita": avg_pos_away,
        "heatmaps": heatmaps
    }

# Ejemplo de uso
if __name__ == "__main__":
    URL_match = "https://www.sofascore.com/universidad-cesar-vallejo-alianza-lima/lWsGfc#id:11967822"
    datos = obtener_datos_completos_del_partido(URL_match)

    # Puedes imprimir o guardar los dataframes según tu flujo
    print("🎯 Datos obtenidos correctamente.")
    print(datos["match_data"])
    print(datos["momentum"])
    print(datos["shotmap"])
    print(datos["alineacion_local"])
    print(datos["alineacion_visita"])
    print(datos["posiciones_promedio_local"])
    print(datos["posiciones_promedio_visita"])
    for player, heatmap in datos["heatmaps"].items():
        if heatmap is not None:
            print(f"Heatmap para {player}:")
            print(heatmap)
        else:
            print(f"No hay heatmap disponible para {player}.")
# Este script es un ejemplo de cómo usar la clase SofaScore para obtener datos de un partido específico.
# Asegúrate de que la URL del partido es correcta y que el partido está disponible en SofaScore.
# Asegúrate de que la clase SofaScore está correctamente implementada y que todas las funciones están disponibles.
# Asegúrate de que tienes las dependencias necesarias instaladas y que tu entorno está configurado correctamente.