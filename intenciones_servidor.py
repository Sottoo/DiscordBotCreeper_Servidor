import re
import random
import asyncio

# Importar mcstatus para verificar el estado del servidor
try:
    from mcstatus import JavaServer
    MCSTATUS_DISPONIBLE = True
except ImportError:
    MCSTATUS_DISPONIBLE = False

# Configuración del servidor
SERVIDOR_IP = "108.181.102.178"
SERVIDOR_PUERTO = 25587

# Patrones para detectar preguntas sobre el servidor
PATRONES_JUGADORES = [
    r"(?:creeper[,\s]*)?(?:cuant[oa]s?\s+(?:personas?|jugador(?:es)?|gente|players?)\s+(?:hay|están?|andan?|tiene[ns]?)\s+(?:en\s+)?(?:el\s+)?(?:server|servidor))",
    r"(?:creeper[,\s]*)?(?:qui[eé]n(?:es)?\s+(?:est[aá][ns]?|hay|andan?)\s+(?:en\s+)?(?:el\s+)?(?:server|servidor))",
    r"(?:creeper[,\s]*)?(?:hay\s+(?:alguien|gente|personas?|jugador(?:es)?)\s+(?:en\s+)?(?:el\s+)?(?:server|servidor))",
    r"(?:creeper[,\s]*)?(?:(?:el\s+)?(?:server|servidor)\s+(?:est[aá]|tiene)\s+(?:vac[ií]o|solo|lleno))",
    r"(?:creeper[,\s]*)?(?:qui[eé]n(?:es)?\s+(?:est[aá][ns]?|juega[ns]?)\s+(?:ahorita?|ahora|en este momento))",
    r"(?:creeper[,\s]*)?(?:(?:cu[aá]ntos?|qui[eé]nes?)\s+(?:est[aá][ns]?|hay)\s+(?:jugando|conectados?|online))",
    r"(?:creeper[,\s]*)?(?:(?:el\s+)?(?:server|servidor)\s+tiene\s+(?:gente|jugadores?|personas?))",
]

PATRONES_ESTADO = [
    r"(?:creeper[,\s]*)?(?:(?:el\s+)?(?:server|servidor)\s+(?:est[aá]|anda)\s+(?:abierto|prendido|encendido|online|activo))",
    r"(?:creeper[,\s]*)?(?:(?:el\s+)?(?:server|servidor)\s+(?:est[aá]|anda)\s+(?:cerrado|apagado|offline|muerto))",
    r"(?:creeper[,\s]*)?(?:(?:puedo|se puede)\s+(?:entrar|jugar|conectar(?:me)?)\s+(?:al\s+)?(?:server|servidor))",
    r"(?:creeper[,\s]*)?(?:(?:est[aá]|anda)\s+(?:el\s+)?(?:server|servidor)\s+(?:abierto|prendido|online))",
    r"(?:creeper[,\s]*)?(?:(?:c[oó]mo\s+(?:est[aá]|anda)|qu[eé]\s+(?:onda|pedo)\s+con)\s+(?:el\s+)?(?:server|servidor))",
    r"(?:creeper[,\s]*)?(?:(?:el\s+)?(?:server|servidor)\s+(?:funciona|sirve|jala))",
]

PATRONES_HORARIO = [
    r"(?:creeper[,\s]*)?(?:(?:a\s+qu[eé]\s+hora|cu[aá]ndo)\s+(?:abre|cierra|prende|apaga)\s+(?:el\s+)?(?:server|servidor))",
    r"(?:creeper[,\s]*)?(?:(?:cu[aá]l\s+es\s+)?(?:el\s+)?horario\s+(?:del\s+)?(?:server|servidor))",
    r"(?:creeper[,\s]*)?(?:(?:el\s+)?(?:server|servidor)\s+(?:a\s+qu[eé]\s+hora)\s+(?:abre|cierra))",
    r"(?:creeper[,\s]*)?(?:hasta\s+qu[eé]\s+hora\s+(?:est[aá]|anda)\s+(?:el\s+)?(?:server|servidor))",
]


def detectar_intencion_servidor(texto):
    """
    Detecta si el mensaje es una pregunta sobre el servidor de Minecraft.
    Retorna: 'jugadores', 'estado', 'horario' o None
    """
    texto_lower = texto.lower().strip()
    
    # Verificar patrones de jugadores
    for patron in PATRONES_JUGADORES:
        if re.search(patron, texto_lower, re.IGNORECASE):
            return 'jugadores'
    
    # Verificar patrones de estado
    for patron in PATRONES_ESTADO:
        if re.search(patron, texto_lower, re.IGNORECASE):
            return 'estado'
    
    # Verificar patrones de horario
    for patron in PATRONES_HORARIO:
        if re.search(patron, texto_lower, re.IGNORECASE):
            return 'horario'
    
    return None


async def obtener_info_servidor():
    """
    Obtiene información del servidor de Minecraft.
    Retorna: (online, jugadores, max_jugadores, lista_jugadores, latencia)
    """
    if not MCSTATUS_DISPONIBLE:
        return None, 0, 0, [], 0
    
    try:
        servidor = JavaServer(SERVIDOR_IP, SERVIDOR_PUERTO)
        loop = asyncio.get_event_loop()
        status = await loop.run_in_executor(None, servidor.status)
        
        jugadores_online = status.players.online
        max_jugadores = status.players.max
        latencia = status.latency
        
        # Obtener lista de nombres de jugadores
        lista_jugadores = []
        if status.players.sample:
            lista_jugadores = [player.name for player in status.players.sample]
        
        return True, jugadores_online, max_jugadores, lista_jugadores, latencia
    except Exception:
        return False, 0, 0, [], 0


