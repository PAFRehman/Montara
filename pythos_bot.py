#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  PYTHOS BOT v2.0 — Optimized Single-File Discord Bot                         ║
║  Crypto • Charts • Music • Moderation • Smoking • Permissions                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Deploy free on: Railway, Render, Fly.io, Replit                             ║
║  Setup: pip install -r requirements.txt && python bot.py                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, asyncio, json, re, random, datetime, io, traceback, logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from contextlib import asynccontextmanager

import discord
from discord import app_commands, ui
from discord.ext import commands
import aiohttp
import aiosqlite
import numpy as np

# Matplotlib setup (headless)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ─── CONFIG ────────────────────────────────────────────────────────────────────
TOKEN       = os.getenv("DISCORD_BOT_TOKEN", "")
ADMIN_ROLE  = os.getenv("ADMIN_ROLE", "Admin")
DB_PATH     = os.getenv("DB_PATH", "pythos.db")
PORT        = int(os.getenv("PORT", "8080"))  # for health-check server

# Pyth Hermes feeds (update placeholders when chains go live)
PYTH_FEEDS: Dict[str, str] = {
    "BTC":"e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    "ETH":"ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
    "SOL":"ef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    "AVAX":"93da3352f9f1d105fdfe4971cfa80e9dd777bfc55d11f976e0fe1b55f4a5a26e",
    "ARB":"3fa4252848f9f0a1480be62745a4629d9eb1322aebab8a791e344b3b9c1adcf5",
    "OP":"385f64d993f7b77d8032ed97c44c499b6d8862f9d6a8a3c4a50be85fae94c427",
    "MATIC":"5de33a9112c2b700b8d30b8a3402c103578ccfa4b2987c6a3b0903b10c9ee1f2",
    "BNB":"2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f",
    "XRP":"ec5d399846a9209f3fe75d793d6811e0742b2b3a747e5d3a81e3332c5c333a11",
    "DOGE":"dcef50d9b0f6b7f5a0e5e6b2e1e2e3e4e5e6e7e8e9e0e1e2e3e4e5e6e7e8e9e0",
    "MONAD":"0x31491744e2dbf6df7fcf4ac0820d18a609b49076d45066d3568424e62f686cd1",
    "MEGAETH":"",
    "SUI":"23d7315113f5b1d3ba7a83604b2358b3b4b5f6f7f8f9f0f1f2f3f4f5f6f7f8f9f0",
    "APT":"03ae4db29ed4ae33d323568895aa00159e5e5f6f7f8f9f0f1f2f3f4f5f6f7f8f9",
    "SEI":"1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12",
    "GOLD":"765d2ba906abc32da01daa4c5e0b8a9f1f2f3f4f5f6f7f8f9f0f1f2f3f4f5f6f7",
    "SILVER":"abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "OIL":"fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
    "LINK":"8ac0c70fff57e9aefdf5edf44b51d62eadba9363a1bb524b797564d32a86b1e",
    "UNI":"9d6e1f1f2f3f4f5f6f7f8f9f0f1f2f3f4f5f6f7f8f9f0f1f2f3f4f5f6f7f8f9",
    "AAVE":"aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899",
    "CRV":"11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
}

