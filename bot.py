"""
╔══════════════════════════════════════════════════════════════╗
║          ULTIMATE DISCORD BOT - Single File Edition          ║
║   Crypto • Commodities • Music • Activity • Smoking • Charts ║
╚══════════════════════════════════════════════════════════════╝

Deploy on Railway: Set BOT_TOKEN env var and run this file.
All features in one file. No external config needed.
"""

import os, sys, asyncio, json, time, random, io, math, datetime, traceback, re
from typing import Optional
from collections import defaultdict
import aiohttp
import discord
from discord.ext import commands, tasks
from discord import app_commands
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ─────────────────────────────────────────────
# CONFIGURATION — edit these or use env vars
# ─────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))          # Your Discord user ID
INACTIVITY_CHANNEL_ID = int(os.getenv("INACTIVITY_CHANNEL_ID", "0"))  # Channel for alerts
INACTIVITY_DAYS = 7        # Days before first warning
PURGE_DAYS = 3             # Extra days before kick notification
PREFIX = "/"

# Coin ID map: symbol → CoinGecko ID
COIN_MAP = {
    "btc": "bitcoin", "eth": "ethereum", "sol": "solana", "bnb": "binancecoin",
    "xrp": "ripple", "ada": "cardano", "doge": "dogecoin", "avax": "avalanche-2",
    "dot": "polkadot", "matic": "matic-network", "link": "chainlink", "ltc": "litecoin",
    "uni": "uniswap", "atom": "cosmos", "xlm": "stellar", "etc": "ethereum-classic",
    "near": "near", "algo": "algorand", "icp": "internet-computer", "apt": "aptos",
    "arb": "arbitrum", "op": "optimism", "sui": "sui", "sei": "sei-network",
    "tia": "celestia", "inj": "injective-protocol", "jup": "jupiter-ag",
    "wif": "dogwifcoin", "bonk": "bonk", "pepe": "pepe", "floki": "floki",
    "shib": "shiba-inu", "sand": "the-sandbox", "mana": "decentraland",
    "axs": "axie-infinity", "gala": "gala", "imx": "immutable-x",
    "rune": "thorchain", "fet": "fetch-ai", "ocean": "ocean-protocol",
    "rndr": "render-token", "grt": "the-graph", "ldo": "lido-dao",
    "mkr": "maker", "aave": "aave", "crv": "curve-dao-token", "snx": "havven",
    "comp": "compound-governance-token", "bal": "balancer", "sushi": "sushi",
    "cake": "pancakeswap-token", "1inch": "1inch", "zrx": "0x",
    "trx": "tron", "hbar": "hedera-hashgraph", "fil": "filecoin",
    "vet": "vechain", "egld": "elrond-erd-2", "theta": "theta-token",
    "ftm": "fantom", "cro": "crypto-com-chain", "klay": "klay-token",
    "flow": "flow", "mina": "mina-protocol", "cfx": "conflux-token",
    "kas": "kaspa", "blur": "blur", "magic": "magic", "lrc": "loopring",
    "dydx": "dydx", "gmx": "gmx", "hyperliquid": "hyperliquid",
    "wld": "worldcoin-wld", "pyth": "pyth-network", "jto": "jito-governance-token",
    "wen": "wen-4", "bome": "book-of-meme", "slerf": "slerf",
    "tnsr": "tensor", "io": "io-net", "zk": "zksync",
    "strk": "starknet", "alt": "altlayer", "eigen": "eigenlayer",
    "pixel": "pixels", "portal": "portal-fantasy", "nyan": "nyan-cat",
    "pendle": "pendle", "ethfi": "ether-fi", "renzo": "renzo",
    "puffer": "puffer-finance", "ageth": "kelp-dao-restaked-eth",
    # New/Trending 2024-2025
    "monad": "monad", "megaeth": "megaeth", "berachain": "bera",
    "bera": "berachain-bera", "sonic": "sonic-3", "abstract": "abstract",
    "story": "story-2", "movement": "movement-2", "eclipse": "eclipse-2",
    "initia": "initia", "humanity": "humanity-protocol", "grass": "grass",
    "drift": "drift-protocol", "kamino": "kamino", "marginfi": "marginfi",
    "zeta": "zeta-chain", "taiko": "taiko", "scroll": "scroll-token",
    "linea": "linea", "base": "base-protocol", "mode": "mode",
    "manta": "manta-network", "blast": "blast-2", "merlin": "merlin-chain",
    "bvm": "bitcoin-virtual-machine", "ordi": "ordinals", "sats": "1000sats-ordinals",
    "rats": "rats-ordinals", "agi": "delysium", "myro": "myro",
    "pnut": "peanut-the-squirrel", "goat": "goat", "act": "act-i-the-ai-prophecy",
    "zerebro": "zerebro", "ai16z": "ai16z", "virtual": "virtual-protocol",
    "aixbt": "aixbt-by-virtuals", "luna": "terra-luna-2", "lunc": "terra-luna",
    "usdt": "tether", "usdc": "usd-coin", "dai": "dai", "frax": "frax",
    "busd": "binance-usd", "tusd": "true-usd",
}

COMMODITY_MAP = {
    "gold": ("XAU", "Gold"),
    "silver": ("XAG", "Silver"),
    "oil": ("OIL", "Crude Oil"),
    "gas": ("GAS", "Natural Gas"),
    "platinum": ("XPT", "Platinum"),
    "palladium": ("XPD", "Palladium"),
    "copper": ("COPPER", "Copper"),
    "wheat": ("WHEAT", "Wheat"),
    "corn": ("CORN", "Corn"),
}

