
from discord.ext import commands
import random

def setup_leermensaje(bot):
    import re

    import json
    import os

    def clasificar_mensaje(texto):
        patrones = {
            'saludo': r"\b(hola|buenas|saludos|hey|hello|hi)\b",
            'despedida': r"\b(adios|bye|nos vemos|hasta luego|chao|me voy)\b",
            'pregunta': r"\?",
            'broma': r"\b(broma|chiste|jaja|xd|jeje|jajaja|lol)\b",
            'queja': r"\b(queja|no me gusta|odio|molesto|enojo|enojado|fastidia|molesta)\b",
            'agradecimiento': r"\b(gracias|thank you|te lo agradezco|muy amable)\b",
            'feliz': r"\b(feliz|contento|alegre|genial|fantástico|maravilloso|bien)\b",
            'triste': r"\b(triste|deprimido|mal|lloro|llorando|pena)\b",
            'enojado': r"\b(enojado|molesto|furioso|rabia|enojo)\b",
            'spoiler': r"\b(spoiler)\b",
            'meme': r"\b(meme|memazo)\b",
            'reto': r"\b(reto|challenge)\b",
            'indirecta': r"\b(indirecta)\b",
            'secreto': r"\b(secreto|confidencial)\b",
            'originalidad': r"\b(original|creativo|único)\b",
            'clima': r"\b(clima|lluvia|soleado|nublado|calor|frío|tormenta)\b",
            'tiempo': r"\b(tiempo|aburrido|esperando|pasar el rato|matando el tiempo|sin hacer nada)\b",
        }
        clasificaciones = []
        for tema, patron in patrones.items():
            if re.search(patron, texto, re.IGNORECASE):
                clasificaciones.append(tema)
        if not clasificaciones:
            clasificaciones.append('otro')
        return clasificaciones

    # Cargar respuestas desde JSON externo
    ruta_respuestas = os.path.join(os.path.dirname(__file__), 'respuestas_creeper.json')
    with open(ruta_respuestas, 'r', encoding='utf-8') as f:
        respuestas_por_tipo = json.load(f)

    ruta_sarcasticas = os.path.join(os.path.dirname(__file__), 'frases_sarcasticas.json')
    with open(ruta_sarcasticas, 'r', encoding='utf-8') as f:
        frases_sarcasticas = json.load(f)

    @bot.listen('on_message')
    async def responde_que_opinas_creeper(message):
        if message.author.bot:
            return
        contenido = message.content.lower()
        if "que opinas creeper" in contenido:
            async for msg in message.channel.history(limit=2):
                if msg.id != message.id:
                    ultimo = msg
                    break
            else:
                await message.channel.send("No encontré ningún mensaje anterior para comentar.")
                return
            clasificacion = clasificar_mensaje(ultimo.content)
            # Elegir la respuesta según la primera clasificación encontrada
            tipo = clasificacion[0] if clasificacion else 'otro'
            if tipo in respuestas_por_tipo:
                respuesta = random.choice(respuestas_por_tipo[tipo])
            else:
                respuesta = random.choice(frases_sarcasticas)
            await message.channel.send(respuesta)
