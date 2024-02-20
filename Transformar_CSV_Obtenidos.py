import pandas as pd

traducciones = {
    'Expected goals': 'Goles esperados',
    'Ball possession': 'Posesión del balón',
    'Total shots': 'Tiros totales',
    'Shots on target': 'Tiros a puerta',
    'Shots off target': 'Tiros fuera',
    'Blocked shots': 'Tiros bloqueados',
    'Corner kicks': 'Saques de esquina',
    'Offsides': 'Fuera de juego',
    'Fouls': 'Faltas',
    'Yellow cards': 'Tarjetas Amarillas',
    'Red cards': 'Tarjetas Rojas',
    'Free kicks': 'Tiros libres',
    'Throw-ins': 'Saques de banda',
    'Goal kicks': 'Saques de puerta',
    'Big chances': 'Grandes oportunidades',
    'Big chances missed': 'Grandes oportunidades falladas',
    'Counter attacks': 'Contraataques',
    'Counter attack shots': 'Tiros de contraataque',
    'Shots inside box': 'Tiros dentro del área',
    'Shots outside box': 'Tiros fuera del área',
    'Goalkeeper saves': 'Paradas del portero',
    'Passes': 'Pases',
    'Accurate passes': 'Pases acertados',
    'Long balls': 'Balones largos',
    'Crosses': 'Centros',
    'Dribbles': 'Regates',
    'Possession lost': 'Posesión perdida',
    'Duels won': 'Duelos ganados',
    'Aerials won': 'Duelos aéreos ganados',
    'Tackles': 'Entradas',
    'Interceptions': 'Intercepciones',
    'Clearances': 'Despejes',
    'goals': 'Goles',
    'yellowCards': 'Tarjetas Amarillas',
    'redCards': 'Tarjetas Rojas',
    'groundDuelsWon': 'Duelos por Tierra Ganados',
    'groundDuelsWonPercentage': 'Porcentaje de Duelos por Tierra Ganados',
    'aerialDuelsWon': 'Duelos Aéreos Ganados',
    'aerialDuelsWonPercentage': 'Porcentaje de Duelos Aéreos Ganados',
    'successfulDribbles': 'Regates Exitosos',
    'successfulDribblesPercentage': 'Porcentaje de Regates Exitosos',
    'tackles': 'Entradas',
    'assists': 'Asistencias',
    'accuratePassesPercentage': 'Porcentaje de Pases Acertados',
    'totalDuelsWon': 'Total de Duelos Ganados',
    'totalDuelsWonPercentage': 'Porcentaje Total de Duelos Ganados',
    'minutesPlayed': 'Minutos Jugados',
    'wasFouled': 'Fue Faltado',
    'fouls': 'Faltas',
    'dispossessed': 'Desposesiones',
    'appearances': 'Apariciones',
    'saves': 'Atajadas',
    'savedShotsFromInsideTheBox': 'Tiros Salvados Dentro del Área',
    'savedShotsFromOutsideTheBox': 'Tiros Salvados Fuera del Área',
    'goalsConcededInsideTheBox': 'Goles Recibidos Dentro del Área',
    'goalsConcededOutsideTheBox': 'Goles Recibidos Fuera del Área',
    'highClaims': 'Reclamos Altos',
    'successfulRunsOut': 'Salidas Exitosas',
    'punches': 'Puñetazos',
    'runsOut': 'Salidas',
    'accurateFinalThirdPasses': 'Pases Acertados en el Último Tercio',
    'bigChancesCreated': 'Grandes Oportunidades Creadas',
    'accuratePasses': 'Pases Acertados',
    'keyPasses': 'Pases Clave',
    'accurateCrosses': 'Centros Acertados',
    'accurateCrossesPercentage': 'Porcentaje de Centros Acertados',
    'accurateLongBalls': 'Balones Largos Acertados',
    'accurateLongBallsPercentage': 'Porcentaje de Balones Largos Acertados',
    'interceptions': 'Intercepciones',
    'clearances': 'Despejes',
    'dribbledPast': 'Regateado por el Adversario',
    'bigChancesMissed': 'Grandes Oportunidades Falladas',
    'totalShots': 'Tiros Totales',
    'shotsOnTarget': 'Tiros al Arco',
    'blockedShots': 'Tiros Bloqueados',
    'goalConversionPercentage': 'Porcentaje de Conversión de Gol',
    'Hit woodwork': 'Balones al Poste',
    'hitWoodwork': 'Balones al Poste',
    'offsides': 'Fueras de Juego',
    'expectedGoals': 'Goles Esperados',
    'errorLeadToGoal': 'Errores que Llevan a Gol',
    'errorLeadToShot': 'Errores que Llevan a Tiro',
    'passToAssist': 'Pase para Asistencia',
    'player': 'Jugador',
    'name': 'Nombre',
    'shortName': 'Nombre Corto',
    'position': 'Posición',
    'jerseyNumber': 'Número de Camiseta',
    'country': 'País',
    'marketValueCurrency': 'Moneda del Valor de Mercado',
    'shirtNumber': 'Número de Camiseta',
    'substitute': 'Suplente',
    'totalPass': 'Total de Pases',
    'accuratePass': 'Pases Acertados',
    'totalLongBalls': 'Total de Balones Largos',
    'Balones Largos Acertados': 'Balones Largos Acertados',
    'Minutos Jugados': 'Minutos Jugados',
    'touches': 'Toques',
    'rating': 'Calificación',
    'possessionLostCtrl': 'Posesión Perdida',
    'keyPass': 'Pases Clave',
    'ratingVersions': 'Versiones de Calificación',
    'totalCross': 'Total de Centros',
    'accurateCross': 'Centros Acertados',
    'aerialLost': 'Duelos Aéreos Perdidos',
    'aerialWon': 'Duelos Aéreos Ganados',
    'duelLost': 'Duelos Perdidos',
    'duelWon': 'Duelos Ganados',
    'challengeLost': 'Desafíos Perdidos',
    'shotOffTarget': 'Tiros Fuera',
    'totalClearance': 'Despejes Totales',
    'interceptionWon': 'Intercepciones Ganadas',
    'totalTackle': 'Entradas Totales',
    'Fue Faltado': 'Fue Faltado',
    'Faltas': 'Faltas',
    'totalOffside': 'Total de Fueras de Juego',
    'Desposesiones': 'Desposesiones',
    'totalContest': 'Total de Contiendas',
    'wonContest': 'Contiendas Ganadas',
    'onTargetScoringAttempt': 'Intentos de Anotación al Arco',
    'goalAssist': 'Asistencias de Gol',
    'bigChanceMissed': 'Grandes Oportunidades Falladas',
    'blockedScoringAttempt': 'Intentos de Anotación Bloqueados',
    'bigChanceCreated': 'Grandes Oportunidades Creadas',
    'Goles': 'Goles',
    'Balones al Poste': 'Balones al Poste',
    'captain': 'Capitán',
}