# Smoking facts/tips database
SMOKING_DATA = {
    "facts": [
        "🚬 Smoking kills ~8 million people per year globally (WHO 2024)",
        "💨 Cigarette smoke contains 7,000+ chemicals; 250 harmful; 69 carcinogenic",
        "❤️ After 20 minutes of quitting: heart rate & blood pressure drop",
        "🫁 After 1 year: heart disease risk cut in HALF",
        "💰 Average smoker spends $2,500–$5,000/year on cigarettes",
        "🧠 Nicotine reaches brain in 10 seconds — faster than IV drugs",
        "🔬 Secondhand smoke causes 1.3M deaths annually worldwide",
        "⏳ Each cigarette cuts ~11 minutes from your life",
        "🌍 1.3 billion people smoke globally — declining each year",
        "💪 Vaping/e-cigs still deliver nicotine and may cause lung damage",
    ],
    "quit_tips": [
        "💡 Set a quit date and stick to it — commitment is step one",
        "🍬 Use nicotine replacement therapy (patches, gum, lozenges)",
        "📱 Download a quit-smoking app to track progress & savings",
        "🏃 Exercise when cravings hit — dopamine beats nicotine cravings",
        "💧 Drink water slowly when cravings come — they pass in 3-5 mins",
        "🧘 Practice deep breathing: inhale 4s, hold 4s, exhale 4s",
        "📞 Call a quit line: US: 1-800-QUIT-NOW | UK: 0300 123 1044",
        "🫂 Tell friends/family — social support doubles quit success",
        "🚫 Avoid triggers: alcohol, coffee, stress situations initially",
        "🏆 Reward yourself with money saved — track it daily",
    ],
    "damage_timeline": {
        "20 min": "Heart rate & BP normalize",
        "12 hrs": "CO levels in blood normalize",
        "2 weeks": "Circulation & lung function improve",
        "1 month": "Coughing & shortness of breath reduce",
        "1 year": "Heart disease risk halved vs smoker",
        "5 years": "Stroke risk equals non-smoker",
        "10 years": "Lung cancer risk halved",
        "15 years": "Heart disease risk equals non-smoker",
    }
}

# ─────────────────────────────────────────────
# IN-MEMORY STATE (persists until bot restarts)
# ─────────────────────────────────────────────
# {user_id: last_active_timestamp}
user_last_active = {}
# {user_id: {"warned": bool, "warned_at": ts}}
inactivity_warned = {}
# {guild_id: {"channel_restrictions": {cmd: [channel_ids]}, "role_restrictions": {cmd: [role_ids]}}}
guild_settings = defaultdict(lambda: {"channel_restrictions": {}, "role_restrictions": {}})
# Pending purge confirmations: {user_id: {"target_id": int, "guild_id": int}}
pending_purge = {}
# Music queues: {guild_id: [url, ...]}
music_queues = defaultdict(list)
# Smoking quit trackers: {user_id: {"quit_time": ts, "cigs_per_day": int}}
quit_trackers = {}

# ─────────────────────────────────────────────
# BOT SETUP
# ─────────────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
tree = bot.tree

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def now_ts():
    return time.time()

def fmt_price(p):
    if p is None: return "N/A"
    if p >= 1000: return f"${p:,.2f}"
    if p >= 1: return f"${p:.4f}"
    if p >= 0.001: return f"${p:.6f}"
    return f"${p:.8f}"

def fmt_change(c):
    if c is None: return "N/A"
    sign = "▲" if c >= 0 else "▼"
    color = "🟢" if c >= 0 else "🔴"
    return f"{color} {sign} {abs(c):.2f}%"

def pct_color(c):
    if c is None: return 0x808080
    return 0x00ff88 if c >= 0 else 0xff4444

async def fetch_json(url, params=None):
    async with aiohttp.ClientSession() as s:
        async with s.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
            return await r.json()

def check_cmd_allowed(interaction: discord.Interaction, cmd_name: str) -> bool:
    """Check if command is allowed in channel and for user's roles."""
    gid = str(interaction.guild_id)
    settings = guild_settings[gid]
    
    ch_restrictions = settings["channel_restrictions"].get(cmd_name, [])
    if ch_restrictions and interaction.channel_id not in ch_restrictions:
        return False
    
    role_restrictions = settings["role_restrictions"].get(cmd_name, [])
    if role_restrictions:
        user_role_ids = [r.id for r in interaction.user.roles]
        if not any(rid in user_role_ids for rid in role_restrictions):
            return False
    return True

def make_dismiss_view():
    """Returns a View with a Dismiss button."""
    view = discord.ui.View(timeout=300)
    btn = discord.ui.Button(label="✖ Dismiss", style=discord.ButtonStyle.secondary, custom_id="dismiss")
    async def dismiss_cb(i: discord.Interaction):
        await i.message.delete()
    btn.callback = dismiss_cb
    view.add_item(btn)
    return view

async def send_ephemeral_err(interaction, msg):
    await interaction.followup.send(f"❌ {msg}", ephemeral=True)

# ─────────────────────────────────────────────
# CHART GENERATION
# ─────────────────────────────────────────────
async def get_crypto_chart(coin_id: str, days: int = 7) -> Optional[io.BytesIO]:
    """Fetch price history and return a chart as BytesIO."""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        data = await fetch_json(url, {"vs_currency": "usd", "days": days, "interval": "daily" if days > 1 else "hourly"})
        prices = data.get("prices", [])
        if not prices: return None

        timestamps = [datetime.datetime.fromtimestamp(p[0]/1000) for p in prices]
        values = [p[1] for p in prices]

        fig, ax = plt.subplots(figsize=(10, 4), facecolor="#0f1117")
        ax.set_facecolor("#0f1117")

        # Gradient fill
        ax.plot(timestamps, values, color="#00ff88", linewidth=2, zorder=5)
        ax.fill_between(timestamps, values, min(values)*0.99, alpha=0.3, color="#00ff88")

        # Styling
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.tick_params(colors="#aaaaaa", labelsize=8)
        ax.spines[:].set_color("#333333")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: fmt_price(x)))
        ax.set_title(f"{coin_id.upper()} — {days}d Price Chart", color="white", fontsize=12, pad=10)
        ax.grid(True, color="#222222", linewidth=0.5, linestyle="--")

        # Price change badge
        change = ((values[-1] - values[0]) / values[0]) * 100
        color = "#00ff88" if change >= 0 else "#ff4444"
        ax.annotate(f"{'▲' if change >= 0 else '▼'} {abs(change):.2f}%",
                    xy=(0.02, 0.93), xycoords='axes fraction',
                    color=color, fontsize=10, fontweight="bold")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Chart error: {e}")
        return None

