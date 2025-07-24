
from discord.ext import commands
from discord import Interaction

def setup_commands(bot):
    @bot.command()
    async def ip(ctx):
        """Muestra la IP del servidor de Minecraft."""
        await ctx.send("La IP del servidor es: 108.181.148.38:25572")

    @bot.command()
    async def mods(ctx):
        """Pregunta si usa CurseForge o no y responde diferente según la opción."""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("¿Usas **CurseForge** para tus mods? Responde con 'curseforge' o 'no'.")
        try:
            respuesta = await bot.wait_for('message', check=check, timeout=30)
        except Exception:
            await ctx.send("⏰ No respondiste a tiempo. Intenta de nuevo.")
            return

        if respuesta.content.lower() == 'curseforge':
            await ctx.send("Perfecto, aquí tienes el modpack recomendado para CurseForge: https://www.mediafire.com/file/detyagx6wrto3gd/Server_Toppo_2.zip/file ¡Disfruta tu experiencia!")
        elif respuesta.content.lower() == 'no':
            await ctx.send("Puedes instalar los mods manualmente desde aqui: https://www.mediafire.com/file/eu8y91zxzy2glcz/MODS_cliente_1.21.1_(2).zip/file. Si necesitas ayuda, pregunta a un admin o revisa el canal de tutoriales. ¡Diviértete!")
        else:
            await ctx.send("Respuesta no reconocida. Por favor responde solo 'curseforge' o 'no'.")
