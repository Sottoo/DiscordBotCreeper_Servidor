import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz
import asyncio

# Importar mcstatus para verificar el estado real del servidor
try:
    from mcstatus import JavaServer
    MCSTATUS_DISPONIBLE = True
except ImportError:
    MCSTATUS_DISPONIBLE = False
    print("⚠️ mcstatus no instalado")

# ============================================
# CONFIGURACIÓN DEL SERVIDOR
# ============================================

SERVIDOR_IP = "108.181.102.178"
SERVIDOR_PUERTO = 25587
CANAL_NOTIFICACIONES_ID = 1277843843743613012

# Horarios del servidor
HORA_APERTURA = 16  # 4:00 PM
HORA_CIERRE = 22    # 10:00 PM

ZONA_HORARIA = 'America/Mexico_City'
INTERVALO_VERIFICACION = 60  # Verificar cada 60 segundos (menos spam en logs)


class EstadoServidor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.canal_notificaciones = None
        self.tz = pytz.timezone(ZONA_HORARIA)
        self.ultimo_estado = None
        self.servidor = None
        
        if MCSTATUS_DISPONIBLE:
            self.servidor = JavaServer(SERVIDOR_IP, SERVIDOR_PUERTO)
        
    def cog_unload(self):
        self.monitorear_servidor.cancel()
    
    def obtener_hora_actual(self):
        return datetime.now(self.tz)
    
    def obtener_timestamp_unix(self, dt):
        return int(dt.timestamp())
    
    def calcular_hora_cierre(self):
        """Calcula la hora de cierre (10 PM de hoy)"""
        ahora = self.obtener_hora_actual()
        cierre = ahora.replace(hour=HORA_CIERRE, minute=0, second=0, microsecond=0)
        if ahora.hour >= HORA_CIERRE:
            cierre += timedelta(days=1)
        return cierre
    
    def calcular_proxima_apertura(self):
        """Calcula la próxima apertura a las 4 PM"""
        ahora = self.obtener_hora_actual()
        
        if ahora.hour < HORA_APERTURA:
            apertura = ahora.replace(hour=HORA_APERTURA, minute=0, second=0, microsecond=0)
        else:
            apertura = ahora.replace(hour=HORA_APERTURA, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return apertura
    
    async def verificar_servidor_online(self):
        if not MCSTATUS_DISPONIBLE or self.servidor is None:
            return None, 0, 0
        
        try:
            loop = asyncio.get_event_loop()
            status = await loop.run_in_executor(None, self.servidor.status)
            return True, status.players.online, status.players.max
        except Exception:
            return False, 0, 0
    
    async def enviar_mensaje_servidor_abierto(self, jugadores=0, max_jugadores=20):
        """Envía embed profesional cuando el servidor se enciende"""
        if self.canal_notificaciones is None:
            return
        
        hora_cierre = self.calcular_hora_cierre()
        timestamp_cierre = self.obtener_timestamp_unix(hora_cierre)
        
        embed = discord.Embed(
            color=0x2ECC71  # Verde elegante
        )
        
        embed.set_author(
            name="SERVIDOR DE MINECRAFT",
            icon_url="https://i.imgur.com/oBVMSmi.png"
        )
        
        embed.add_field(
            name="",
            value=(
                f"# 🟢 ¡Servidor Abierto!\n\n"
                f"El servidor ya está disponible para jugar.\n\n"
                f"**⏰ Se cierra:** <t:{timestamp_cierre}:R>\n"
                f"**📅 Hora exacta:** <t:{timestamp_cierre}:t>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎮 Conexión",
            value=f"```{SERVIDOR_IP}:{SERVIDOR_PUERTO}```",
            inline=True
        )
        
        embed.add_field(
            name="👥 Jugadores",
            value=f"```{jugadores}/{max_jugadores}```",
            inline=True
        )
        
        embed.set_footer(text="Horario: 4:00 PM - 10:00 PM")
        embed.set_thumbnail(url="https://i.imgur.com/6YToyEF.png")
        
        try:
            await self.canal_notificaciones.send(embed=embed)
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")
    
    async def enviar_mensaje_servidor_cerrado(self):
        """Envía embed profesional cuando el servidor se apaga"""
        if self.canal_notificaciones is None:
            return
        
        proxima_apertura = self.calcular_proxima_apertura()
        timestamp_apertura = self.obtener_timestamp_unix(proxima_apertura)
        
        embed = discord.Embed(
            color=0xE74C3C  # Rojo elegante
        )
        
        embed.set_author(
            name="SERVIDOR DE MINECRAFT",
            icon_url="https://i.imgur.com/oBVMSmi.png"
        )
        
        embed.add_field(
            name="",
            value=(
                f"# 🔴 Servidor Cerrado\n\n"
                f"El servidor se ha apagado por hoy.\n\n"
                f"**⏰ Abre:** <t:{timestamp_apertura}:R>\n"
                f"**📅 Próxima sesión:** <t:{timestamp_apertura}:F>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📋 Horario diario",
            value="```🟢 Abierto:  4:00 PM\n🔴 Cierra:  10:00 PM```",
            inline=False
        )
        
        embed.set_footer(text="¡Nos vemos en la próxima sesión!")
        embed.set_thumbnail(url="https://i.imgur.com/JxYMC8T.png")
        
        try:
            await self.canal_notificaciones.send(embed=embed)
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")
    
    @tasks.loop(seconds=INTERVALO_VERIFICACION)
    async def monitorear_servidor(self):
        """Monitorea el servidor y envía mensajes cuando cambia de estado"""
        if self.canal_notificaciones is None:
            return
        
        online, jugadores, max_jugadores = await self.verificar_servidor_online()
        
        if online is None:
            return
        
        # Detectar cambio de estado
        if self.ultimo_estado is not None:
            if online and not self.ultimo_estado:
                # OFFLINE → ONLINE
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🟢 Servidor ONLINE detectado")
                await self.enviar_mensaje_servidor_abierto(jugadores, max_jugadores)
            
            elif not online and self.ultimo_estado:
                # ONLINE → OFFLINE
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔴 Servidor OFFLINE detectado")
                await self.enviar_mensaje_servidor_cerrado()
        
        self.ultimo_estado = online
    
    @monitorear_servidor.before_loop
    async def antes_de_monitorear(self):
        await self.bot.wait_until_ready()
        
        if CANAL_NOTIFICACIONES_ID:
            self.canal_notificaciones = self.bot.get_channel(CANAL_NOTIFICACIONES_ID)
            if self.canal_notificaciones:
                online, _, _ = await self.verificar_servidor_online()
                self.ultimo_estado = online
                print(f"📡 Monitoreo activo | Estado inicial: {'ONLINE' if online else 'OFFLINE'}")
    
    # ============================================
    # COMANDOS
    # ============================================
    
    @commands.command(name='estado', aliases=['server', 'status', 'mc'])
    async def mostrar_estado(self, ctx):
        """Muestra el estado actual del servidor"""
        async with ctx.typing():
            online, jugadores, max_jugadores = await self.verificar_servidor_online()
        
        if online is None:
            await ctx.send("⚠️ No se puede verificar el estado")
            return
        
        if online:
            hora_cierre = self.calcular_hora_cierre()
            ts = self.obtener_timestamp_unix(hora_cierre)
            
            embed = discord.Embed(
                title="🟢 Servidor Online",
                description=f"**Jugadores:** {jugadores}/{max_jugadores}\n**Cierra:** <t:{ts}:R>",
                color=0x2ECC71
            )
        else:
            proxima = self.calcular_proxima_apertura()
            ts = self.obtener_timestamp_unix(proxima)
            
            embed = discord.Embed(
                title="🔴 Servidor Offline",
                description=f"**Abre:** <t:{ts}:R>",
                color=0xE74C3C
            )
        
        embed.add_field(name="IP", value=f"`{SERVIDOR_IP}:{SERVIDOR_PUERTO}`", inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(name='jugadores', aliases=['players', 'online'])
    async def mostrar_jugadores(self, ctx):
        """Muestra jugadores conectados"""
        online, jugadores, max_jugadores = await self.verificar_servidor_online()
        
        if online:
            await ctx.send(f"👥 **{jugadores}/{max_jugadores}** jugadores online")
        else:
            await ctx.send("🔴 Servidor offline")
    
    @commands.command(name='forzaronline')
    @commands.has_permissions(administrator=True)
    async def forzar_online(self, ctx):
        """Fuerza estado a ONLINE (para testing)"""
        self.ultimo_estado = True
        await ctx.send("✅ Estado forzado a ONLINE", delete_after=5)
    
    @commands.command(name='forzaroffline')
    @commands.has_permissions(administrator=True)
    async def forzar_offline(self, ctx):
        """Fuerza estado a OFFLINE (para testing)"""
        self.ultimo_estado = False
        await ctx.send("✅ Estado forzado a OFFLINE", delete_after=5)
    
    @commands.command(name='testabierto')
    @commands.has_permissions(administrator=True)
    async def test_abierto(self, ctx):
        """Prueba mensaje de servidor abierto"""
        self.canal_notificaciones = ctx.channel
        await self.enviar_mensaje_servidor_abierto(0, 20)
    
    @commands.command(name='testcerrado')
    @commands.has_permissions(administrator=True)
    async def test_cerrado(self, ctx):
        """Prueba mensaje de servidor cerrado"""
        self.canal_notificaciones = ctx.channel
        await self.enviar_mensaje_servidor_cerrado()


async def setup(bot):
    await bot.add_cog(EstadoServidor(bot))
