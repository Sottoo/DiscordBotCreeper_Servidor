import os
import discord
from discord.ext import commands

# Lee el token desde la variable de entorno DISCORD_TOKEN (Railway)
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  # Necesario para leer el contenido de los mensajes
intents.members = True  # Necesario para detectar nuevos miembros


bot = commands.Bot(command_prefix='!', intents=intents)

# Importar y registrar comandos personalizados
from comandos import setup_commands
setup_commands(bot)

# Importar y registrar comando quedijo
from leermensaje import setup_leermensaje
setup_leermensaje(bot)

# Integrar respuesta si o no creeper en el evento de mensajes
from intenciones import respuesta_si_o_no_creeper

# Integrar respuestas sobre el servidor de Minecraft
from intenciones_servidor import respuesta_servidor_minecraft

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Primero verificar si es una pregunta sobre el servidor de Minecraft
    respuesta_mc = await respuesta_servidor_minecraft(message.content)
    if respuesta_mc:
        await message.channel.send(respuesta_mc)
        return
    
    # Si no, verificar si es un "si o no creeper"
    respuesta = respuesta_si_o_no_creeper(message.content)
    if respuesta:
        await message.channel.send(respuesta)
    
    await bot.process_commands(message)

# Evento para dar la bienvenida a nuevos miembros
from bienvenida import send_welcome_message

@bot.event
async def on_member_join(member):
    await send_welcome_message(member)

# Cargar las extensiones de forma asíncrona al iniciar el bot
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    
    # Cargar extensión de reglas
    if 'reglas' not in bot.extensions:
        try:
            await bot.load_extension('reglas')
            print('Extensión "reglas" cargada correctamente.')
        except Exception as e:
            print(f'Error al cargar la extensión reglas: {e}')
    
    # Cargar extensión de estado del servidor
    if 'estado_servidor' not in bot.extensions:
        try:
            await bot.load_extension('estado_servidor')
            print('Extensión "estado_servidor" cargada correctamente.')
            
            # Iniciar el monitoreo manualmente después de cargar
            cog = bot.get_cog('EstadoServidor')
            if cog and not cog.monitorear_servidor.is_running():
                cog.monitorear_servidor.start()
                print('Monitoreo del servidor iniciado.')
        except Exception as e:
            print(f'Error al cargar la extensión estado_servidor: {e}')

bot.run(TOKEN)
