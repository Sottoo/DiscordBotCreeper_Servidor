import discord
from discord.ext import commands

# ID del canal donde se publicarán las reglas
RULES_CHANNEL_ID = 1397708607977689170
# ID del rol que se asignará al reaccionar
ROLE_ID = 1397709418337927290
# Emoji que se usará para la reacción
REACTION_EMOJI = '✅'  # Puedes cambiarlo por el emoji que prefieras

class Reglas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reglas(self, ctx):
        """Publica las reglas en el canal de reglas y añade la reacción. Solo el usuario autorizado puede usarlo."""
        USUARIO_AUTORIZADO = 569682914967814144
        if ctx.author.id != USUARIO_AUTORIZADO:
            await ctx.send('No tienes permiso para usar este comando.')
            return
        canal_reglas = ctx.guild.get_channel(RULES_CHANNEL_ID)
        if canal_reglas is None:
            await ctx.send('No se encontró el canal de reglas.')
            return
        embed = discord.Embed(
            title="📜 REGLAS DEL SERVIDOR DISCORD & MINECRAFT",
            description=(
                "**1. Respeto ante todo:**\n"
                "Trata a todos los miembros con cortesía y amabilidad. No se tolerarán insultos, acoso ni discriminación.\n\n"
                "**2. No spam ni flood:**\n"
                "Evita enviar mensajes repetitivos, publicidad o enlaces no autorizados.\n\n"
                "**3. Contenido apropiado:**\n"
                "Está prohibido compartir contenido ofensivo, NSFW, ilegal o que infrinja derechos de autor.\n\n"
                "**4. Canales y temas:**\n"
                "Utiliza cada canal para su propósito. Respeta las temáticas y evita desviar conversaciones.\n\n"
                "**5. Minecraft:**\n"
                "No uses hacks, cheats ni exploits en el servidor. Respeta las construcciones y pertenencias de otros jugadores.\n\n"
                "**6. Moderación:**\n"
                "Sigue las indicaciones del staff y reporta cualquier problema o usuario que incumpla las reglas.\n\n"
                "**7. Seguridad:**\n"
                "No compartas datos personales ni solicites información privada a otros miembros.\n\n"
                "Al reaccionar con ✅ aceptas todas las reglas y obtendrás acceso al servidor. ¡Bienvenido y disfruta!"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Servidor de Minecraft")
        msg = await canal_reglas.send(embed=embed)
        await msg.add_reaction(REACTION_EMOJI)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == RULES_CHANNEL_ID and str(payload.emoji) == REACTION_EMOJI:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(ROLE_ID)
            member = guild.get_member(payload.user_id)
            if member is None:
                try:
                    member = await guild.fetch_member(payload.user_id)
                except Exception:
                    member = None
            if member and role:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id == RULES_CHANNEL_ID and str(payload.emoji) == REACTION_EMOJI:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(ROLE_ID)
            member = guild.get_member(payload.user_id)
            if member is None:
                try:
                    member = await guild.fetch_member(payload.user_id)
                except Exception:
                    member = None
            if member and role:
                await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(Reglas(bot))
