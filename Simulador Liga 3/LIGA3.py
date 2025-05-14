import random
import pandas as pd

# Definición de equipos por grupo (sin cambios)
grupos = {
    'Grupo_A': [
        'Club Unión Santo Domingo (Amazonas)', 'Cultural Volante (Cajamarca)', 'Juventus FC Huamachuco (La Libertad)',
        'U. César Vallejo (R)', 'Carlos Stein (Lambayeque)', 'Deportivo Lute (Lambayeque)',
        'Juan Aurich (Lambayeque)', 'Juventud Cautivo (Piura)', 'Sport Bolognesi (Tumbes)'
    ],
    'Grupo_B': [
        'Centro Social Pariacoto (Áncash)', 'Amazon Callao (Callao)', 'Sport Boys (R)', 'Juventud Santo Domingo (Ica)',
        'Alianza Lima (R)', 'Deportivo Municipal', 'Pacifico FC (Lima)', 'Unión Huaral',
        'Universitario de Deportes (R)', 'Estudiantil CNI (Loreto)'
    ],
    'Grupo_C': [
        'Nuevo San Cristóbal (Ayacucho)', 'Unión Deportivo Ascension UDA (Huancavelica)', 'Construcción Civil (Huánuco)',
        'Asociación Deportiva Tarma (R)', 'Deportivo Municipal Pangoa (Junín)', 'Sport Huancayo (R)',
        'Ecosem Pasco (Pasco)', 'Deportivo Ucrania (San Martín)', 'Rauker FC Calleria (Ucayali)'
    ],
    'Grupo_D': [
        'Defensor Jose María Arguedas (Apurímac)', 'FBC Melgar (R)', 'Nacional FBC (Arequipa)', 'Cienciano (R)',
        'Juventud Alfa F.C. (Cusco)', 'Alto Rendimiento JVM (Madre de Dios)', 'FCR San Antonio (Moquegua)',
        'Diablos Rojos (Puno)', 'Patriotas FC Tacna'
    ]
}

def simular_grupo(grupo_equipos, partidos_log=None, nombre_grupo=None):
    tabla = pd.DataFrame({
        'Equipo': grupo_equipos,
        'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0,
        'GF': 0, 'GC': 0, 'DG': 0, 'Puntos': 0
    })

    for i in range(len(grupo_equipos)):
        for j in range(i + 1, len(grupo_equipos)):
            eq1, eq2 = grupo_equipos[i], grupo_equipos[j]

            # Partido de ida
            goles1, goles2 = simular_partido(eq1, eq2)
            if partidos_log is not None:
                partidos_log.append({
                    'Fase': 'Fase Regular' if nombre_grupo else 'Fase Final',
                    'Grupo': nombre_grupo if nombre_grupo else '',
                    'Local': eq1,
                    'Visitante': eq2,
                    'Goles Local': goles1,
                    'Goles Visitante': goles2
                })
            for eq, gf, gc in [(eq1, goles1, goles2), (eq2, goles2, goles1)]:
                idx = tabla[tabla['Equipo'] == eq].index[0]
                tabla.at[idx, 'PJ'] += 1
                tabla.at[idx, 'GF'] += gf
                tabla.at[idx, 'GC'] += gc
            if goles1 > goles2:
                tabla.loc[tabla['Equipo'] == eq1, ['PG', 'Puntos']] += [1, 3]
                tabla.loc[tabla['Equipo'] == eq2, 'PP'] += 1
            elif goles2 > goles1:
                tabla.loc[tabla['Equipo'] == eq2, ['PG', 'Puntos']] += [1, 3]
                tabla.loc[tabla['Equipo'] == eq1, 'PP'] += 1
            else:
                tabla.loc[tabla['Equipo'].isin([eq1, eq2]), ['PE', 'Puntos']] += [1, 1]

            # Partido de vuelta
            goles1, goles2 = simular_partido(eq2, eq1)
            if partidos_log is not None:
                partidos_log.append({
                    'Fase': 'Fase Regular' if nombre_grupo else 'Fase Final',
                    'Grupo': nombre_grupo if nombre_grupo else '',
                    'Local': eq2,
                    'Visitante': eq1,
                    'Goles Local': goles1,
                    'Goles Visitante': goles2
                })
            for eq, gf, gc in [(eq2, goles1, goles2), (eq1, goles2, goles1)]:
                idx = tabla[tabla['Equipo'] == eq].index[0]
                tabla.at[idx, 'PJ'] += 1
                tabla.at[idx, 'GF'] += gf
                tabla.at[idx, 'GC'] += gc
            if goles1 > goles2:
                tabla.loc[tabla['Equipo'] == eq2, ['PG', 'Puntos']] += [1, 3]
                tabla.loc[tabla['Equipo'] == eq1, 'PP'] += 1
            elif goles2 > goles1:
                tabla.loc[tabla['Equipo'] == eq1, ['PG', 'Puntos']] += [1, 3]
                tabla.loc[tabla['Equipo'] == eq2, 'PP'] += 1
            else:
                tabla.loc[tabla['Equipo'].isin([eq1, eq2]), ['PE', 'Puntos']] += [1, 1]

    tabla['DG'] = tabla['GF'] - tabla['GC']
    tabla = tabla.sort_values(by=['Puntos', 'DG', 'GF'], ascending=False).reset_index(drop=True)
    return tabla



