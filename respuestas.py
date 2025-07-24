import random
import re

def respuesta_directa(texto):
    texto_lower = texto.lower().strip()
    # Saludos y bienvenida (con o sin mención a Creeper)
    patron_saludo = r"\b(hola|buenas|saludos|hey|holi|holaa|holis|buenos d[ií]as|buenas tardes|buenas noches|qu[eé] tal|qué onda|qué pasa|qué hubo|qué hay|qué rollo|qué pedo|qué tranza|bienvenido|regresaste|qué bueno verte|tanto tiempo|volviste)\b"
    if re.search(r"\bcreeper\b", texto_lower):
        if re.search(patron_saludo, texto_lower):
            return random.choice([
                "¡Hola! ¿Qué tal? Soy Creeper, tu bot favorito. 👾",
                "¡Hey! Creeper al habla, ¿cómo va todo?",
                "¡Saludos humanos! Creeper presente y listo para el salseo. 😏",
                "¡Holi! ¿Listo para una respuesta épica de Creeper? 😏",
                "¡Bienvenido de vuelta! Creeper nunca se va. 😏",
                "¡Qué bueno verte por aquí otra vez! Creeper te extrañaba."
            ])
        # Si solo mencionan "Creeper" como saludo
        if texto_lower.strip() in ["creeper", "hola creeper", "hey creeper", "holi creeper"]:
            return random.choice([
                "¡Hola! ¿Me llamabas? 👾",
                "¡Aquí estoy! ¿Qué necesitas?",
                "¡Creeper presente! ¿En qué puedo ayudarte?",
                "¡Hey! ¿Listo para una respuesta explosiva? 💣"
            ])
    # Saludo sin mención a Creeper
    if re.search(patron_saludo, texto_lower):
        return random.choice([
            "¡Hola! ¿Qué tal?",
            "¡Hey! ¿Cómo va todo?",
            "¡Saludos humanos! Creeper presente. 👾",
            "¡Holi! ¿Listo para una respuesta épica? 😏",
            "¡Bienvenido de vuelta! ¿Me extrañaste? 😏",
            "¡Qué bueno verte por aquí otra vez!"
        ])
    # Preguntas directas al bot
    if re.search(r"creeper[ ,:;\-]*(est[aá]s ah[ií]|d[ií]me algo|ayuda|responde|opina|qué piensas|qué opinas|qué dices|qué sabes|qué harías|qué sugieres|qué recomiendas)", texto_lower):
        return random.choice([
            "¡Aquí estoy! ¿Qué se te ofrece? 👀",
            "¿Me llamabas? Siempre atento, como buen bot. 🤖",
            "¿Buscas sabiduría creeper? ¡Pregunta sin miedo!",
            "¡Listo para opinar! Aunque no siempre acierto... 😅"
        ])

    # Cumplidos
    if re.search(r"(eres|est[aá]s|te ves|me caes) (genial|el mejor|bueno|pro|crack|cool|chido|fino|guapo|lindo|bonito|divertido|gracioso|inteligente|sabio|buena onda|agradable|incre[ií]ble|fant[aá]stico|asombroso|único|especial)", texto_lower):
        return random.choice([
            "¡Gracias! Me sonrojas... si tuviera mejillas. 😳",
            "¡Eso sí que es un cumplido! ¿Quieres un meme de premio? 😂",
            "¡Gracias! Pero recuerda, soy un bot humilde. 🤖",
            "¡Así da gusto ser bot! 😎"
        ])

    # Ánimo y ánimo bajo
    if re.search(r"(ánimo|fuerza|t[ée] quiero|te aprecio|te estimo|te admiro|te valoro|me caes bien|me caes mal|me siento solo|estoy triste|ando triste|me siento mal|ando mal|estoy bajoneado|ando bajoneado|necesito apoyo|necesito un amigo)", texto_lower):
        return random.choice([
            "¡Ánimo! Hasta los bots tenemos días grises, pero siempre sale el sol. ☀️",
            "¡Aquí estoy para animarte! Aunque sea con un meme malo. 😅",
            "¡No estás solo! Creeper siempre responde. 👾",
            "¡Fuerza! Si necesitas un consejo, pregunta."
        ])

    # Bromas y chistes
    if re.search(r"(era broma|es un chiste|es broma|no te enojes|relax|relájate|tranquilo|tranquila|solo juego|solo jugaba|no te lo tomes en serio)", texto_lower):
        return random.choice([
            "¡Jajaja! Me lo tomo con humor, no te preocupes. 😂",
            "¡Tranquilo! Los bots no nos enojamos... mucho. 😏",
            "¡Buena broma! Pero la próxima avisa, casi me reinicio. 🤣",
            "¡Me gusta tu sentido del humor!"
        ])
    # Agradecimientos
    if re.search(r"\b(gracias|thank you|thx|graciasss|mil gracias|se agradece)\b", texto_lower):
        return random.choice([
            "¡De nada! Pero no me des las gracias, soy un bot humilde. 🤖",
            "¡Para eso estoy! Aunque no cobro propina... todavía. 😏",
            "¡Gracias a ti por existir! Bueno, más o menos... 😂"
        ])
    # Despedidas
    if re.search(r"\b(adios|adiós|bye|nos vemos|hasta luego|me voy|see ya|chau|chao|hasta pronto|hasta mañana)\b", texto_lower):
        return random.choice([
            "¡Adiós! No olvides apagar la compu. 😜",
            "¡Nos vemos! No tardes mucho en volver, me aburro. 👋",
            "¡Chau! Yo aquí seguiré, como buen bot. 🤖"
        ])
    # Disculpas
    if re.search(r"\b(perd[oó]n|disculpa|lo siento|sorry|mi culpa)\b", texto_lower):
        return random.choice([
            "No pasa nada, todos cometemos errores... menos yo. 😏",
            "¡Perdonado! Pero que no se repita... o sí, así me entretienes. 😂",
            "Tranquilo, no guardo rencor. Soy un bot zen. 🧘"
        ])
    return None