def estadisticas_transformar_csv_a_xlsx(ruta_csv, ruta_xlsx):
    df= pd.read_csv(ruta_csv),
    # Renombrar las FILAS a español
    df['Estadistica'] = df['Estadistica'].map(traducciones).fillna(df['Estadistica'])
    df['Completado'] = df['NumeroCamiseta'].astype(float)
    df['Intentado'] = df['Intentado'].astype(float)
    # Guardar el DataFrame como archivo XLSX
    #df.to_excel(ruta_xlsx, index=False, engine='openpyxl')


def jugadores_transformar_csv_a_xlsx(ruta_csv, ruta_xlsx):
    df= pd.read_csv(ruta_csv),
    df.rename(columns=traducciones, inplace=True)
    # Convertir columnas booleanas a 'Sí' y 'No'
    df['Suplente'] = df['Suplente'].map({True: 'Sí', False: 'No'})
    df['Capitan'] = df['Capitan'].map({1.0: 'Sí', 0.0: 'No'})

    # Verificar y ajustar tipos de datos 
    df['NumeroCamiseta'] = df['NumeroCamiseta'].astype(int)  # Asegurarse de que los números de camiseta sean enteros

    # Guardar el DataFrame como archivo XLSX
    #df.to_excel(ruta_xlsx, index=False, engine='openpyxl')

# Lista de archivos CSV para transformar


jugadores_csv = [
    'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\CSV obtenidos\AL_J1_jugadores.csv',
    'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\CSV obtenidos\AL_J2_jugadores.csv',
    'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\CSV obtenidos\AL_J3_jugadores.csv',
    'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\CSV obtenidos\AL_J4_jugadores.csv',
]

estadisticas_csv = [
    'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\CSV obtenidos\AL_J1_estadisticas.csv',
    'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\CSV obtenidos\AL_J2_estadisticas.csv',
    'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\CSV obtenidos\AL_J3_estadisticas.csv',
    'C:\Users\Alvaro\Proyectos\Proyecto Gronestats\GroneStats\CSV obtenidos\AL_J4_estadisticas.csv',
]

for archivo_csv in jugadores_csv:
    # Crear la ruta del archivo XLSX basado en la ruta del archivo CSV
    ruta_xlsx = archivo_csv.replace('.csv', '.xlsx')

    # Llamar a la función para transformar el archivo
    jugadores_transformar_csv_a_xlsx(archivo_csv,ruta_xlsx)
    print(f'Archivo de Jugadores transformado y guardado como: {ruta_xlsx}')

for archivo_csv in estadisticas_csv:
    # Crear la ruta del archivo XLSX basado en la ruta del archivo CSV
    ruta_xlsx = archivo_csv.replace('.csv', '.xlsx')

    # Llamar a la función para transformar el archivo
    estadisticas_transformar_csv_a_xlsx(archivo_csv,ruta_xlsx)
    print(f'Archivo de Estadisticas transformado y guardado como: {ruta_xlsx}')