def simular_partido(home, away):
    """Simula un partido con ventaja por localía y equipos reserva (R)"""
    ventaja_home = 1.5 + (0.3 if '(R)' in home else 0)
    ventaja_away = 1.0 + (0.3 if '(R)' in away else 0)
    
    goles_home = max(0, int(random.gauss(ventaja_home, 1.2)))
    goles_away = max(0, int(random.gauss(ventaja_away, 1.0)))
    
    return goles_home, goles_away

def determinar_local_vuelta(eq1, eq2, df_acumulada):
    """Determina el orden de los partidos según tabla acumulada"""
    try:
        pos1 = df_acumulada[df_acumulada['Equipo'] == eq1].index[0]
        pos2 = df_acumulada[df_acumulada['Equipo'] == eq2].index[0]
        return (eq2, eq1) if pos1 < pos2 else (eq1, eq2)
    except:
        return (eq1, eq2)

def simular_llave(eq1, eq2, df_acumulada, etapa, partidos_log=None):
    local_ida, local_vuelta = (eq2, eq1) if etapa == 'cuartos' else determinar_local_vuelta(eq1, eq2, df_acumulada)
    # Ida
    goles_ida = simular_partido(local_ida, eq1 if local_ida == eq2 else eq2)
    if partidos_log is not None:
        partidos_log.append({
            'Fase': etapa.capitalize(),
            'Grupo': '',
            'Local': local_ida,
            'Visitante': eq1 if local_ida == eq2 else eq2,
            'Goles Local': goles_ida[0],
            'Goles Visitante': goles_ida[1]
        })
    # Vuelta
    goles_vuelta = simular_partido(local_vuelta, eq2 if local_vuelta == eq1 else eq1)
    if partidos_log is not None:
        partidos_log.append({
            'Fase': etapa.capitalize(),
            'Grupo': '',
            'Local': local_vuelta,
            'Visitante': eq2 if local_vuelta == eq1 else eq1,
            'Goles Local': goles_vuelta[0],
            'Goles Visitante': goles_vuelta[1]
        })

    # Calcular agregado
    if local_ida == eq2:
        agregado_eq1 = goles_ida[1] + goles_vuelta[0]
        agregado_eq2 = goles_ida[0] + goles_vuelta[1]
    else:
        agregado_eq1 = goles_ida[0] + goles_vuelta[1]
        agregado_eq2 = goles_ida[1] + goles_vuelta[0]

    logs = [
        f"{etapa.capitalize()} Ida: {local_ida} {goles_ida[0]}-{goles_ida[1]}",
        f"{etapa.capitalize()} Vuelta: {local_vuelta} {goles_vuelta[0]}-{goles_vuelta[1]}",
        f"Agregado: {eq1} {agregado_eq1}-{agregado_eq2} {eq2}"
    ]
    if agregado_eq1 > agregado_eq2:
        return eq1, logs
    elif agregado_eq2 > agregado_eq1:
        return eq2, logs
    else:
        ganador = eq1 if random.random() > 0.5 else eq2
        # Registrar penales como partido extra
        if partidos_log is not None:
            partidos_log.append({
                'Fase': etapa.capitalize() + " (Penales)",
                'Grupo': '',
                'Local': 'Penales',
                'Visitante': '',
                'Goles Local': ganador,
                'Goles Visitante': ''
            })
        logs.append(f"¡Empate en el global! Se define por penales: gana {ganador}")
        return ganador, logs