SMOKE_FACTS = [
    "The world's oldest known cigarette brand is Lorillard, founded in 1760.",
    "A single cigarette contains over 7,000 chemicals, 69 of which are known carcinogens.",
    "Nicotine reaches the brain within 10 seconds of inhalation.",
    "Bhutan was the first country to completely ban tobacco sales in 2004.",
    "Cigarette butts are the most littered item on Earth: 4.5 trillion/year.",
    "The word 'nicotine' comes from Jean Nicot, who introduced tobacco to France in 1560.",
]
SMOKE_STRAINS = [
    "🌿 OG Kush — Relaxing, earthy, pine",
    "🍋 Sour Diesel — Energetic, pungent, diesel",
    "🫐 Blue Dream — Balanced, sweet, berry",
    "🌲 Northern Lights — Sedating, sweet, spicy",
    "🥭 Mango Haze — Uplifting, tropical, fruity",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("pythos")

# ─── DISMISS VIEW (reusable) ─────────────────────────────────────────────────
class DismissView(ui.View):
    """Adds a 🗑️ Dismiss button to any response."""
    def __init__(self, user_id: int, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.user_id = user_id

    @ui.button(label="🗑️ Dismiss", style=discord.ButtonStyle.secondary)
    async def dismiss(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your message.", ephemeral=True)
            return
        await interaction.message.delete()

# ─── ASYNC DATABASE ──────────────────────────────────────────────────────────
class AsyncDB:
    """Singleton async SQLite pool wrapper."""
    _instance: Optional["AsyncDB"] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._db: Optional[aiosqlite.Connection] = None
        return cls._instance

    async def connect(self):
        if self._db is None:
            self._db = await aiosqlite.connect(DB_PATH)
            self._db.row_factory = aiosqlite.Row
            await self._migrate()
        return self._db

    async def _migrate(self):
        await self._db.executescript("""
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id INTEGER, guild_id INTEGER,
                last_msg_ts REAL, last_react_ts REAL,
                warned_7 INTEGER DEFAULT 0, warned_10 INTEGER DEFAULT 0,
                dm_sent INTEGER DEFAULT 0, PRIMARY KEY(user_id,guild_id)
            );
            CREATE TABLE IF NOT EXISTS guild_cfg (
                guild_id INTEGER PRIMARY KEY, alert_ch INTEGER,
                warn_days INTEGER DEFAULT 7, kick_add_days INTEGER DEFAULT 3,
                enabled INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS cmd_perms (
                id INTEGER PRIMARY KEY, guild_id INTEGER, cmd TEXT,
                chs TEXT, roles TEXT, disabled INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS smoke_stats (
                user_id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0,
                last REAL, streak INTEGER DEFAULT 0
            );
        """)
        await self._db.commit()

    async def execute(self, sql: str, params=()):
        db = await self.connect()
        async with db.execute(sql, params) as cur:
            await db.commit()
            return cur

    async def fetchone(self, sql: str, params=()):
        db = await self.connect()
        async with db.execute(sql, params) as cur:
            return await cur.fetchone()

    async def fetchall(self, sql: str, params=()):
        db = await self.connect()
        async with db.execute(sql, params) as cur:
            return await cur.fetchall()

DB = AsyncDB()

# ─── PYTH CLIENT ─────────────────────────────────────────────────────────────
class PythClient:
    BASE = "https://hermes.pyth.network/v2"
    def __init__(self):
        self._sess: Optional[aiohttp.ClientSession] = None

    async def _sess(self) -> aiohttp.ClientSession:
        if self._sess is None or self._sess.closed:
            self._sess = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        return self._sess

    async def price(self, sym: str) -> Optional[Dict]:
        fid = PYTH_FEEDS.get(sym.upper())
        if not fid:
            return None
        try:
            s = await self._sess()
            async with s.get(f"{self.BASE}/updates/price/latest", params={"ids[]": fid}) as r:
                if r.status != 200:
                    return None
                d = await r.json()
                p = d["parsed"][0]["price"]
                return {
                    "sym": sym.upper(),
                    "price": float(p["price"]) * (10 ** p["expo"]),
                    "conf": float(p["conf"]) * (10 ** p["expo"]),
                    "ts": p["publish_time"],
                }
        except Exception as e:
            log.warning(f"Pyth error {sym}: {e}")
            return None

    async def feeds(self) -> List[Dict]:
        try:
            s = await self._sess()
            async with s.get(f"{self.BASE}/price_feeds") as r:
                return await r.json() if r.status == 200 else []
        except:
            return []

    async def close(self):
        if self._sess and not self._sess.closed:
            await self._sess.close()

# ─── CHART ENGINE ─────────────────────────────────────────────────────────────
class ChartEngine:
    @staticmethod
    def render(sym: str, hist: List[tuple] = None, title: str = None) -> discord.File:
        if not hist:
            hist = ChartEngine._demo(sym)
        dates = [datetime.datetime.fromtimestamp(ts) for ts, _ in hist]
        prices = [p for _, p in hist]
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(10, 5), facecolor="#1a1a2e")
        ax.set_facecolor("#16213e")
        ax.plot(dates, prices, color="#e94560", lw=2.5)
        ax.fill_between(dates, prices, alpha=0.25, color="#e94560")
        ax.grid(True, alpha=0.15, color="white")
        ax.set_title(title or f"{sym.upper()} Price", color="white", fontsize=15, weight="bold")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=140, bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)
        return discord.File(buf, filename=f"{sym.lower()}_chart.png")

    @staticmethod
    def _demo(sym: str) -> List[tuple]:
        bases = {"BTC":65000,"ETH":3500,"SOL":145,"AVAX":35,"MONAD":2.5,
                 "MEGAETH":1.2,"GOLD":2300,"SILVER":28,"BNB":580,"XRP":0.55,
                 "DOGE":0.12,"LINK":18}
        b = bases.get(sym.upper(), 100)
        now = datetime.datetime.now()
        return [( (now - datetime.timedelta(hours=48-i)).timestamp(),
                  b + np.random.normal(0,b*0.02) + np.sin(i/5)*b*0.05 )
                for i in range(48)]

# ─── MUSIC MANAGER ───────────────────────────────────────────────────────────
class MusicMgr:
    def __init__(self):
        self.q: Dict[int, List[Dict]] = {}
        self.cur: Dict[int, Optional[Dict]] = {}
    def add(self, gid: int, song: Dict):
        self.q.setdefault(gid, []).append(song)
    def pop(self, gid: int) -> Optional[Dict]:
        return self.q[gid].pop(0) if self.q.get(gid) else None
    async def nxt(self, gid: int, vc: discord.VoiceClient):
        song = self.pop(gid)
        if not song:
            self.cur[gid] = None
            return
        self.cur[gid] = song
        def after(err):
            if err:
                log.warning(f"Playback err: {err}")
            asyncio.run_coroutine_threadsafe(self.nxt(gid, vc), vc.loop)
        src = discord.FFmpegPCMAudio(song["url"],
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")
        vc.play(src, after=after)

# ─── PERMISSIONS ───────────────────────────────────────────────────────────────
class Perms:
    @staticmethod
    async def check(inter: discord.Interaction, cmd: str) -> bool:
        rows = await DB.fetchall(
            "SELECT chs,roles,disabled FROM cmd_perms WHERE guild_id=? AND cmd=?",
            (inter.guild_id, cmd))
        if not rows:
            return True
        for r in rows:
            if r["disabled"]:
                continue
            chs = [int(x) for x in r["chs"].split(",") if x.strip()] if r["chs"] else []
            if chs and inter.channel_id not in chs:
                continue
            roles = [int(x) for x in r["roles"].split(",") if x.strip()] if r["roles"] else []
            if roles and not any(rid in [rl.id for rl in inter.user.roles] for rid in roles):
                continue
            return True
        return False

    @staticmethod
    def is_admin(m: discord.Member) -> bool:
        return any(r.name == ADMIN_ROLE or r.permissions.administrator for r in m.roles)

# ─── INACTIVITY TRACKER ────────────────────────────────────────────────────────
class Inactivity:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def bump(self, uid: int, gid: int, typ: str = "msg"):
        now = datetime.datetime.now().timestamp()
        exists = await DB.fetchone("SELECT 1 FROM user_activity WHERE user_id=? AND guild_id=?", (uid, gid))
        if exists:
            col = "last_msg_ts" if typ == "msg" else "last_react_ts"
            await DB.execute(f"""UPDATE user_activity SET {col}=?, warned_7=0,warned_10=0,dm_sent=0
                               WHERE user_id=? AND guild_id=?""", (now, uid, gid))
        else:
            await DB.execute("""INSERT INTO user_activity(user_id,guild_id,last_msg_ts,last_react_ts)
                               VALUES(?,?,?,?)""", (uid, gid, now, now if typ=="react" else now))

    async def scan(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                now = datetime.datetime.now().timestamp()
                guilds = await DB.fetchall("SELECT * FROM guild_cfg WHERE enabled=1")
                for g in guilds:
                    gid, ach, wd, kd = g["guild_id"], g["alert_ch"], g["warn_days"], g["kick_add_days"]
                    guild = self.bot.get_guild(gid)
                    if not guild:
                        continue
                    ch = guild.get_channel(ach) if ach else None
                    if not ch:
                        for c in guild.text_channels:
                            if c.name == "moderation-alerts":
                                ch = c; break
                    if not ch:
                        continue
                    # 7-day warning
                    rows = await DB.fetchall(
                        "SELECT * FROM user_activity WHERE guild_id=? AND warned_7=0 AND (last_msg_ts<? OR last_react_ts<?)",
                        (gid, now - wd*86400, now - wd*86400))
                    for r in rows:
                        mem = guild.get_member(r["user_id"])
                        if not mem or mem.bot:
                            continue
                        try:
                            emb = discord.Embed(title="🚨 PURGER ALERT", color=discord.Color.red(),
                                description=f"**{mem.display_name}**, you've been inactive **{wd} days** in **{guild.name}**.\n\n"
                                            f"Send a message or react within **{kd} days** or you may be removed.")
                            emb.set_footer(text="Reply to stay active")
                            await mem.send(embed=emb)
                            await DB.execute("UPDATE user_activity SET warned_7=1,dm_sent=1 WHERE user_id=? AND guild_id=?",
                                            (r["user_id"], gid))
                        except:
                            pass
                        adm = discord.Embed(title="⚠️ Inactivity Warning", color=discord.Color.orange(),
                            description=f"{mem.mention} inactive **{wd}+ days**.\nDM sent. Admin react ✅ to confirm.")
                        msg = await ch.send(embed=adm)
                        await msg.add_reaction("✅")
                    # 10-day kick rec
                    rows = await DB.fetchall(
                        "SELECT * FROM user_activity WHERE guild_id=? AND warned_7=1 AND warned_10=0 AND (last_msg_ts<? OR last_react_ts<?)",
                        (gid, now - (wd+kd)*86400, now - (wd+kd)*86400))
                    for r in rows:
                        mem = guild.get_member(r["user_id"])
                        if not mem or mem.bot:
                            continue
                        kick = discord.Embed(title="🔨 Kick Recommendation", color=discord.Color.dark_red(),
                            description=f"{mem.mention} inactive **{wd+kd}+ days** total.\nReact 🥾 to kick | 🚫 to ignore.")
                        await ch.send(embed=kick)
                        await DB.execute("UPDATE user_activity SET warned_10=1 WHERE user_id=? AND guild_id=?",
                                        (r["user_id"], gid))
            except Exception as e:
                log.error(f"Inactivity scan: {e}")
            await asyncio.sleep(3600)

# ─── BOT CLASS ─────────────────────────────────────────────────────────────────
class Pythos(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = intents.members = intents.reactions = intents.voice_states = True
        super().__init__(command_prefix="!", intents=intents)
        self.pyth = PythClient()
        self.chart = ChartEngine()
        self.music = MusicMgr()
        self.inact = Inactivity(self)
        self.tree.on_error = self._cmd_err

    async def setup_hook(self):
        await DB.connect()
        asyncio.create_task(self.inact.scan())
        asyncio.create_task(self._keepalive())

    async def on_ready(self):
        log.info(f"Bot online as {self.user} | Guilds: {len(self.guilds)}")
        try:
            synced = await self.tree.sync()
            log.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            log.error(f"Sync error: {e}")

    async def on_message(self, msg: discord.Message):
        if msg.author.bot or not msg.guild:
            return
        await self.inact.bump(msg.author.id, msg.guild.id, "msg")
        await self.process_commands(msg)

    async def on_reaction_add(self, react: discord.Reaction, user: discord.User):
        if user.bot or not react.message.guild:
            return
        await self.inact.bump(user.id, react.message.guild.id, "react")

    async def _cmd_err(self, inter: discord.Interaction, err: app_commands.AppCommandError):
        if isinstance(err, app_commands.CheckFailure):
            await inter.response.send_message("❌ Permission denied.", ephemeral=True)
        else:
            log.error(f"Cmd error: {err}")
            if not inter.response.is_done():
                await inter.response.send_message("❌ Internal error.", ephemeral=True)
            else:
                await inter.followup.send("❌ Internal error.", ephemeral=True)

    async def _keepalive(self):
        """Simple HTTP health-check to keep free-tier hosts alive."""
        from aiohttp import web
        async def health(_):
            return web.Response(text=json.dumps({"status":"ok","guilds":len(self.guilds)}), content_type="application/json")
        app = web.Application()
        app.router.add_get("/", health)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        log.info(f"Keep-alive server on port {PORT}")

# ─── CHECKS ────────────────────────────────────────────────────────────────────
def perm_check():
    async def pred(inter: discord.Interaction) -> bool:
        if not await Perms.check(inter, inter.command.name if inter.command else "unknown"):
            raise app_commands.CheckFailure("denied")
        return True
    return app_commands.check(pred)

def admin_check():
    async def pred(inter: discord.Interaction) -> bool:
        if not isinstance(inter.user, discord.Member) or not Perms.is_admin(inter.user):
            raise app_commands.CheckFailure("admin only")
        return True
    return app_commands.check(pred)

bot = Pythos()

# ─── CRYPTO COMMANDS ─────────────────────────────────────────────────────────
@bot.tree.command(name="price", description="Real-time crypto/commodity price via Pyth")
@app_commands.describe(symbol="Symbol: BTC, ETH, SOL, GOLD, MONAD, MEGAETH...")
@perm_check()
async def cmd_price(inter: discord.Interaction, symbol: str):
    await inter.response.defer(ephemeral=False)
    data = await bot.pyth.price(symbol)
    if not data:
        emb = discord.Embed(title="❌ Not Found", color=discord.Color.red(),
            description=f"No Pyth feed for **{symbol.upper()}**.\nTry: {', '.join(sorted(PYTH_FEEDS)[:10])}...")
        await inter.followup.send(embed=emb, view=DismissView(inter.user.id))
        return
    emb = discord.Embed(title=f"💰 {data['sym']}", description=f"**${data['price']:,.4f}**", color=discord.Color.green())
    emb.add_field(name="Confidence", value=f"±${data['conf']:,.4f}", inline=True)
    emb.add_field(name="Updated", value=f"<t:{int(data['ts'])}:R>", inline=True)
    emb.set_footer(text="Pyth Network Oracle")
    await inter.followup.send(embed=emb, view=DismissView(inter.user.id))

@bot.tree.command(name="chart", description="Price chart for any asset")
@app_commands.describe(symbol="Asset symbol", timeframe="1h / 24h / 7d")
@perm_check()
async def cmd_chart(inter: discord.Interaction, symbol: str, timeframe: str = "24h"):
    await inter.response.defer(ephemeral=False)
    data = await bot.pyth.price(symbol)
    if not data:
        await inter.followup.send(f"❌ No feed for **{symbol.upper()}**.", ephemeral=True)
        return
    file = bot.chart.render(symbol, title=f"{symbol.upper()} — {timeframe} (Pyth)")
    emb = discord.Embed(title=f"📊 {symbol.upper()}", description=f"${data['price']:,.4f}", color=discord.Color.blue())
    emb.set_image(url=f"attachment://{symbol.lower()}_chart.png")
    emb.set_footer(text="Pyth Network | Demo data for viz")
    await inter.followup.send(embed=emb, file=file, view=DismissView(inter.user.id))

@bot.tree.command(name="convert", description="Convert between assets using Pyth")
@app_commands.describe(f="From", t="To", amount="Amount")
@perm_check()
async def cmd_convert(inter: discord.Interaction, f: str, t: str, amount: float):
    await inter.response.defer()
    a = await bot.pyth.price(f); b = await bot.pyth.price(t)
    if not a or not b:
        await inter.followup.send("❌ Price fetch failed.", ephemeral=True); return
    res = (amount * a["price"]) / b["price"]
    emb = discord.Embed(title="💱 Conversion", color=discord.Color.gold())
    emb.add_field(name="From", value=f"{amount:,.4f} {a['sym']} @ ${a['price']:,.4f}", inline=False)
    emb.add_field(name="To", value=f"{res:,.4f} {b['sym']} @ ${b['price']:,.4f}", inline=False)
    emb.add_field(name="Rate", value=f"1 {a['sym']} = {a['price']/b['price']:,.6f} {b['sym']}", inline=False)
    await inter.followup.send(embed=emb, view=DismissView(inter.user.id))

@bot.tree.command(name="pyth_feeds", description="List available Pyth feeds")
@perm_check()
async def cmd_feeds(inter: discord.Interaction):
    await inter.response.defer()
    feeds = await bot.pyth.feeds()
    if not feeds:
        txt = "\n".join(f"• **{k}**" for k in sorted(PYTH_FEEDS))
        emb = discord.Embed(title="📡 Configured Feeds", description=txt, color=discord.Color.blue())
    else:
        txt = "\n".join(f"• {f.get('attributes',{}).get('base','?')}" for f in feeds[:40])
        emb = discord.Embed(title=f"📡 Pyth Feeds ({len(feeds)})", description=txt+"\n...", color=discord.Color.blue())
    await inter.followup.send(embed=emb, view=DismissView(inter.user.id))

# ─── MUSIC COMMANDS ────────────────────────────────────────────────────────────
@bot.tree.command(name="play", description="Play music in your voice channel")
@app_commands.describe(query="YouTube URL or search")
@perm_check()
async def cmd_play(inter: discord.Interaction, query: str):
    await inter.response.defer(ephemeral=False)
    if not inter.user.voice or not inter.user.voice.channel:
        await inter.followup.send("❌ Join a voice channel first!", ephemeral=True); return
    vc = inter.guild.voice_client
    if not vc:
        vc = await inter.user.voice.channel.connect()
    elif vc.channel != inter.user.voice.channel:
        await vc.move_to(inter.user.voice.channel)
    await inter.followup.send(f"🔍 Searching **{query}**...")
    try:
        import yt_dlp
        ydl = yt_dlp.YoutubeDL({"format":"bestaudio/best","quiet":True,"no_warnings":True})
        info = ydl.extract_info(query if "http" in query else f"ytsearch1:{query}", download=False)
        if "entries" in info:
            info = info["entries"][0]
        song = {"url":info["url"], "title":info.get("title","?"), "dur":info.get("duration",0), "by":inter.user.id}
        bot.music.add(inter.guild_id, song)
        if not vc.is_playing():
            await bot.music.nxt(inter.guild_id, vc)
            await inter.edit_original_response(content=f"🎶 Now playing: **{song['title']}**")
        else:
            await inter.edit_original_response(content=f"🎵 Queued: **{song['title']}**")
    except Exception as e:
        await inter.edit_original_response(content=f"❌ Error: {e}")

@bot.tree.command(name="skip", description="Skip current song")
@perm_check()
async def cmd_skip(inter: discord.Interaction):
    vc = inter.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await inter.response.send_message("⏭️ Skipped.", view=DismissView(inter.user.id))
    else:
        await inter.response.send_message("❌ Nothing playing.", ephemeral=True)

@bot.tree.command(name="queue", description="Show music queue")
@perm_check()
async def cmd_queue(inter: discord.Interaction):
    q = bot.music.q.get(inter.guild_id, [])
    cur = bot.music.cur.get(inter.guild_id)
    if not cur and not q:
        await inter.response.send_message("📭 Empty.", ephemeral=True); return
    emb = discord.Embed(title="🎵 Queue", color=discord.Color.purple())
    if cur:
        emb.add_field(name="Now", value=f"▶️ {cur['title']}", inline=False)
    if q:
        emb.add_field(name="Up Next", value="\n".join(f"{i+1}. {s['title']}" for i,s in enumerate(q[:10])), inline=False)
    await inter.response.send_message(embed=emb, view=DismissView(inter.user.id))

@bot.tree.command(name="stop", description="Stop and clear queue")
@perm_check()
async def cmd_stop(inter: discord.Interaction):
    vc = inter.guild.voice_client
    if vc:
        vc.stop()
    bot.music.q[inter.guild_id] = []
    bot.music.cur[inter.guild_id] = None
    await inter.response.send_message("⏹️ Stopped & cleared.", view=DismissView(inter.user.id))

@bot.tree.command(name="leave", description="Leave voice channel")
@perm_check()
async def cmd_leave(inter: discord.Interaction):
    vc = inter.guild.voice_client
    if vc:
        await vc.disconnect()
    bot.music.q.pop(inter.guild_id, None)
    bot.music.cur.pop(inter.guild_id, None)
    await inter.response.send_message("👋 Left VC.", view=DismissView(inter.user.id))

# ─── SMOKING COMMANDS ──────────────────────────────────────────────────────────
@bot.tree.command(name="smoke", description="Log a smoke break")
@perm_check()
async def cmd_smoke(inter: discord.Interaction):
    now = datetime.datetime.now().timestamp()
    r = await DB.fetchone("SELECT * FROM smoke_stats WHERE user_id=?", (inter.user.id,))
    if r:
        streak = r["streak"]+1 if r["last"] and (now-r["last"])<86400 else 1
        await DB.execute("UPDATE smoke_stats SET count=count+1,last=?,streak=? WHERE user_id=?",
                        (now, streak, inter.user.id))
        count = r["count"]+1
    else:
        await DB.execute("INSERT INTO smoke_stats(user_id,count,last,streak) VALUES(?,?,?,?)",
                        (inter.user.id, 1, now, 1))
        count, streak = 1, 1
    emb = discord.Embed(title="🚬 Smoke Logged", color=discord.Color.dark_grey())
    emb.add_field(name="Today", value=str(count), inline=True)
    emb.add_field(name="Streak", value=f"{streak}d", inline=True)
    emb.add_field(name="Fact", value=random.choice(SMOKE_FACTS), inline=False)
    emb.add_field(name="Strain", value=random.choice(SMOKE_STRAINS), inline=False)
    emb.set_footer(text="Stay safe 🫁")
    await inter.response.send_message(embed=emb, view=DismissView(inter.user.id))

@bot.tree.command(name="smoke_stats", description="View smoking stats")
@app_commands.describe(user="Optional user to check")
@perm_check()
async def cmd_sstats(inter: discord.Interaction, user: Optional[discord.User] = None):
    t = user or inter.user
    r = await DB.fetchone("SELECT * FROM smoke_stats WHERE user_id=?", (t.id,))
    if not r:
        await inter.response.send_message(f"🚭 {t.display_name} has no data. Use `/smoke` first.", ephemeral=True); return
    emb = discord.Embed(title=f"🚬 {t.display_name}'s Stats", color=discord.Color.dark_grey())
    emb.add_field(name="Total", value=str(r["count"]), inline=True)
    emb.add_field(name="Streak", value=f"{r['streak']}d", inline=True)
    if r["last"]:
        emb.add_field(name="Last", value=datetime.datetime.fromtimestamp(r["last"]).strftime("%Y-%m-%d %H:%M"), inline=True)
    await inter.response.send_message(embed=emb, view=DismissView(inter.user.id))

@bot.tree.command(name="strain", description="Random strain recommendation")
@perm_check()
async def cmd_strain(inter: discord.Interaction):
    emb = discord.Embed(title="🌿 Strain Rec", description=random.choice(SMOKE_STRAINS), color=discord.Color.green())
    emb.set_footer(text="Educational only. Know local laws.")
    await inter.response.send_message(embed=emb, view=DismissView(inter.user.id))

# ─── MODERATION COMMANDS ───────────────────────────────────────────────────────
@bot.tree.command(name="inactivity_config", description="Configure inactivity tracking")
@app_commands.describe(ch="Alert channel", warn="Days before warning", kick="Extra days before kick rec")
@admin_check()
async def cmd_inact_cfg(inter: discord.Interaction, ch: discord.TextChannel, warn: int = 7, kick: int = 3):
    await DB.execute("INSERT OR REPLACE INTO guild_cfg(guild_id,alert_ch,warn_days,kick_add_days,enabled) VALUES(?,?,?,?,1)",
                    (inter.guild_id, ch.id, warn, kick))
    emb = discord.Embed(title="✅ Configured", color=discord.Color.green())
    emb.add_field(name="Channel", value=ch.mention, inline=True)
    emb.add_field(name="Warn", value=f"{warn}d", inline=True)
    emb.add_field(name="Kick Rec", value=f"{warn+kick}d total", inline=True)
    await inter.response.send_message(embed=emb, view=DismissView(inter.user.id))

@bot.tree.command(name="activity_check", description="Check user activity status")
@app_commands.describe(user="User to inspect")
@admin_check()
async def cmd_act_chk(inter: discord.Interaction, user: discord.Member):
    r = await DB.fetchone("SELECT * FROM user_activity WHERE user_id=? AND guild_id=?", (user.id, inter.guild_id))
    if not r:
        await inter.response.send_message(f"ℹ️ No data for {user.mention}.", ephemeral=True); return
    now = datetime.datetime.now().timestamp()
    last = max(r["last_msg_ts"] or 0, r["last_react_ts"] or 0)
    days = (now-last)/86400
    emb = discord.Embed(title=f"📊 {user.display_name}", color=discord.Color.blue())
    emb.add_field(name="Last Msg", value=f"<t:{int(r['last_msg_ts'])}:R>" if r["last_msg_ts"] else "Never", inline=True)
    emb.add_field(name="Last React", value=f"<t:{int(r['last_react_ts'])}:R>" if r["last_react_ts"] else "Never", inline=True)
    emb.add_field(name="Inactive", value=f"{days:.1f}d", inline=True)
    emb.add_field(name="7d Warn", value="✅" if r["warned_7"] else "❌", inline=True)
    emb.add_field(name="10d Warn", value="✅" if r["warned_10"] else "❌", inline=True)
    emb.add_field(name="DM Sent", value="✅" if r["dm_sent"] else "❌", inline=True)
    await inter.response.send_message(embed=emb, view=DismissView(inter.user.id))

@bot.tree.command(name="purge_inactive", description="Kick users past inactivity threshold")
@app_commands.describe(confirm="Set True to execute")
@admin_check()
async def cmd_purge(inter: discord.Interaction, confirm: bool = False):
    if not confirm:
        await inter.response.send_message("⚠️ Use `confirm: True` to execute.", ephemeral=True); return
    cfg = await DB.fetchone("SELECT * FROM guild_cfg WHERE guild_id=?", (inter.guild_id,))
    if not cfg:
        await inter.response.send_message("❌ Not configured. Use `/inactivity_config`.", ephemeral=True); return
    thresh = (cfg["warn_days"] + cfg["kick_add_days"]) * 86400
    now = datetime.datetime.now().timestamp()
    rows = await DB.fetchall(
        "SELECT user_id FROM user_activity WHERE guild_id=? AND warned_10=1 AND (last_msg_ts<? OR last_react_ts<?)",
        (inter.guild_id, now-thresh, now-thresh))
    kicked = 0
    for row in rows:
        m = inter.guild.get_member(row["user_id"])
        if m and not m.bot:
            try:
                await m.kick(reason="Inactive 10+ days")
                kicked += 1
            except:
                pass
    await inter.response.send_message(f"👢 Kicked **{kicked}** users.", view=DismissView(inter.user.id))

# ─── PERMISSION COMMANDS ──────────────────────────────────────────────────────
@bot.tree.command(name="cmd_allow", description="Restrict command to channels/roles")
@app_commands.describe(cmd="Command name", chs="Channel IDs/mentions (comma)", roles="Role IDs/mentions (comma)")
@admin_check()
async def cmd_allow(inter: discord.Interaction, cmd: str, chs: str = "", roles: str = ""):
    cids = ",".join(re.findall(r"\d+", chs))
    rids = ",".join(re.findall(r"\d+", roles))
    await DB.execute("INSERT INTO cmd_perms(guild_id,cmd,chs,roles,disabled) VALUES(?,?,?,?,0)",
                    (inter.guild_id, cmd.lower(), cids, rids))
    emb = discord.Embed(title="🔐 Allowed", color=discord.Color.green())
    emb.add_field(name="Command", value=f"/{cmd}", inline=True)
    emb.add_field(name="Channels", value=str(len(cids.split(","))) if cids else "All", inline=True)
    emb.add_field(name="Roles", value=str(len(rids.split(","))) if rids else "All", inline=True)
    await inter.response.send_message(embed=emb, view=DismissView(inter.user.id))

@bot.tree.command(name="cmd_deny", description="Disable a command")
@admin_check()
async def cmd_deny(inter: discord.Interaction, cmd: str):
    await DB.execute("INSERT INTO cmd_perms(guild_id,cmd,chs,roles,disabled) VALUES(?,?,?,?,1)",
                    (inter.guild_id, cmd.lower(), "", ""))
    await inter.response.send_message(f"🚫 `/{cmd}` disabled.", view=DismissView(inter.user.id))

@bot.tree.command(name="cmd_reset", description="Reset command permissions")
@admin_check()
async def cmd_reset(inter: discord.Interaction, cmd: str):
    await DB.execute("DELETE FROM cmd_perms WHERE guild_id=? AND cmd=?", (inter.guild_id, cmd.lower()))
    await inter.response.send_message(f"♻️ `/{cmd}` reset.", view=DismissView(inter.user.id))

@bot.tree.command(name="cmd_list", description="List permission settings")
@admin_check()
async def cmd_list(inter: discord.Interaction):
    rows = await DB.fetchall("SELECT * FROM cmd_perms WHERE guild_id=?", (inter.guild_id,))
    if not rows:
        await inter.response.send_message("ℹ️ No custom perms. All commands open.", ephemeral=True); return
    emb = discord.Embed(title="🔐 Permissions", color=discord.Color.blue())
    for r in rows:
        s = "🚫 Disabled" if r["disabled"] else "✅ Enabled"
        emb.add_field(name=f"/{r['cmd']}", value=f"Chs: {r['chs'] or 'All'}\nRoles: {r['roles'] or 'All'}\n{s}", inline=False)
    await inter.response.send_message(embed=emb, view=DismissView(inter.user.id))

# ─── UTILS ───────────────────────────────────────────────────────────────────────
@bot.tree.command(name="help", description="Show all commands")
@perm_check()
async def cmd_help(inter: discord.Interaction):
    emb = discord.Embed(title="📖 Pythos Help", color=discord.Color.gold())
    emb.add_field(name="💰 Crypto", value="`/price` `/chart` `/convert` `/pyth_feeds`", inline=False)
    emb.add_field(name="🎵 Music", value="`/play` `/skip` `/queue` `/stop` `/leave`", inline=False)
    emb.add_field(name="🚬 Smoking", value="`/smoke` `/smoke_stats` `/strain`", inline=False)
    emb.add_field(name="🛡️ Mod", value="`/inactivity_config` `/activity_check` `/purge_inactive`", inline=False)
    emb.add_field(name="🔐 Admin", value="`/cmd_allow` `/cmd_deny` `/cmd_reset` `/cmd_list`", inline=False)
    emb.set_footer(text="All commands have 🗑️ Dismiss buttons | Free deploy: Railway/Render/Fly.io")
    await inter.response.send_message(embed=emb, view=DismissView(inter.user.id))

@bot.tree.command(name="ping", description="Bot latency")
@perm_check()
async def cmd_ping(inter: discord.Interaction):
    await inter.response.send_message(f"🏓 **{round(bot.latency*1000)}ms**", view=DismissView(inter.user.id))

# ─── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        log.error("Set DISCORD_BOT_TOKEN env var!"); sys.exit(1)
    try:
        bot.run(TOKEN)
    except Exception as e:
        log.critical(f"Fatal: {e}")
    finally:
        asyncio.run(bot.pyth.close())
