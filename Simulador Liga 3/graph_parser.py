import re

def extraer_ganador_linea(lineas):
    for linea in lineas:
        m = re.search(r'gana (.+)', linea, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    
    agregado_line = next((l for l in lineas if l.lower().startswith('agregado')), None)
    if agregado_line:
        partes = re.split(r'(\d+)-(\d+)', agregado_line)
        if len(partes) >= 4:
            equipo1 = partes[0].replace('Agregado:', '').strip()
            goles1 = int(partes[1])
            goles2 = int(partes[2])
            equipo2 = partes[3].strip()
            return equipo1 if goles1 > goles2 else equipo2
    return None

def extraer_equipos_de_linea(linea):
    m = re.search(r': (.+?) (\d+)-(\d+) (.+)', linea)
    if m:
        return m.group(1).strip(), m.group(4).strip()
    return None, None


def generar_dot_desde_log(playoffs_log):
    dot_lines = [
        'digraph torneo {',
        'rankdir=LR;',  # Dirección de los nodos de izquierda a derecha
        'node [shape=box, style=filled, fillcolor=lightgray];',  # Cambié a ellipse para hacer los bordes ovalados
        'graph [ratio=fill, size="12,10"];'
    ]
    llaves_ganadores = {}

    conexiones_entradas = set()
    conexiones_salidas = set()
    nodos_creados = set()

    i = 0
    while i < len(playoffs_log):
        linea = playoffs_log[i].strip()
        llave_match = re.match(r'(Llave|Semifinal|Final) ?(\d*)[:]*', linea, re.IGNORECASE)
        if llave_match:
            llave_tipo = llave_match.group(1).lower()
            llave_num = llave_match.group(2)
            llave_id = f"{llave_tipo.capitalize()} {llave_num}".strip()

            segmento = []
            j = i + 1
            while j < len(playoffs_log) and playoffs_log[j].strip() != '' and not re.match(r'(Llave|Semifinal|Final) ?(\d*)[:]*', playoffs_log[j], re.IGNORECASE):
                segmento.append(playoffs_log[j].strip())
                j += 1

            equipos = []
            for l in segmento:
                if 'Ida' in l or 'Vuelta' in l:
                    e1, e2 = extraer_equipos_de_linea(l)
                    if e1 and e2:
                        equipos.extend([e1, e2])
            equipos = list(dict.fromkeys(equipos))

            ganador = extraer_ganador_linea(segmento)
            if not ganador and equipos:
                ganador = equipos[0]

            llaves_ganadores[llave_id] = ganador

            dot_lines.append(f'"{llave_id}" [label="{ganador}", fillcolor=lightblue, style=filled];')
            nodos_creados.add(llave_id)
            for eq in equipos:
                dot_lines.append(f'"{eq}" -> "{llave_id}";')
                conexiones_salidas.add(eq)
                conexiones_entradas.add(llave_id)
                nodos_creados.add(eq)

            i = j
        else:
            i += 1

    conexiones = {
        'Llave 1': 'Semifinal 1',
        'Llave 2': 'Semifinal 1',
        'Semifinal 2': 'Final',
        'Semifinal 1': 'Final',
        'Llave 3': 'Semifinal 2',
        'Llave 4': 'Semifinal 2',
    }

    semifinales = {'Semifinal 2': [], 'Semifinal 1': []}
    for llave, semifinal in conexiones.items():
        ganador = llaves_ganadores.get(llave)
        if ganador:
            semifinales[semifinal].append(ganador)

    # Agregar subgrafo para controlar la posición de Semifinal 1 y Semifinal 2
    dot_lines.append('subgraph cluster_semifinales {')
    dot_lines.append('rank=same;')  # Asegura que los nodos dentro de este subgrafo estén alineados en la misma fila
    dot_lines.append('style=invis;')  # Hace invisible el borde del subgrafo
    for semifinal in ['Semifinal 1', 'Semifinal 2']:
        if semifinales[semifinal]:
            dot_lines.append(f'"{semifinal}" [label="{", ".join(semifinales[semifinal])}", fillcolor=lightblue, style=filled];')
            nodos_creados.add(semifinal)
            for equipo in semifinales[semifinal]:
                dot_lines.append(f'"{equipo}" -> "{semifinal}";')
                conexiones_salidas.add(equipo)
                conexiones_entradas.add(semifinal)
    dot_lines.append('}')


    # Conexión entre semifinales y final
    if semifinales['Semifinal 1']:
        dot_lines.append(f'"Semifinal 1" -> "Final";')
        conexiones_salidas.add('Semifinal 1')
        conexiones_entradas.add('Final')
    if semifinales['Semifinal 2']:
        dot_lines.append(f'"Semifinal 2" -> "Final";')
        conexiones_salidas.add('Semifinal 2')
        conexiones_entradas.add('Final')

    campeon = llaves_ganadores.get('Final', 'Campeón')
    dot_lines.append(f'"Final" [label="{campeon} - CAMPEÓN", fillcolor=gold, style=filled, shape=doubleoctagon];')
    nodos_creados.add('Final')

    dot_lines.append('}')

    # Limpiar nodos huérfanos
    dot_code = '\n'.join(dot_lines)
    nodos_a_eliminar = []
    for nodo in nodos_creados:
        if nodo not in conexiones_salidas and nodo not in conexiones_entradas:
            nodos_a_eliminar.append(nodo)

    for nodo in nodos_a_eliminar:
        dot_code = re.sub(rf'\n\s*"{re.escape(nodo)}"\s*\[.*?\];', '', dot_code)

    return dot_code
