Para qué se utiliza cada archivo:

- Datos totales 2023: 
Contiene las estadisticas generales de todos los jugadores de la Liga 1 peruana en 2023, con las columnas en ingles ordenadas por equipo.
Se utiliza para
 Obtener promedios generales por estadística de la liga del año pasado por cantidad de minutos de juego.

- Datos totales Alianza Lima 2023: 
Se utiliza para
 Obtener promedios de los jugadores de Alianza Lima que estuvieron en la plantilla el año pasado.
 Obtener promedios por posicion de jugadores de Alianza Lima utilizando los datos de ALIANZA LIMA 2024.

- Datos totales 2024: 
Contiene las estadisticas generales de todos los jugadores de la Liga 1 peruana en 2024 hasta la última jornada jugada, con las columnas en ingles ordenadas por equipo, sin incluir a Alianza Lima.
Se utiliza para
 Obtener promedios generales de la liga del año pasado por cantidad de minutos de juego
 Obtener estadisticas de los rivales para hacer la previa de los partidos

- ALIANZA LIMA 2024: Contiene los datos en resumen de la plantilla de Alianza Lima para esta temporada, contiene datos relevantes como los nombres, dorsal, posicion, y totales.
Se utiliza de tabla maestra Jugadores, con clave en la columna Jugador.

- Resumen_AL_Jugadores: Contiene los datos recopilados de todos los jugadores para cada jornada individual jugada.

- Resumen_AL_Oponentes: Contiene los datos recopilados de todos los jugadores oponentes para cada jornada individual jugada, contiene la posicion del oponente para hacer calculos de promedio con los datos totales de 2024, solo matchea el nombre del jugador.


-------------------------------------

df_jugadores = ALIANZA LIMA 2024.xlsx
df_datos = Resumen_AL_Jugadores.xlsx

Agrupacion de estadisticas
-----
Concentración (para todos los jugadores):
["fouls"; "Faltas"]
["wasFouled"; "Recibió falta"]
["totalOffside"; "Fuera de juego"]
["dispossessed"; "Desposesiones"]
["errorLeadToAShot"; "Error que lleva a tiro"]
["penaltyConceded"; "Penal concedido"]

