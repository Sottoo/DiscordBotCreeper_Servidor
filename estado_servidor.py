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
    print("⚠️ mcstatus no instalado. Instala con: pip install mcstatus")

# ============================================
# CONFIGURACIÓN DEL SERVIDOR
# ============================================

# IP y puerto del servidor de Minecraft
SERVIDOR_IP = "108.181.102.178"
SERVIDOR_PUERTO = 25587

# ID del canal donde se enviarán las notificaciones
CANAL_NOTIFICACIONES_ID = 1277843843743613012

# Horario de apertura (para calcular próxima apertura cuando cierre)
HORA_APERTURA = 16  # 4:00 PM

# Duración del servidor encendido (6 horas)
DURACION_SERVIDOR_HORAS = 6

# Zona horaria
ZONA_HORARIA = 'America/Mexico_City'

# Tiempo entre verificaciones (en segundos)
INTERVALO_VERIFICACION = 30


class EstadoServidor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.canal_notificaciones = None
        self.tz = pytz.timezone(ZONA_HORARIA)
        self.ultimo_estado = None  # True = online, False = offline, None = desconocido
        self.servidor = None
        
        if MCSTATUS_DISPONIBLE:
            self.servidor = JavaServer(SERVIDOR_IP, SERVIDOR_PUERTO)
        
    def cog_unload(self):
        self.monitorear_servidor.cancel()
    
    def obtener_hora_actual(self):
        """Obtiene la hora actual en la zona horaria configurada"""
        return datetime.now(self.tz)
    
    def obtener_timestamp_unix(self, dt):
        """Convierte datetime a timestamp Unix para Discord"""
        return int(dt.timestamp())
    
    def calcular_hora_cierre(self):
        """Calcula la hora de cierre (6 horas desde ahora)"""
        ahora = self.obtener_hora_actual()
        cierre = ahora + timedelta(hours=DURACION_SERVIDOR_HORAS)
        return cierre
    
    def calcular_proxima_apertura(self):
        """Calcula la próxima apertura a las 4 PM del siguiente día"""
        ahora = self.obtener_hora_actual()
        
        # Si son antes de las 4 PM de hoy, la apertura es hoy a las 4 PM
        if ahora.hour < HORA_APERTURA:
            apertura = ahora.replace(hour=HORA_APERTURA, minute=0, second=0, microsecond=0)
        else:
            # Si ya pasaron las 4 PM, la apertura es mañana a las 4 PM
            apertura = ahora.replace(hour=HORA_APERTURA, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return apertura
    
    async def verificar_servidor_online(self):
        """
        Hace ping real al servidor de Minecraft.
        Retorna: (online: bool, jugadores: int, max_jugadores: int)
        """
        if not MCSTATUS_DISPONIBLE or self.servidor is None:
            return None, 0, 0
        
        try:
            loop = asyncio.get_event_loop()
            status = await loop.run_in_executor(None, self.servidor.status)
            return True, status.players.online, status.players.max
        except Exception:
            return False, 0, 0
    
    async def enviar_mensaje_servidor_abierto(self):
        """Envía mensaje cuando el servidor se enciende"""
        if self.canal_notificaciones is None:
            return
        
        hora_cierre = self.calcular_hora_cierre()
        timestamp_cierre = self.obtener_timestamp_unix(hora_cierre)
        
        embed = discord.Embed(
            title="🟢 ¡SERVIDOR ABIERTO!",
            description=(
                f"El servidor de Minecraft está **ONLINE** 🎮\n\n"
                f"**Se cierra en:** <t:{timestamp_cierre}:R>\n"
                f"**Hora de cierre:** <t:{timestamp_cierre}:t>"
            ),
            color=discord.Color.green()
        )
        embed.add_field(
            name="🎮 IP del Servidor",
            value=f"**Java:** `{SERVIDOR_IP}:{SERVIDOR_PUERTO}`\n**Bedrock:** `{SERVIDOR_IP}` Puerto: `{SERVIDOR_PUERTO}`",
            inline=False
        )
        embed.set_footer(text="¡Conéctate y disfruta!")
        embed.set_thumbnail(url="https://i.imgur.com/oBVMSmi.png")
        
        await self.canal_notificaciones.send(
            content=f"@everyone 🎉 **¡El servidor está ABIERTO!** Se cierra <t:{timestamp_cierre}:R>",
            embed=embed
        )
    
    async def enviar_mensaje_servidor_cerrado(self):
        """Envía mensaje cuando el servidor se apaga"""
        if self.canal_notificaciones is None:
            return
        
        proxima_apertura = self.calcular_proxima_apertura()
        timestamp_apertura = self.obtener_timestamp_unix(proxima_apertura)
        
        embed = discord.Embed(
            title="🔴 SERVIDOR CERRADO",
            description=(
                f"El servidor de Minecraft está **OFFLINE** 😴\n\n"
                f"**Vuelve:** <t:{timestamp_apertura}:R>\n"
                f"**Próxima apertura:** <t:{timestamp_apertura}:F>"
            ),
            color=discord.Color.red()
        )
        embed.add_field(
            name="📅 Horario del Servidor",
            value="🟢 **Abierto:** 4:00 PM - 10:00 PM\n🔴 **Cerrado:** 10:00 PM - 4:00 PM",
            inline=False
        )
        embed.set_footer(text="¡Descansa y vuelve mañana!")
        embed.set_thumbnail(url="https://i.imgur.com/JxYMC8T.png")
        
        await self.canal_notificaciones.send(
            content=f"💤 **Servidor cerrado.** Vuelve <t:{timestamp_apertura}:R>",
            embed=embed
        )
    
    @tasks.loop(seconds=INTERVALO_VERIFICACION)
    async def monitorear_servidor(self):
        """Monitorea el servidor y envía mensajes cuando cambia de estado"""
        if self.canal_notificaciones is None:
            return
        
        online, jugadores, max_jugadores = await self.verificar_servidor_online()
        
        if online is None:
            return  # mcstatus no disponible
        
        # Detectar cambio de estado
        if self.ultimo_estado is not None:
            if online and not self.ultimo_estado:
                # Servidor pasó de OFFLINE a ONLINE
                print(f"[{datetime.now()}] Servidor detectado ONLINE - Enviando notificación")
                await self.enviar_mensaje_servidor_abierto()
            
            elif not online and self.ultimo_estado:
                # Servidor pasó de ONLINE a OFFLINE
                print(f"[{datetime.now()}] Servidor detectado OFFLINE - Enviando notificación")
                await self.enviar_mensaje_servidor_cerrado()
        
        # Actualizar último estado conocido
        self.ultimo_estado = online
    
    @monitorear_servidor.before_loop
    async def antes_de_monitorear(self):
        await self.bot.wait_until_ready()
        
        # Configurar automáticamente el canal de notificaciones
        if CANAL_NOTIFICACIONES_ID:
            self.canal_notificaciones = self.bot.get_channel(CANAL_NOTIFICACIONES_ID)
            if self.canal_notificaciones:
                print(f"✅ Canal de notificaciones configurado: #{self.canal_notificaciones.name}")
                
                # Obtener estado inicial del servidor
                online, _, _ = await self.verificar_servidor_online()
                self.ultimo_estado = online
                estado = "ONLINE" if online else "OFFLINE"
                print(f"📡 Estado inicial del servidor: {estado}")
            else:
                print(f"⚠️ No se encontró el canal con ID: {CANAL_NOTIFICACIONES_ID}")
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Inicia el monitoreo automáticamente cuando el bot está listo"""
        if not self.monitorear_servidor.is_running():
            self.monitorear_servidor.start()
            print("🔄 Monitoreo del servidor iniciado automáticamente")
    
    # ============================================
    # COMANDOS
    # ============================================
    
    @commands.command(name='estadoservidor', aliases=['estado', 'server', 'status'])
    async def mostrar_estado(self, ctx):
        """Muestra el estado actual del servidor de Minecraft"""
        async with ctx.typing():
            online, jugadores, max_jugadores = await self.verificar_servidor_online()
        
        if online is None:
            await ctx.send("⚠️ No se puede verificar el estado del servidor (mcstatus no disponible)")
            return
        
        if online:
            hora_cierre = self.calcular_hora_cierre()
            timestamp_cierre = self.obtener_timestamp_unix(hora_cierre)
            
            embed = discord.Embed(
                title="🟢 SERVIDOR ONLINE",
                description=f"👥 **Jugadores:** {jugadores}/{max_jugadores}",
                color=discord.Color.green()
            )
            embed.add_field(
                name="⏰ Se cierra en:",
                value=f"<t:{timestamp_cierre}:R> (<t:{timestamp_cierre}:t>)",
                inline=False
            )
        else:
            proxima_apertura = self.calcular_proxima_apertura()
            timestamp_apertura = self.obtener_timestamp_unix(proxima_apertura)
            
            embed = discord.Embed(
                title="🔴 SERVIDOR OFFLINE",
                description="El servidor está apagado.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="📅 Próxima apertura:",
                value=f"<t:{timestamp_apertura}:R> (<t:{timestamp_apertura}:F>)",
                inline=False
            )
        
        embed.add_field(
            name="🎮 IP",
            value=f"`{SERVIDOR_IP}:{SERVIDOR_PUERTO}`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='jugadores', aliases=['players', 'online'])
    async def mostrar_jugadores(self, ctx):
        """Muestra los jugadores actualmente conectados"""
        async with ctx.typing():
            online, jugadores, max_jugadores = await self.verificar_servidor_online()
        
        if online:
            await ctx.send(f"👥 **Jugadores online:** {jugadores}/{max_jugadores}")
        else:
            await ctx.send("🔴 El servidor está **offline**.")
    
    @commands.command(name='iniciarmonitor', aliases=['monitor'])
    @commands.has_permissions(administrator=True)
    async def iniciar_monitor(self, ctx, canal: discord.TextChannel = None):
        """
        Inicia el monitoreo del servidor en el canal especificado.
        Cuando el servidor se encienda/apague, enviará notificaciones automáticas.
        Uso: !iniciarmonitor #canal
        """
        if canal is None:
            canal = ctx.channel
        
        self.canal_notificaciones = canal
        
        # Obtener estado actual para no enviar notificación falsa al iniciar
        online, _, _ = await self.verificar_servidor_online()
        self.ultimo_estado = online
        
        # Iniciar el loop de monitoreo si no está corriendo
        if not self.monitorear_servidor.is_running():
            self.monitorear_servidor.start()
        
        estado_actual = "🟢 ONLINE" if online else "🔴 OFFLINE"
        
        await ctx.send(
            f"✅ **Monitoreo del servidor iniciado en {canal.mention}**\n\n"
            f"📡 **Estado actual:** {estado_actual}\n"
            f"🔄 **Verificando cada:** {INTERVALO_VERIFICACION} segundos\n"
            f"🎮 **IP monitoreada:** `{SERVIDOR_IP}:{SERVIDOR_PUERTO}`\n\n"
            f"Cuando el servidor se **encienda** o **apague**, enviaré una notificación automática con el reloj dinámico de Discord."
        )
    
    @commands.command(name='detenermonitor', aliases=['stopmonitor'])
    @commands.has_permissions(administrator=True)
    async def detener_monitor(self, ctx):
        """Detiene el monitoreo del servidor"""
        if self.monitorear_servidor.is_running():
            self.monitorear_servidor.cancel()
        
        self.canal_notificaciones = None
        self.ultimo_estado = None
        
        await ctx.send("⏹️ **Monitoreo del servidor detenido.**")
    
    @commands.command(name='testabierto')
    @commands.has_permissions(administrator=True)
    async def test_mensaje_abierto(self, ctx):
        """Prueba el mensaje de servidor abierto"""
        self.canal_notificaciones = ctx.channel
        await self.enviar_mensaje_servidor_abierto()
    
    @commands.command(name='testcerrado')
    @commands.has_permissions(administrator=True)
    async def test_mensaje_cerrado(self, ctx):
        """Prueba el mensaje de servidor cerrado"""
        self.canal_notificaciones = ctx.channel
        await self.enviar_mensaje_servidor_cerrado()


async def setup(bot):
    await bot.add_cog(EstadoServidor(bot))
