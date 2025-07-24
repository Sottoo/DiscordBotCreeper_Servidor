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

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    respuesta = respuesta_si_o_no_creeper(message.content)
    if respuesta:
        await message.channel.send(respuesta)
    await bot.process_commands(message)

# Evento para dar la bienvenida a nuevos miembros
from bienvenida import send_welcome_message

@bot.event
async def on_member_join(member):
    await send_welcome_message(member)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

# Cargar la extensión de reglas de forma asíncrona al iniciar el bot
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    # Solo cargar la extensión si no está cargada
    if 'reglas' not in bot.extensions:
        try:
            await bot.load_extension('reglas')
            print('Extensión "reglas" cargada correctamente.')
        except Exception as e:
            print(f'Error al cargar la extensión: {e}')

bot.run(TOKEN)