-----
Juego básico (para todos los jugadores):
["substitute"; "Suplente"]
["minutesPlayed"; "Minutos jugados"]
["goals" ; "Goles" ]
["goalAssist"; "Asistencias"]
["touches"; "Toques de balón"]
["possesionLostCtrl"; "Control de posesión perdida"]
["totalPass"; "Pases totales"]
["accuratePass"; "Pases precisos"]
["totalLongBalls"; "Pases largos totales"]
["accurateLongBalls; "Pases largos precisos"]
["bigChanceCreated ; "Gran oportunidad de gol creada"]
["bigChanceMissed"; "Gran oportunidad de gol fallada"]
["penaltyWon"; "Penal ganado"]
["penaltyMiss"; "Penal fallado"]


Resumen de Jugador una vez es seleccionado

Posiciones (POS_1 , POS_2 , POS_3 )
-------------------------------------------------------------------------
Ángelo Campos: POR
Franco Saravia: POR
Ángel De la Cruz: POR
Portero: {
POR; Portero; G ; 0  -> ["punches"; "Salidas con puños"];
			["goodHighClaim"; "Centros atrapados"]
			["accurateKeeperSweeper"; "Salidas del área con éxito"]
			["totalKeeperSweeper"; "Salidas del área"]
			["savedShotsFromInsideTheBox"; "Salvadas dentro del área"]
			["saves"; "Salvadas"]
}
-------------------------------------------------------------------------
Renzo Garces: DFC | LIB |
Yordi Vílchez: DFC | DFD
Carlos Zambrano: DFC | LIB | DFD

Juan Freytes : DFI | DFC | LI
Jiovany Ramos: DFC | DFD | LD

Sebastian Aranda: LI | CRI
Marco Huaman: LD | CRD | DFD
Nicolas Amasifuen: LI | CRI
Ricardo Lagos: LI | CRI | VLI

Defensa: {
{
DFI; Defensa izquierdo; D ; 0 
DFD; Defensa derecho; D ; 0
DFC; Defensa central; D ; 0
LIB; Defensa libero; D ; 0 } -> ["aerialLost";"Duelos Aereos perdidos"]
				["aerialWon";"Duelos Aereos ganados"]
				["duelLost";"Duelos perdidos"]
				["duelWon";"Duelos ganados"]
				["challengeLost";"Desafios perdidos"]
				["totalClearance";"Despejes totales"]
				["interceptionWon";"Intercepciones ganadas"]
				["totalTackle";"Entradas totales"]
				["outfielderBlock";"Bloqueos de jugadores de campo"]
{
LD; Lateral derecho; D ; M
LI; Lateral izquierdo ; D ; M
CRI; Carrilero izquierdo; D ; M 
CRD; Carrilero derecho; D ; M }      -> ["aerialLost";"Duelos Aereos perdidos"]
					["aerialWon";"Duelos Aereos ganados"]
					["duelLost";"Duelos perdidos"]
					["duelWon";"Duelos ganados"]
					["challengeLost";"Desafios perdidos"]
					["totalClearance";"Despejes totales"]
					["interceptionWon";"Intercepciones ganadas"]
					["totalTackle";"Entradas totales"]
					["totalCross"; "Centros totales"]
				   	["accurateCross; "Centros precisos"]
}
-------------------------------------------------------------------------

Aldair Fuentes: MCD | DFC | MCC
Jesús Castillo: MCD | MCC | VLX
Adrián Arregui: MCD | MCC | VLX
Axel Moyano: MCC | VLX

Jhamir D´Arrigo: CRI | EXI | VLI
Franco Zanelatto: VLI | EXI | EXD

Sebastián Rodríguez: VLX | MCO
Catriel Cabellos: VLX | CRD | VLD
Gabriel Costa: VLX | MCO | DLC
Christian Neira: MCO | VLX

Kevin Serna: EXD | CRD | SDC

Mediocampista: {
{ MCD; Mediocampista central def. ; D ; M
MCC; Mediocampista contencion ; M ; D }	     -> ["aerialLost";"Duelos Aereos perdidos"]
						["aerialWon";"Duelos Aereos ganados"]
						["duelLost";"Duelos perdidos"]
						["duelWon";"Duelos ganados"]
						["challengeLost";"Desafios perdidos"]
						["totalClearance";"Despejes totales"]
						["interceptionWon";"Intercepciones ganadas"]
						["totalTackle";"Entradas totales"]
						["outfielderBlock";"Bloqueos de jugadores de campo"]

{ VLX; Volante mixto; M ; 0
VLD; Volante derecho; M ; 0
VLI; Volante izquierdo ; M ; 0 } 	     -> ["aerialLost";"Duelos Aereos perdidos"]
						["aerialWon";"Duelos Aereos ganados"]
						["duelLost";"Duelos perdidos"]
						["duelWon";"Duelos ganados"]
						["challengeLost";"Desafios perdidos"]
						["outfielderBlock";"Bloqueos de jugadores de campo"]
						["interceptionWon";"Intercepciones ganadas"]
						["totalCross"; "Centros totales"]
				   		["accurateCross; "Centros precisos"]
						["shotOffTarget"; "Tiros fuera"]
						["onTargetScoringAttempt"; "Tiro al arco"]
						["blockedScoringAttempt"; "Tiro bloqueado"]
						["totalContest"; "Regates totales"]
						["wonContest"; "Regates con éxito"]
						["keyPass"; "Pases clave"]

{ MCO; Mediocampista enganche; M ; F }	     -> ["interceptionWon";"Intercepciones ganadas"]
						["totalCross"; "Centros totales"]
				   		["accurateCross; "Centros precisos"]
						["shotOffTarget"; "Tiros fuera"]
						["onTargetScoringAttempt"; "Tiro al arco"]
						["blockedScoringAttempt"; "Tiro bloqueado"]
						["duelLost";"Duelos perdidos"]
						["duelWon";"Duelos ganados"]
						["totalContest"; "Regates totales"]
						["wonContest"; "Regates con éxito"]
						["keyPass"; "Pases clave"]
{ EXI; Extremo izquierdo ; F ; M
EXD; Extremo derecho; F ; M }	     -> ["totalCross"; "Centros totales"]
				   	["accurateCross; "Centros precisos"]
					["shotOffTarget"; "Tiros fuera"]
					["onTargetScoringAttempt"; "Tiro al arco"]
					["blockedScoringAttempt"; "Tiro bloqueado"]
					["hitWoodwork"; "Tiro al poste"]
					["duelLost";"Duelos perdidos"]
					["duelWon";"Duelos ganados"]
					["totalContest"; "Regates totales"]
					["wonContest"; "Regates con éxito"]
					["keyPass"; "Pases clave"]
}
-------------------------------------------------------------------------
Delantero: {
{ SDC; Segundo delantero centro; F ; 0
DLC; Delantero centro; F ; 0 } 	     	     -> ["shotOffTarget"; "Tiros fuera"]
						["onTargetScoringAttempt"; "Tiro al arco"]
						["blockedScoringAttempt"; "Tiro bloqueado"]
						["hitWoodwork"; "Tiro al poste"]
						["aerialLost";"Duelos Aereos perdidos"]
						["aerialWon";"Duelos Aereos ganados"]
						["duelLost";"Duelos perdidos"]
						["duelWon";"Duelos ganados"]
						["totalContest"; "Regates totales"]
						["wonContest"; "Regates con éxito"]
}
