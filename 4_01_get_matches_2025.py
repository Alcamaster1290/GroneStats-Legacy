import os
import pandas as pd
import ScraperFC
import LanusStats as ls

# Crear una instancia del objeto Sofascore
sofascore = ScraperFC.Sofascore()
sofascore_ls = ls.SofaScore()

# Pedir el match_id al usuario
match_id = '13123301'  # Puedes cambiarlo o pedirlo como input al usuario

# Directorio de salida
output_dir = "Sofascore_2025"
os.makedirs(output_dir, exist_ok=True)

# Nombre del archivo de salida
output_file = os.path.join(output_dir, f'Sofascore_{match_id}.xlsx')

try:
    # Obtener datos del partido
    match_stats = sofascore.scrape_team_match_stats(match_id)
    player_stats = sofascore.scrape_player_match_stats(match_id)
    average_positions = sofascore.scrape_player_average_positions(match_id)
    match_url = sofascore.get_match_url_from_id(match_id)
    match_shotmap_df = sofascore_ls.get_match_shotmap(match_url)
    match_momentum = sofascore.scrape_match_momentum(match_id)

    # Obtener datos del heatmap
    heatmap_data = sofascore.scrape_heatmaps(match_id)
    heatmap_list = []
    
    if heatmap_data:
        for player_id, heatmap in heatmap_data.items():
            heatmap_list.append({'player': player_id, 'heatmap': heatmap})
        df_heatmaps = pd.DataFrame(heatmap_list)
    else:
        df_heatmaps = pd.DataFrame(columns=['player', 'heatmap'])  # DataFrame vacío con columnas correctas

    # Crear un archivo Excel con todos los datos en hojas separadas
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        match_stats.to_excel(writer, sheet_name='Team Stats', index=False)
        player_stats.to_excel(writer, sheet_name='Player Stats', index=False)
        average_positions.to_excel(writer, sheet_name='Average Positions', index=False)
        match_shotmap_df.to_excel(writer, sheet_name='Shotmap', index=False)
        match_momentum.to_excel(writer, sheet_name='Match Momentum', index=False)
        
        if not df_heatmaps.empty:
            df_heatmaps.to_excel(writer, sheet_name='Heatmap', index=False)

    print(f"Datos exportados a {output_file} con éxito.")

except Exception as e:
    print(f"Error al obtener datos para el partido {match_id}: {e}")