def ejecutar_simulacion(numero_simulacion):
    writer = pd.ExcelWriter(f'Simulador Liga 3\\Liga3_Simulacion_{numero_simulacion}.xlsx', engine='xlsxwriter')
    registros = []
    fase_finalistas = {}
    descensos = []
    
    # Fase Regular (corregido: recopila datos de todos los grupos)
    for grupo, eqs in grupos.items():
        tabla = simular_grupo(eqs)
        tabla.to_excel(writer, sheet_name=f'{grupo}_Regular', index=False)
        fase_finalistas[grupo] = tabla.iloc[:4]['Equipo'].tolist()  # Top 4 de cada grupo
        descensos.append(tabla.iloc[-1]['Equipo'])  # Último de cada grupo

    # Fase Final (corregido: escritura única en Excel)
    fase_final_equipos = [team for teams in fase_finalistas.values() for team in teams]
    random.shuffle(fase_final_equipos)
    grupos_fase_final = {f'Grupo_{chr(65+i)}': fase_final_equipos[i*4:(i+1)*4] for i in range(4)}

    df_fase_final = pd.DataFrame()
    for grupo, eqs in grupos_fase_final.items():
        tabla = simular_grupo(eqs)
        tabla.insert(0, 'Grupo', grupo)
        df_fase_final = pd.concat([df_fase_final, tabla], ignore_index=True)
    
    df_fase_final.to_excel(writer, sheet_name='Fase Final', index=False)  # Fuera del loop

    # Playoffs (corregido: usa datos de la fase final)
    df_acumulada = df_fase_final.sort_values(
        by=['Puntos', 'DG', 'GF'], 
        ascending=False
    ).reset_index(drop=True)

    # Cuartos de final (corregido: selección desde fase final)
    llaves = [
        (df_fase_final[df_fase_final['Grupo'] == 'Grupo_A'].iloc[0]['Equipo'], 
         df_fase_final[df_fase_final['Grupo'] == 'Grupo_B'].iloc[1]['Equipo']),
        (df_fase_final[df_fase_final['Grupo'] == 'Grupo_B'].iloc[0]['Equipo'], 
         df_fase_final[df_fase_final['Grupo'] == 'Grupo_A'].iloc[1]['Equipo']),
        (df_fase_final[df_fase_final['Grupo'] == 'Grupo_C'].iloc[0]['Equipo'], 
         df_fase_final[df_fase_final['Grupo'] == 'Grupo_D'].iloc[1]['Equipo']),
        (df_fase_final[df_fase_final['Grupo'] == 'Grupo_D'].iloc[0]['Equipo'], 
         df_fase_final[df_fase_final['Grupo'] == 'Grupo_C'].iloc[1]['Equipo'])
    ]
    
    semifinalistas = []
    for i, (eq1, eq2) in enumerate(llaves, 1):
        ganador, logs = simular_llave(eq1, eq2, df_acumulada, 'cuartos')
        registros.extend([f"Llave {i}:"] + logs)
        semifinalistas.append(ganador)
    
    # Semifinales (corregido: emparejamiento cruzado)
    finalistas = []
    for i in range(0, 4, 2):
        ganador, logs = simular_llave(semifinalistas[i], semifinalistas[i+1], df_acumulada, 'semifinal')
        registros.extend([f"Semifinal {(i//2)+1}:"] + logs)
        finalistas.append(ganador)
    
    # Final (corregido: formato oficial)
    campeon, logs = simular_llave(finalistas[0], finalistas[1], df_acumulada, 'final')
    registros.extend(["\n🔥 Gran Final 🔥"] + logs + [f"\n🏆 CAMPEÓN: {campeon}", f"🥈 SUBCAMPEÓN: {finalistas[1 if campeon == finalistas[0] else 0]}"])

    # Descensos (corregido: registro completo)
    registros.append("\n⏬ DESCENSOS ⏬")
    registros.extend([f"Desciende de {grupo}: {eq}" for grupo, eq in zip(grupos.keys(), descensos)])
    
    pd.DataFrame({'Evento': registros}).to_excel(writer, sheet_name='Playoffs', index=False)
    writer.close()


# Simular una temporada
ejecutar_simulacion(1)