# ─────────────────────────────────────────────
# CRYPTO PRICE FETCHING
# ─────────────────────────────────────────────
async def fetch_crypto_price(symbol: str):
    """Returns dict with price info or None."""
    sym = symbol.lower().strip()
    coin_id = COIN_MAP.get(sym, sym)  # fallback: treat symbol as coin id directly
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        data = await fetch_json(url, {
            "vs_currency": "usd",
            "ids": coin_id,
            "price_change_percentage": "1h,24h,7d",
        })
        if data and len(data) > 0:
            d = data[0]
            return {
                "id": d.get("id"),
                "name": d.get("name"),
                "symbol": d.get("symbol", "").upper(),
                "price": d.get("current_price"),
                "change_1h": d.get("price_change_percentage_1h_in_currency"),
                "change_24h": d.get("price_change_percentage_24h"),
                "change_7d": d.get("price_change_percentage_7d_in_currency"),
                "market_cap": d.get("market_cap"),
                "volume": d.get("total_volume"),
                "high_24h": d.get("high_24h"),
                "low_24h": d.get("low_24h"),
                "rank": d.get("market_cap_rank"),
                "ath": d.get("ath"),
                "image": d.get("image"),
            }
    except Exception as e:
        print(f"Price fetch error for {symbol}: {e}")
    return None

async def fetch_commodity_price(symbol: str):
    """Fetch commodity price via open metals/fiat API."""
    try:
        # Use frankfurter or metals-api public endpoint
        url = f"https://api.metals.live/v1/spot/{symbol.lower()}"
        data = await fetch_json(url)
        if isinstance(data, list) and data:
            entry = data[0]
            price = list(entry.values())[0] if entry else None
            return price
    except:
        pass
    # Fallback: approximate static data + note
    fallback = {"XAU": 3320.0, "XAG": 32.5, "XPT": 980.0, "XPD": 970.0}
    return fallback.get(symbol)

# ─────────────────────────────────────────────
# ACTIVITY TRACKING
# ─────────────────────────────────────────────
def record_activity(user_id: int):
    user_last_active[user_id] = now_ts()
    # Clear warned status if user becomes active again
    if user_id in inactivity_warned:
        del inactivity_warned[user_id]

@bot.event
async def on_message(msg):
    if msg.author.bot: return
    record_activity(msg.author.id)
    await bot.process_commands(msg)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot: return
    record_activity(user.id)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot: return
    if after.channel:
        record_activity(member.id)

