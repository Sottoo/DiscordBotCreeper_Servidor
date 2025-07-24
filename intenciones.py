import re
import random

def respuesta_si_o_no_creeper(texto):
    # Detecta variantes: "si o no creeper", "creeper si o no", "sí o no creeper", etc.
    patron = re.compile(r"(?:^| )(.*?)(?:,?\s*)?(si[íi]?\s*o\s*no)[\s,;:¿?¡!]*(creeper)?(?:\s+(.*))?$", re.IGNORECASE)
    match = patron.search(texto)
    if match:
        # Si hay texto después de 'si o no creeper', ese es el tema
        palabras_irrelevantes = [
            'debería', 'puedo', 'quiero', 'tengo que', 'podría', 'debo', 'hay que', 'sería', 'es mejor', 'es bueno', 'es malo', 'dejar', 'hacer', 'como', 'esta', 'está', 'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'mi', 'tu', 'su', 'me', 'te', 'lo', 'le', 'nos', 'vos', 'usted', 'ustedes', 'yo', 'tú', 'él', 'ella', 'ellos', 'ellas'
        ]
        def limpiar_tema(texto):
            texto = texto.strip(' ,¿?¡!\n\t')
            palabras = texto.split()
            palabras_filtradas = [p for p in palabras if p.lower() not in palabras_irrelevantes]
            return ' '.join(palabras_filtradas[:6])

        tema = None
        # Si hay grupo 4 (texto después de si o no creeper), ese es el tema
        if match.group(4) and match.group(4).strip():
            tema = limpiar_tema(match.group(4))
        # Si no, usar lo que está antes de si o no
        elif match.group(1) and match.group(1).strip():
            tema = limpiar_tema(match.group(1))
        respuestas_generales = [
            "Mmm... depende, ¿tú qué crees? 😏",
            "¡Obvio sí! (o tal vez no, quién sabe) 🤔",
            "No sé, pero seguro tú tienes la respuesta.",
            "Sí... o no... o tal vez. ¡Qué difícil decisión!",
            "Eso ni el oráculo lo sabe, pero yo digo que sí. O no. 🤪",
            "¡Sí! ...Ah, ¿no era no? Bueno, tú decides.",
            "No, pero sí. Pero no. Pero sí. ¿Quedó claro? 😂",
            "¿Por qué me pones en aprietos? Mejor decide tú.",
            "¿Quieres que decida por ti? ¡Sí! ...o no. 😜",
            "La respuesta es... redoble de tambores... ¡quizás! 🥁",
            "¿Sí o no? Yo digo sí, pero el Creeper dice BOOM.",
            "Eso depende... ¿hay diamantes de por medio?",
            "Sí, pero solo si me invitas a tu server de Minecraft.",
            "No sé, pero si explota, fue tu culpa.",
            "Sí, no, tal vez... ¿puedo elegir todas?",
            "¿Por qué no? Total, nadie lo va a recordar mañana.",
            "No, pero si lo preguntas otra vez, capaz que sí.",
            "Sí, pero solo si hay memes involucrados.",
            "No, pero sí, pero no, pero sí... esto es un bucle infinito.",
            "¿Sí o no? Mejor pregúntale al Ender Dragon.",
            "Sí, pero con lag. No, pero con bugs."
        ]
        respuestas_con_tema = [
            "Sobre {tema}... yo diría que sí, pero no me hagas mucho caso. 😏",
            "¿{tema}? ¡Obvio sí! (o tal vez no, quién sabe) 🤔",
            "Con respecto a {tema}, la respuesta es... ¡quizás! 🥁",
            "¿Quieres mi opinión sobre {tema}? Mejor decide tú, yo solo soy un bot. 🤖",
            "{tema.capitalize()}... sí, no, o tal vez. ¡Qué difícil decisión! 😅",
            "Si se trata de {tema}, yo digo sí, pero solo si hay Creepers cerca.",
            "¿{tema}? Eso ni el aldeano lo sabe, pero yo digo sí.",
            "Sobre {tema}, la respuesta oficial es: depende del clima en Minecraft.",
            "¿{tema}? Sí, pero solo si no explota nada.",
            "{tema.capitalize()}... sí, pero con bugs. No, pero con memes. Tú decides.",
            "¿{tema}? Mejor que decida el chat, yo solo hago ruido digital.",
            "Si {tema} implica diamantes, entonces sí. Si no, pues no sé.",
            "En el mundo de Minecraft, {tema} sería un sí... pero en la vida real, quién sabe.",
            "¿{tema}? Solo si el Ender Dragon lo aprueba.",
            "Sobre {tema}, mi respuesta es sí, pero con lag y mobs cerca.",
            "Si {tema} aparece en el chat, seguro es para decir sí y luego arrepentirse.",
            "¿{tema}? Yo digo sí, pero solo si hay memes y pan.",
            "{tema.capitalize()}... sí, pero solo si no hay Creepers detrás de ti.",
            "¿{tema}? Eso depende del server, pero yo voto sí por los diamantes.",
            "Si {tema} fuera un bloque, sería de tierra... así que sí, pero con estilo.",
            "Sobre {tema}, sí, pero solo si no es spoiler de la serie.",
            "¿{tema}? Sí, pero solo si no me funan por decirlo.",
            "{tema.capitalize()}... sí, pero solo si el clima está soleado en Minecraft.",
            "¿{tema}? Sí, pero solo si el bot no se buguea."
        ]
        if tema and tema.strip():
            respuesta = random.choice(respuestas_con_tema).format(tema=tema)
        else:
            respuesta = random.choice(respuestas_generales)
        return respuesta
    return None