def generar_respuesta_jugadores(online, jugadores, max_jugadores, lista_jugadores):
    """Genera una respuesta sobre los jugadores conectados"""
    
    if not online:
        respuestas_offline = [
            "El servidor está apagado ahorita, no hay nadie conectado. 💤",
            "Nel, el server está offline. Vuelve más tarde. 😴",
            "No hay nadie porque el servidor está apagado. Toca esperar. ⏰",
            "Server muerto... bueno, apagado. Regresa cuando abra. 🔴",
        ]
        return random.choice(respuestas_offline)
    
    if jugadores == 0:
        respuestas_vacio = [
            "El servidor está encendido pero solito... ¡Necesitamos gente! Hay **0/{max}** jugadores. 🏜️",
            "Nadie está conectado ahorita. El server está esperando por ti. **0/{max}** 😢",
            "Cero jugadores... el servidor se siente solo. ¡Únete! **0/{max}** 🌵",
            "Server vacío, momento perfecto para minear sin que te roben los diamantes. **0/{max}** 💎",
        ]
        return random.choice(respuestas_vacio).format(max=max_jugadores)
    
    elif jugadores == 1:
        nombre = lista_jugadores[0] if lista_jugadores else "alguien"
        respuestas_uno = [
            f"Solo está **{nombre}** conectado. ¡Únete para hacerle compañía! 👤",
            f"Hay **1/{max_jugadores}** jugador: **{nombre}**. ¡No lo dejes solo! 🎮",
            f"**{nombre}** anda jugando solito. ¡Métete a echar paro! 💪",
        ]
        return random.choice(respuestas_uno)
    
    else:
        if lista_jugadores:
            nombres = ", ".join([f"**{n}**" for n in lista_jugadores])
            respuestas_varios = [
                f"Hay **{jugadores}/{max_jugadores}** jugadores conectados:\n{nombres} 🎮",
                f"¡El server tiene vida! **{jugadores}/{max_jugadores}** jugando:\n{nombres} 🎉",
                f"Actualmente hay **{jugadores}** de **{max_jugadores}** jugadores:\n{nombres} ⛏️",
            ]
        else:
            respuestas_varios = [
                f"Hay **{jugadores}/{max_jugadores}** jugadores conectados ahorita. 🎮",
                f"¡El server tiene gente! **{jugadores}/{max_jugadores}** jugadores online. 🎉",
                f"Actualmente hay **{jugadores}** de **{max_jugadores}** jugadores. ⛏️",
            ]
        return random.choice(respuestas_varios)


def generar_respuesta_estado(online, jugadores, max_jugadores):
    """Genera una respuesta sobre el estado del servidor"""
    
    if online:
        respuestas_online = [
            f"¡Sí! El servidor está **encendido** y listo para jugar. 🟢\nHay **{jugadores}/{max_jugadores}** jugadores conectados.",
            f"El server está **online** y funcionando. 🟢\n👥 **{jugadores}/{max_jugadores}** jugadores ahorita.",
            f"¡El servidor anda **prendido**! Puedes conectarte. 🟢\nGente conectada: **{jugadores}/{max_jugadores}**",
            f"Sí se puede entrar, el server está **activo**. 🟢\nJugadores: **{jugadores}/{max_jugadores}**",
        ]
        return random.choice(respuestas_online)
    else:
        respuestas_offline = [
            "El servidor está **apagado** ahorita. 🔴\nHorario: **2:00 PM - 2:00 AM**",
            "Nel, el server está **offline**. 🔴\nVuelve en horario: **2:00 PM - 2:00 AM**",
            "No se puede entrar, el servidor está **cerrado**. 🔴\nAbre de **2:00 PM a 2:00 AM**",
            "Server **apagado**, toca esperar. 🔴\nHorario normal: **2:00 PM - 2:00 AM**",
        ]
        return random.choice(respuestas_offline)


def generar_respuesta_horario():
    """Genera una respuesta sobre el horario del servidor"""
    
    respuestas = [
        "**📋 Horario del servidor:**\n🟢 **Abre:** 2:00 PM\n🔴 **Cierra:** 2:00 AM\n\n¡12 horas para viciarte! ⏰",
        "El server está disponible de **2:00 PM a 2:00 AM** todos los días. 🕐",
        "**Horario:**\n• Apertura: **2:00 PM** 🟢\n• Cierre: **2:00 AM** 🔴\n\n¡No llegues tarde! 🎮",
        "Abrimos a las **2 de la tarde** y cerramos a las **2 de la mañana**. 12 horas de diversión. ⛏️",
    ]
    return random.choice(respuestas)


async def respuesta_servidor_minecraft(texto):
    """
    Procesa el texto y retorna una respuesta si es una pregunta sobre el servidor.
    Retorna: respuesta (str) o None si no es una pregunta sobre el servidor
    """
    intencion = detectar_intencion_servidor(texto)
    
    if intencion is None:
        return None
    
    if intencion == 'horario':
        return generar_respuesta_horario()
    
    # Para jugadores y estado necesitamos consultar el servidor
    online, jugadores, max_jugadores, lista_jugadores, latencia = await obtener_info_servidor()
    
    if intencion == 'jugadores':
        return generar_respuesta_jugadores(online, jugadores, max_jugadores, lista_jugadores)
    
    elif intencion == 'estado':
        return generar_respuesta_estado(online, jugadores, max_jugadores)
    
    return None