# ─────────────────────────────────────────────
# BACKGROUND TASKS
# ─────────────────────────────────────────────
@tasks.loop(hours=12)
async def check_inactivity():
    """Every 12h, scan all tracked users for inactivity."""
    if not INACTIVITY_CHANNEL_ID:
        return
    
    now = now_ts()
    warn_threshold = INACTIVITY_DAYS * 86400
    purge_threshold = (INACTIVITY_DAYS + PURGE_DAYS) * 86400
    alert_ch = bot.get_channel(INACTIVITY_CHANNEL_ID)
    if not alert_ch:
        return

    for uid, last in list(user_last_active.items()):
        elapsed = now - last
        warned_data = inactivity_warned.get(uid, {})

        if elapsed >= purge_threshold and warned_data.get("warned"):
            # Send kick notification
            user = bot.get_user(uid)
            uname = f"<@{uid}>" if not user else f"**{user.name}** (<@{uid}>)"
            embed = discord.Embed(
                title="⚠️ PURGE ALERT — Extended Inactivity",
                description=f"{uname} has been inactive for **{int(elapsed/86400)} days** ({INACTIVITY_DAYS + PURGE_DAYS}+ days total).\n\nReact ✅ to confirm kick or ❌ to dismiss.",
                color=0xff2222,
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(text="Admin: Confirm kick or dismiss")
            view = PurgeConfirmView(uid)
            msg = await alert_ch.send(content=f"<@{ADMIN_USER_ID}> 🚨", embed=embed, view=view)
            # Also DM admin
            if ADMIN_USER_ID:
                try:
                    admin = await bot.fetch_user(ADMIN_USER_ID)
                    await admin.send(f"🚨 **PURGE ALERT**: User <@{uid}> has been inactive for {int(elapsed/86400)} days in your server. Check #{alert_ch.name} to confirm kick.")
                except:
                    pass

        elif elapsed >= warn_threshold and not warned_data.get("warned"):
            # First warning
            user = bot.get_user(uid)
            uname = f"<@{uid}>" if not user else f"**{user.name}** (<@{uid}>)"
            embed = discord.Embed(
                title="💤 Inactivity Alert",
                description=f"{uname} has been inactive for **{int(elapsed/86400)} days**.\n\nIf no activity in **{PURGE_DAYS} more days**, a purge notification will be sent.",
                color=0xffaa00,
                timestamp=datetime.datetime.utcnow()
            )
            view = make_dismiss_view()
            await alert_ch.send(embed=embed, view=view)
            inactivity_warned[uid] = {"warned": True, "warned_at": now}

class PurgeConfirmView(discord.ui.View):
    def __init__(self, target_id: int):
        super().__init__(timeout=86400)
        self.target_id = target_id

    @discord.ui.button(label="✅ Confirm Kick", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != ADMIN_USER_ID and not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ Only admins can confirm kicks.", ephemeral=True)
            return
        try:
            member = interaction.guild.get_member(self.target_id)
            if member:
                await member.send(f"You have been removed from **{interaction.guild.name}** due to extended inactivity ({INACTIVITY_DAYS + PURGE_DAYS}+ days).")
                await member.kick(reason="Extended inactivity")
                await interaction.response.send_message(f"✅ <@{self.target_id}> has been kicked.", ephemeral=False)
            else:
                await interaction.response.send_message("⚠️ Member not found (may have already left).", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to kick: {e}", ephemeral=True)
        self.stop()

    @discord.ui.button(label="❌ Dismiss", style=discord.ButtonStyle.secondary)
    async def dismiss(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        self.stop()

    @discord.ui.button(label="📩 DM Warning First", style=discord.ButtonStyle.primary)
    async def dm_warn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            user = await bot.fetch_user(self.target_id)
            await user.send(
                f"⚠️ **Activity Warning** from **{interaction.guild.name}**\n\n"
                f"You have been flagged for inactivity. Please engage in the server to avoid being removed."
            )
            await interaction.response.send_message(f"📩 DM sent to <@{self.target_id}>.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Could not DM user: {e}", ephemeral=True)

# ─────────────────────────────────────────────
# MUSIC PLAYER
# ─────────────────────────────────────────────
class MusicView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="⏭ Skip", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭ Skipped!", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing playing.", ephemeral=True)

    @discord.ui.button(label="⏹ Stop", style=discord.ButtonStyle.danger)
    async def stop_music(self, interaction: discord.Interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            music_queues[self.guild_id].clear()
            vc.stop()
            await vc.disconnect()
            await interaction.response.send_message("⏹ Stopped & disconnected.", ephemeral=True)
        else:
            await interaction.response.send_message("Not in a voice channel.", ephemeral=True)

    @discord.ui.button(label="📋 Queue", style=discord.ButtonStyle.secondary)
    async def show_queue(self, interaction: discord.Interaction, button):
        q = music_queues[self.guild_id]
        if not q:
            await interaction.response.send_message("Queue is empty.", ephemeral=True)
        else:
            items = "\n".join(f"`{i+1}.` {url[:60]}..." for i, url in enumerate(q[:10]))
            await interaction.response.send_message(f"📋 **Queue ({len(q)} tracks):**\n{items}", ephemeral=True)

    @discord.ui.button(label="✖ Dismiss", style=discord.ButtonStyle.secondary)
    async def dismiss(self, interaction: discord.Interaction, button):
        await interaction.message.delete()

async def play_next(guild: discord.Guild):
    gid = guild.id
    q = music_queues[gid]
    if not q:
        return
    url = q.pop(0)
    vc = guild.voice_client
    if not vc or not vc.is_connected():
        return
    try:
        import yt_dlp
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "default_search": "ytsearch",
            "source_address": "0.0.0.0",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if "entries" in info:
                info = info["entries"][0]
            audio_url = info["url"]
            title = info.get("title", url)

        source = discord.FFmpegPCMAudio(
            audio_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn"
        )

        def after_play(err):
            if err: print(f"Player error: {err}")
            asyncio.run_coroutine_threadsafe(play_next(guild), bot.loop)

        vc.play(source, after=after_play)
        return title
    except Exception as e:
        print(f"Music error: {e}")
        await play_next(guild)
        return None

# ─────────────────────────────────────────────
# SLASH COMMANDS — CRYPTO
# ─────────────────────────────────────────────
@tree.command(name="price", description="💰 Get real-time price of any crypto (e.g. BTC, ETH, SOL)")
@app_commands.describe(symbol="Coin symbol or name (e.g. btc, eth, monad, megaeth)")
async def cmd_price(interaction: discord.Interaction, symbol: str):
    if not check_cmd_allowed(interaction, "price"):
        await interaction.response.send_message("❌ This command is not allowed here.", ephemeral=True)
        return
    await interaction.response.defer()
    data = await fetch_crypto_price(symbol)
    if not data:
        await send_ephemeral_err(interaction, f"Could not find `{symbol}`. Try a full name or check CoinGecko ID.")
        return

    embed = discord.Embed(
        title=f"{data['name']} ({data['symbol']})",
        description=f"# {fmt_price(data['price'])}",
        color=pct_color(data['change_24h']),
        timestamp=datetime.datetime.utcnow()
    )
    if data.get("image"):
        embed.set_thumbnail(url=data["image"])
    embed.add_field(name="1h", value=fmt_change(data['change_1h']), inline=True)
    embed.add_field(name="24h", value=fmt_change(data['change_24h']), inline=True)
    embed.add_field(name="7d", value=fmt_change(data['change_7d']), inline=True)
    if data['market_cap']:
        embed.add_field(name="Market Cap", value=f"${data['market_cap']:,.0f}", inline=True)
    if data['volume']:
        embed.add_field(name="24h Volume", value=f"${data['volume']:,.0f}", inline=True)
    if data['rank']:
        embed.add_field(name="CMC Rank", value=f"#{data['rank']}", inline=True)
    if data['high_24h'] and data['low_24h']:
        embed.add_field(name="24h High / Low", value=f"{fmt_price(data['high_24h'])} / {fmt_price(data['low_24h'])}", inline=False)
    if data['ath']:
        embed.add_field(name="All-Time High", value=fmt_price(data['ath']), inline=True)
    embed.set_footer(text="Data: CoinGecko • Updates every ~60s")
    await interaction.followup.send(embed=embed, view=make_dismiss_view())

@tree.command(name="chart", description="📈 Get real-time price chart for any crypto")
@app_commands.describe(symbol="Coin symbol (btc, eth, sol...)", days="Days of history (1, 7, 30, 90, 365)")
async def cmd_chart(interaction: discord.Interaction, symbol: str, days: int = 7):
    if not check_cmd_allowed(interaction, "chart"):
        await interaction.response.send_message("❌ Not allowed here.", ephemeral=True)
        return
    await interaction.response.defer()
    sym = symbol.lower()
    coin_id = COIN_MAP.get(sym, sym)
    chart_buf = await get_crypto_chart(coin_id, min(max(days, 1), 365))
    if not chart_buf:
        await send_ephemeral_err(interaction, f"No chart data for `{symbol}`.")
        return
    file = discord.File(chart_buf, filename=f"{sym}_chart.png")
    embed = discord.Embed(title=f"📈 {symbol.upper()} — {days}d Chart", color=0x00ff88)
    embed.set_image(url=f"attachment://{sym}_chart.png")
    embed.set_footer(text="Data: CoinGecko")
    await interaction.followup.send(embed=embed, file=file, view=make_dismiss_view())

@tree.command(name="top", description="🏆 Top N cryptocurrencies by market cap")
@app_commands.describe(count="How many coins to show (max 20)")
async def cmd_top(interaction: discord.Interaction, count: int = 10):
    if not check_cmd_allowed(interaction, "top"):
        await interaction.response.send_message("❌ Not allowed here.", ephemeral=True)
        return
    await interaction.response.defer()
    count = min(max(count, 1), 20)
    try:
        data = await fetch_json("https://api.coingecko.com/api/v3/coins/markets", {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": count,
            "page": 1,
            "price_change_percentage": "24h",
        })
        embed = discord.Embed(title=f"🏆 Top {count} Cryptos by Market Cap", color=0xf7931a, timestamp=datetime.datetime.utcnow())
        rows = []
        for i, c in enumerate(data, 1):
            chg = c.get("price_change_percentage_24h") or 0
            arrow = "🟢▲" if chg >= 0 else "🔴▼"
            rows.append(f"**#{i}** {c['name']} `{c['symbol'].upper()}` — {fmt_price(c['current_price'])} {arrow} {abs(chg):.2f}%")
        embed.description = "\n".join(rows)
        embed.set_footer(text="CoinGecko • Real-time data")
        await interaction.followup.send(embed=embed, view=make_dismiss_view())
    except Exception as e:
        await send_ephemeral_err(interaction, f"API error: {e}")

@tree.command(name="compare", description="⚖️ Compare two cryptocurrencies side-by-side")
@app_commands.describe(coin1="First coin symbol", coin2="Second coin symbol")
async def cmd_compare(interaction: discord.Interaction, coin1: str, coin2: str):
    await interaction.response.defer()
    d1, d2 = await asyncio.gather(fetch_crypto_price(coin1), fetch_crypto_price(coin2))
    if not d1 or not d2:
        await send_ephemeral_err(interaction, "Could not fetch one or both coins.")
        return
    embed = discord.Embed(title=f"⚖️ {d1['name']} vs {d2['name']}", color=0x7289da, timestamp=datetime.datetime.utcnow())
    fields = [
        ("Price", fmt_price(d1['price']), fmt_price(d2['price'])),
        ("24h Change", fmt_change(d1['change_24h']), fmt_change(d2['change_24h'])),
        ("7d Change", fmt_change(d1['change_7d']), fmt_change(d2['change_7d'])),
        ("Market Cap", f"${d1['market_cap']:,.0f}" if d1['market_cap'] else "N/A", f"${d2['market_cap']:,.0f}" if d2['market_cap'] else "N/A"),
        ("Rank", f"#{d1['rank']}" if d1['rank'] else "N/A", f"#{d2['rank']}" if d2['rank'] else "N/A"),
    ]
    for name, v1, v2 in fields:
        embed.add_field(name=f"📊 {name}", value=f"**{d1['symbol']}:** {v1}\n**{d2['symbol']}:** {v2}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
    await interaction.followup.send(embed=embed, view=make_dismiss_view())

@tree.command(name="trending", description="🔥 Get trending coins on CoinGecko right now")
async def cmd_trending(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        data = await fetch_json("https://api.coingecko.com/api/v3/search/trending")
        coins = data.get("coins", [])[:10]
        embed = discord.Embed(title="🔥 Trending Cryptos (CoinGecko)", color=0xff6600, timestamp=datetime.datetime.utcnow())
        rows = []
        for i, item in enumerate(coins, 1):
            c = item["item"]
            rows.append(f"**#{i}** {c['name']} `{c['symbol']}` — Rank #{c.get('market_cap_rank', 'N/A')}")
        embed.description = "\n".join(rows)
        await interaction.followup.send(embed=embed, view=make_dismiss_view())
    except Exception as e:
        await send_ephemeral_err(interaction, str(e))

@tree.command(name="fomo", description="😱 FOMO check — what if you bought X ago?")
@app_commands.describe(symbol="Coin symbol", amount_usd="USD invested", days_ago="Days ago you would have bought")
async def cmd_fomo(interaction: discord.Interaction, symbol: str, amount_usd: float, days_ago: int):
    await interaction.response.defer()
    sym = symbol.lower()
    coin_id = COIN_MAP.get(sym, sym)
    try:
        date_str = (datetime.datetime.utcnow() - datetime.timedelta(days=days_ago)).strftime("%d-%m-%Y")
        hist = await fetch_json(f"https://api.coingecko.com/api/v3/coins/{coin_id}/history", {"date": date_str})
        past_price = hist.get("market_data", {}).get("current_price", {}).get("usd")
        current = await fetch_crypto_price(symbol)
        if not past_price or not current:
            await send_ephemeral_err(interaction, "Could not fetch historical data.")
            return
        coins_bought = amount_usd / past_price
        current_value = coins_bought * current['price']
        profit = current_value - amount_usd
        pct = ((current_value - amount_usd) / amount_usd) * 100
        embed = discord.Embed(
            title=f"😱 FOMO Calculator — {current['name']}",
            color=0x00ff88 if profit >= 0 else 0xff4444,
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="💵 Invested", value=f"${amount_usd:,.2f}", inline=True)
        embed.add_field(name="📅 Days Ago", value=f"{days_ago} days", inline=True)
        embed.add_field(name="💰 Price Then", value=fmt_price(past_price), inline=True)
        embed.add_field(name="📈 Price Now", value=fmt_price(current['price']), inline=True)
        embed.add_field(name="🪙 Coins Bought", value=f"{coins_bought:.6f}", inline=True)
        embed.add_field(name="💎 Value Now", value=f"${current_value:,.2f}", inline=True)
        embed.add_field(
            name="🚀 P&L",
            value=f"{'🟢 +' if profit >= 0 else '🔴 -'}${abs(profit):,.2f} ({'▲' if pct >= 0 else '▼'}{abs(pct):.2f}%)",
            inline=False
        )
        await interaction.followup.send(embed=embed, view=make_dismiss_view())
    except Exception as e:
        await send_ephemeral_err(interaction, str(e))

# ─────────────────────────────────────────────
# COMMODITIES
# ─────────────────────────────────────────────
@tree.command(name="commodity", description="🥇 Get price of gold, silver, oil, platinum, etc.")
@app_commands.describe(item="Commodity name: gold, silver, oil, platinum, palladium, copper, wheat, corn")
async def cmd_commodity(interaction: discord.Interaction, item: str):
    await interaction.response.defer()
    key = item.lower().strip()
    info = COMMODITY_MAP.get(key)
    if not info:
        keys = ", ".join(COMMODITY_MAP.keys())
        await send_ephemeral_err(interaction, f"Unknown commodity. Available: {keys}")
        return
    symbol, name = info
    price = await fetch_commodity_price(symbol)
    embed = discord.Embed(title=f"{'🥇' if key=='gold' else '🥈' if key=='silver' else '🛢️' if key=='oil' else '⚙️'} {name}", color=0xFFD700 if key == "gold" else 0xC0C0C0)
    if price:
        embed.description = f"# ${price:,.2f} / oz"
        embed.set_footer(text="⚠️ Approximate price — connect to a live metals API for precision")
    else:
        embed.description = "Price unavailable — metals API rate limited. Try again shortly."
    await interaction.followup.send(embed=embed, view=make_dismiss_view())

# ─────────────────────────────────────────────
# MUSIC
# ─────────────────────────────────────────────
@tree.command(name="play", description="🎵 Play a song in your voice channel (YouTube URL or search)")
@app_commands.describe(query="Song name or YouTube URL")
async def cmd_play(interaction: discord.Interaction, query: str):
    if not check_cmd_allowed(interaction, "play"):
        await interaction.response.send_message("❌ Not allowed here.", ephemeral=True)
        return
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Join a voice channel first!", ephemeral=True)
        return
    await interaction.response.defer()
    vc = interaction.guild.voice_client
    if not vc:
        vc = await interaction.user.voice.channel.connect()
    elif vc.channel != interaction.user.voice.channel:
        await vc.move_to(interaction.user.voice.channel)

    gid = interaction.guild_id
    music_queues[gid].append(query)

    if not vc.is_playing():
        title = await play_next(interaction.guild)
        embed = discord.Embed(title="🎵 Now Playing", description=f"`{title or query}`", color=0x1db954)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.followup.send(embed=embed, view=MusicView(gid))
    else:
        embed = discord.Embed(title="📋 Added to Queue", description=f"`{query}`", color=0x7289da)
        embed.add_field(name="Position", value=f"#{len(music_queues[gid])}")
        await interaction.followup.send(embed=embed, view=make_dismiss_view())

@tree.command(name="skip", description="⏭ Skip the current song")
async def cmd_skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭ Skipped!", view=make_dismiss_view())
    else:
        await interaction.response.send_message("Nothing is playing.", ephemeral=True)

@tree.command(name="stop", description="⏹ Stop music and disconnect bot from VC")
async def cmd_stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        music_queues[interaction.guild_id].clear()
        vc.stop()
        await vc.disconnect()
        await interaction.response.send_message("⏹ Stopped and disconnected.", view=make_dismiss_view())
    else:
        await interaction.response.send_message("Not in a voice channel.", ephemeral=True)

@tree.command(name="queue", description="📋 View the current music queue")
async def cmd_queue(interaction: discord.Interaction):
    q = music_queues[interaction.guild_id]
    if not q:
        await interaction.response.send_message("Queue is empty.", ephemeral=True)
        return
    items = "\n".join(f"`{i+1}.` {url[:70]}" for i, url in enumerate(q[:15]))
    embed = discord.Embed(title=f"📋 Music Queue ({len(q)} tracks)", description=items, color=0x1db954)
    await interaction.response.send_message(embed=embed, view=make_dismiss_view())

@tree.command(name="nowplaying", description="🎵 Show currently playing song info")
async def cmd_nowplaying(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        embed = discord.Embed(title="🎵 Now Playing", description="Audio is streaming in your VC!", color=0x1db954)
        embed.add_field(name="Queue", value=f"{len(music_queues[interaction.guild_id])} tracks remaining")
        await interaction.response.send_message(embed=embed, view=make_dismiss_view())
    else:
        await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)

# ─────────────────────────────────────────────
# SMOKING
# ─────────────────────────────────────────────
@tree.command(name="smoking", description="🚬 Smoking facts, quit tips, damage timeline")
@app_commands.describe(category="facts | quit | timeline | random")
async def cmd_smoking(interaction: discord.Interaction, category: str = "random"):
    cat = category.lower()
    embed = discord.Embed(timestamp=datetime.datetime.utcnow())
    view = make_dismiss_view()

    if cat == "facts":
        embed.title = "🚬 Smoking Facts"
        embed.color = 0xff6600
        embed.description = "\n".join(SMOKING_DATA["facts"])
    elif cat == "quit":
        embed.title = "💪 Quit Smoking Tips"
        embed.color = 0x00cc66
        embed.description = "\n".join(SMOKING_DATA["quit_tips"])
    elif cat == "timeline":
        embed.title = "⏳ Recovery Timeline After Quitting"
        embed.color = 0x00aaff
        for k, v in SMOKING_DATA["damage_timeline"].items():
            embed.add_field(name=f"⏰ {k}", value=v, inline=True)
    else:
        # Random from any category
        all_items = SMOKING_DATA["facts"] + SMOKING_DATA["quit_tips"]
        embed.title = "🚬 Smoking Info"
        embed.color = 0xff6600
        embed.description = random.choice(all_items)

    embed.set_footer(text="/smoking facts | quit | timeline | random")
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="quittrack", description="🏆 Start tracking your quit-smoking journey")
@app_commands.describe(cigs_per_day="How many cigarettes did you smoke per day?", price_per_pack="Price per pack (20 cigs) in USD")
async def cmd_quittrack(interaction: discord.Interaction, cigs_per_day: int = 10, price_per_pack: float = 7.0):
    uid = interaction.user.id
    quit_trackers[uid] = {"quit_time": now_ts(), "cpd": cigs_per_day, "ppp": price_per_pack}
    embed = discord.Embed(
        title="🏆 Quit Tracker Started!",
        description=f"Your quit journey begins **NOW** {interaction.user.mention}!\nTracking {cigs_per_day} cigs/day at ${price_per_pack:.2f}/pack.",
        color=0x00ff88,
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="💡 Tip", value=random.choice(SMOKING_DATA["quit_tips"]), inline=False)
    embed.set_footer(text="Use /quitstats to see your progress!")
    await interaction.response.send_message(embed=embed, view=make_dismiss_view())

@tree.command(name="quitstats", description="📊 Check your quit-smoking progress & money saved")
async def cmd_quitstats(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid not in quit_trackers:
        await interaction.response.send_message("❌ You haven't started tracking! Use `/quittrack` first.", ephemeral=True)
        return
    data = quit_trackers[uid]
    elapsed = now_ts() - data["quit_time"]
    days = elapsed / 86400
    hours = elapsed / 3600
    minutes = elapsed / 60
    cigs_not_smoked = int(days * data["cpd"])
    money_saved = (cigs_not_smoked / 20) * data["ppp"]
    life_gained_min = cigs_not_smoked * 11  # ~11 min per cigarette

    embed = discord.Embed(
        title=f"🏆 {interaction.user.display_name}'s Quit Journey",
        color=0x00ff88,
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="⏱️ Time Smoke-Free", value=f"{int(days)}d {int(hours%24)}h {int(minutes%60)}m", inline=True)
    embed.add_field(name="🚫 Cigs Avoided", value=f"{cigs_not_smoked:,}", inline=True)
    embed.add_field(name="💰 Money Saved", value=f"${money_saved:,.2f}", inline=True)
    embed.add_field(name="❤️ Life Regained", value=f"~{life_gained_min//60}h {life_gained_min%60}m", inline=True)

    # Milestone badges
    milestones = []
    if days >= 1: milestones.append("🥉 1 Day!")
    if days >= 7: milestones.append("🥈 1 Week!")
    if days >= 30: milestones.append("🥇 1 Month!")
    if days >= 90: milestones.append("💎 3 Months!")
    if days >= 365: milestones.append("🏆 1 Year!!!")
    if milestones:
        embed.add_field(name="🎖️ Milestones Earned", value=" ".join(milestones), inline=False)

    embed.set_footer(text="Keep going! Every minute counts.")
    await interaction.response.send_message(embed=embed, view=make_dismiss_view())

# ─────────────────────────────────────────────
# ADMIN — SETTINGS
# ─────────────────────────────────────────────
@tree.command(name="setcmdchannel", description="🔒 Admin: Restrict a command to specific channels")
@app_commands.describe(command_name="Command name (e.g. price, chart, play)", channel="Channel to allow the command in")
@app_commands.default_permissions(administrator=True)
async def cmd_setchannel(interaction: discord.Interaction, command_name: str, channel: discord.TextChannel):
    gid = str(interaction.guild_id)
    if command_name not in guild_settings[gid]["channel_restrictions"]:
        guild_settings[gid]["channel_restrictions"][command_name] = []
    guild_settings[gid]["channel_restrictions"][command_name].append(channel.id)
    embed = discord.Embed(
        title="✅ Channel Restriction Set",
        description=f"`/{command_name}` is now restricted to {channel.mention}",
        color=0x00ff88
    )
    await interaction.response.send_message(embed=embed, view=make_dismiss_view())

@tree.command(name="setcmdrole", description="🔒 Admin: Restrict a command to a specific role")
@app_commands.describe(command_name="Command name", role="Role allowed to use the command")
@app_commands.default_permissions(administrator=True)
async def cmd_setrole(interaction: discord.Interaction, command_name: str, role: discord.Role):
    gid = str(interaction.guild_id)
    if command_name not in guild_settings[gid]["role_restrictions"]:
        guild_settings[gid]["role_restrictions"][command_name] = []
    guild_settings[gid]["role_restrictions"][command_name].append(role.id)
    embed = discord.Embed(
        title="✅ Role Restriction Set",
        description=f"`/{command_name}` is now restricted to {role.mention}",
        color=0x00ff88
    )
    await interaction.response.send_message(embed=embed, view=make_dismiss_view())

@tree.command(name="clearcmdrestrictions", description="🔓 Admin: Clear all restrictions for a command")
@app_commands.describe(command_name="Command to unrestrict")
@app_commands.default_permissions(administrator=True)
async def cmd_clearrestrictions(interaction: discord.Interaction, command_name: str):
    gid = str(interaction.guild_id)
    guild_settings[gid]["channel_restrictions"].pop(command_name, None)
    guild_settings[gid]["role_restrictions"].pop(command_name, None)
    await interaction.response.send_message(f"✅ All restrictions cleared for `/{command_name}`.", view=make_dismiss_view())

@tree.command(name="settings", description="⚙️ Admin: View current command restrictions")
@app_commands.default_permissions(administrator=True)
async def cmd_settings(interaction: discord.Interaction):
    gid = str(interaction.guild_id)
    s = guild_settings[gid]
    embed = discord.Embed(title="⚙️ Server Settings", color=0x7289da)
    
    ch = s["channel_restrictions"]
    if ch:
        lines = []
        for cmd, cids in ch.items():
            channels = ", ".join(f"<#{c}>" for c in cids)
            lines.append(f"`/{cmd}` → {channels}")
        embed.add_field(name="📌 Channel Restrictions", value="\n".join(lines), inline=False)
    else:
        embed.add_field(name="📌 Channel Restrictions", value="None set", inline=False)

    ro = s["role_restrictions"]
    if ro:
        lines = []
        for cmd, rids in ro.items():
            roles = ", ".join(f"<@&{r}>" for r in rids)
            lines.append(f"`/{cmd}` → {roles}")
        embed.add_field(name="🎭 Role Restrictions", value="\n".join(lines), inline=False)
    else:
        embed.add_field(name="🎭 Role Restrictions", value="None set", inline=False)

    await interaction.response.send_message(embed=embed, view=make_dismiss_view(), ephemeral=True)

@tree.command(name="setinactivitychannel", description="🔒 Admin: Set the channel for inactivity alerts")
@app_commands.describe(channel="Channel for inactivity notifications")
@app_commands.default_permissions(administrator=True)
async def cmd_set_inactivity_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    global INACTIVITY_CHANNEL_ID
    INACTIVITY_CHANNEL_ID = channel.id
    await interaction.response.send_message(f"✅ Inactivity alerts will be sent to {channel.mention}", view=make_dismiss_view())

# ─────────────────────────────────────────────
# PURGE ALERT (Admin Manual)
# ─────────────────────────────────────────────
@tree.command(name="purgealert", description="⚠️ Admin: Manually send a purge alert for a user")
@app_commands.describe(user="User to flag for inactivity")
@app_commands.default_permissions(administrator=True)
async def cmd_purgealert(interaction: discord.Interaction, user: discord.Member):
    if not INACTIVITY_CHANNEL_ID:
        await interaction.response.send_message("❌ Set an inactivity channel first with `/setinactivitychannel`.", ephemeral=True)
        return
    ch = bot.get_channel(INACTIVITY_CHANNEL_ID)
    embed = discord.Embed(
        title="⚠️ Manual Purge Alert",
        description=f"Admin flagged **{user.mention}** for inactivity review.",
        color=0xff2222,
        timestamp=datetime.datetime.utcnow()
    )
    view = PurgeConfirmView(user.id)
    await ch.send(embed=embed, view=view)
    # DM admin confirmation
    if ADMIN_USER_ID:
        try:
            admin = await bot.fetch_user(ADMIN_USER_ID)
            await admin.send(f"🚨 Purge alert sent for {user} in #{ch.name}")
        except:
            pass
    await interaction.response.send_message(f"✅ Purge alert sent to {ch.mention}", ephemeral=True)

# ─────────────────────────────────────────────
# GENERAL UTILITY
# ─────────────────────────────────────────────
@tree.command(name="help", description="📖 Show all available bot commands")
async def cmd_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="All commands use `/` prefix. Some may be restricted by admin.",
        color=0x5865F2,
        timestamp=datetime.datetime.utcnow()
    )
    sections = {
        "💰 Crypto Prices": [
            "`/price <symbol>` — Real-time price (btc, eth, monad, megaeth...)",
            "`/chart <symbol> [days]` — Price chart (1/7/30/90/365d)",
            "`/top [count]` — Top N coins by market cap",
            "`/compare <coin1> <coin2>` — Side-by-side comparison",
            "`/trending` — Trending coins right now",
            "`/fomo <symbol> <usd> <days>` — What if you bought X days ago?",
        ],
        "🥇 Commodities": [
            "`/commodity <item>` — Gold, Silver, Oil, Platinum, Palladium, Copper, Wheat, Corn",
        ],
        "🎵 Music (VC)": [
            "`/play <song>` — Play in voice channel (YT URL or search)",
            "`/skip` — Skip current song",
            "`/stop` — Stop & disconnect",
            "`/queue` — View song queue",
            "`/nowplaying` — Current song info",
        ],
        "🚬 Smoking": [
            "`/smoking [facts|quit|timeline|random]` — Info & tips",
            "`/quittrack [cpd] [ppp]` — Start quit tracker",
            "`/quitstats` — View your quit progress",
        ],
        "⚙️ Admin": [
            "`/setcmdchannel <cmd> <#channel>` — Restrict cmd to channel",
            "`/setcmdrole <cmd> <@role>` — Restrict cmd to role",
            "`/clearcmdrestrictions <cmd>` — Remove restrictions",
            "`/settings` — View all restrictions",
            "`/setinactivitychannel <#channel>` — Set alert channel",
            "`/purgealert <@user>` — Manual purge alert",
        ],
    }
    for section, cmds in sections.items():
        embed.add_field(name=section, value="\n".join(cmds), inline=False)
    embed.set_footer(text="All responses have a ✖ Dismiss button • Inactivity auto-tracked")
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(), ephemeral=True)

@tree.command(name="ping", description="🏓 Check bot latency")
async def cmd_ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    color = 0x00ff88 if latency < 100 else 0xffaa00 if latency < 200 else 0xff4444
    embed = discord.Embed(title="🏓 Pong!", description=f"Latency: **{latency}ms**", color=color)
    await interaction.response.send_message(embed=embed, view=make_dismiss_view())

@tree.command(name="coins", description="📋 List all supported coin symbols")
async def cmd_coins(interaction: discord.Interaction):
    symbols = sorted(COIN_MAP.keys())
    chunks = [symbols[i:i+40] for i in range(0, len(symbols), 40)]
    embed = discord.Embed(title=f"📋 Supported Coins ({len(symbols)} total)", color=0xf7931a)
    for i, chunk in enumerate(chunks[:4]):
        embed.add_field(name=f"Symbols {i*40+1}–{min((i+1)*40, len(symbols))}", value=" • ".join(f"`{s}`" for s in chunk), inline=False)
    embed.set_footer(text="Use /price <symbol> or /chart <symbol>")
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(), ephemeral=True)

# ─────────────────────────────────────────────
# BOT EVENTS
# ─────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"\n{'='*50}")
    print(f"  Bot: {bot.user} ({bot.user.id})")
    print(f"  Guilds: {len(bot.guilds)}")
    print(f"  Latency: {round(bot.latency*1000)}ms")
    print(f"{'='*50}\n")
    
    try:
        synced = await tree.sync()
        print(f"✅ Synced {len(synced)} slash commands globally")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="📈 Crypto Markets | /help")
    )
    check_inactivity.start()
    print("✅ Inactivity check task started")

@bot.event
async def on_guild_join(guild):
    print(f"Joined guild: {guild.name} ({guild.id})")
    # Pre-populate activity for all members
    for m in guild.members:
        if not m.bot and m.id not in user_last_active:
            user_last_active[m.id] = now_ts()

@bot.event
async def on_member_join(member):
    if not member.bot:
        user_last_active[member.id] = now_ts()

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"Command error: {error}")
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ An error occurred: `{error}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Error: `{error}`", ephemeral=True)
    except:
        pass

# ─────────────────────────────────────────────
# KEEPALIVE (Railway / Render health check)
# ─────────────────────────────────────────────
async def keepalive():
    """Simple HTTP server so Railway/Render don't sleep the container."""
    from aiohttp import web
    app = web.Application()
    async def health(req): return web.Response(text="Bot is alive 🟢")
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Health server running on port {port}")

async def main():
    async with bot:
        await keepalive()
        await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Set BOT_TOKEN environment variable!")
        print("   Railway: Add BOT_TOKEN in Variables tab")
        print("   Local: export BOT_TOKEN=your_token_here")
        sys.exit(1)
    asyncio.run(main())
