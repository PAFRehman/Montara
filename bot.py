import os, sys, asyncio, time, random, io, datetime
from collections import defaultdict
import aiohttp
import discord
from discord.ext import commands, tasks
from discord import app_commands
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# ── CONFIG ──────────────────────────────────────────────────────────────────
BOT_TOKEN  = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID   = int(os.getenv("ADMIN_USER_ID", "0"))

# ── COIN MAP ─────────────────────────────────────────────────────────────────
COIN_MAP = {
    "btc":"bitcoin","eth":"ethereum","sol":"solana","bnb":"binancecoin",
    "xrp":"ripple","ada":"cardano","doge":"dogecoin","avax":"avalanche-2",
    "dot":"polkadot","matic":"matic-network","link":"chainlink","ltc":"litecoin",
    "uni":"uniswap","atom":"cosmos","xlm":"stellar","etc":"ethereum-classic",
    "near":"near","algo":"algorand","icp":"internet-computer","apt":"aptos",
    "arb":"arbitrum","op":"optimism","sui":"sui","sei":"sei-network",
    "tia":"celestia","inj":"injective-protocol","jup":"jupiter-ag",
    "wif":"dogwifcoin","bonk":"bonk","pepe":"pepe","floki":"floki",
    "shib":"shiba-inu","sand":"the-sandbox","mana":"decentraland",
    "axs":"axie-infinity","gala":"gala","imx":"immutable-x",
    "rune":"thorchain","fet":"fetch-ai","ocean":"ocean-protocol",
    "rndr":"render-token","grt":"the-graph","ldo":"lido-dao",
    "mkr":"maker","aave":"aave","crv":"curve-dao-token","snx":"havven",
    "comp":"compound-governance-token","bal":"balancer","sushi":"sushi",
    "cake":"pancakeswap-token","1inch":"1inch","zrx":"0x",
    "trx":"tron","hbar":"hedera-hashgraph","fil":"filecoin",
    "vet":"vechain","egld":"elrond-erd-2","theta":"theta-token",
    "ftm":"fantom","cro":"crypto-com-chain","flow":"flow",
    "mina":"mina-protocol","cfx":"conflux-token","kas":"kaspa",
    "blur":"blur","magic":"magic","lrc":"loopring","dydx":"dydx",
    "gmx":"gmx","wld":"worldcoin-wld","pyth":"pyth-network",
    "jto":"jito-governance-token","bome":"book-of-meme",
    "tnsr":"tensor","io":"io-net","zk":"zksync","strk":"starknet",
    "alt":"altlayer","eigen":"eigenlayer","pendle":"pendle",
    "ethfi":"ether-fi","monad":"monad","megaeth":"megaeth",
    "bera":"berachain-bera","sonic":"sonic-3","story":"story-2",
    "movement":"movement-2","initia":"initia","grass":"grass",
    "drift":"drift-protocol","kamino":"kamino","taiko":"taiko",
    "scroll":"scroll-token","manta":"manta-network","blast":"blast-2",
    "ordi":"ordinals","pnut":"peanut-the-squirrel","goat":"goat",
    "zerebro":"zerebro","ai16z":"ai16z","virtual":"virtual-protocol",
    "aixbt":"aixbt-by-virtuals","luna":"terra-luna-2","lunc":"terra-luna",
    "usdt":"tether","usdc":"usd-coin","dai":"dai","hyperliquid":"hyperliquid",
    "zeta":"zeta-chain","myro":"myro","act":"act-i-the-ai-prophecy",
}

# ── COMMODITY CONFIG ──────────────────────────────────────────────────────────
COMMODITIES = {
    "gold":      {"symbol":"XAU","name":"Gold",         "emoji":"🥇","unit":"oz","fallback":3320.0},
    "silver":    {"symbol":"XAG","name":"Silver",       "emoji":"🥈","unit":"oz","fallback":32.5},
    "platinum":  {"symbol":"XPT","name":"Platinum",     "emoji":"⚪","unit":"oz","fallback":980.0},
    "palladium": {"symbol":"XPD","name":"Palladium",    "emoji":"⚙️","unit":"oz","fallback":970.0},
    "oil":       {"symbol":"BRENTOIL","name":"Brent Crude Oil","emoji":"🛢️","unit":"bbl","fallback":85.0},
    "gas":       {"symbol":"NATGAS","name":"Natural Gas","emoji":"🔥","unit":"MMBtu","fallback":2.8},
    "copper":    {"symbol":"COPPER","name":"Copper",    "emoji":"🟤","unit":"lb","fallback":4.2},
    "wheat":     {"symbol":"WHEAT","name":"Wheat",      "emoji":"🌾","unit":"bu","fallback":560.0},
    "corn":      {"symbol":"CORN","name":"Corn",        "emoji":"🌽","unit":"bu","fallback":450.0},
}

# ── SMOKING DATA ──────────────────────────────────────────────────────────────
SMOKING = {
    "facts": [
        "🚬 Cigarettes: the only product that kills its best customers",
        "💨 7,000+ chemicals in smoke — but hey, at least it's organic",
        "🧠 Nicotine hits your brain in 10 seconds. Your morning coffee wishes it were that fast",
        "🌍 1.3 billion smokers worldwide — largest loyalty program on Earth",
        "💰 Average smoker spends $3,000+/year on cigarettes. That's a vacation, bro",
        "⏳ Each cig costs ~11 minutes of life. At least it's a relaxing 11 minutes",
        "🔬 Secondhand smoke: sharing is caring, apparently",
        "📉 Global smoking rates declining — quitters are the new cool kids",
        "🫁 Smoker's lungs are basically a charcoal filter that talks",
        "❤️ Your heart beats 36,000 times a day — smoke gives it overtime pay",
    ],
    "funny": [
        "🚬 Smoking: because sometimes you need a fire alarm that fits in your pocket",
        "😂 A cigarette is like a friend — it hangs around, costs money, and slowly kills you",
        "🌫️ Smoking doesn't kill you, it just makes you look cool while slowly regretting it",
        "💨 Smokers never get cold in winter — they've always got a light",
        "🏃 A smoker ran a marathon once. He needed 6 cigarette breaks but finished",
        "🤔 Cigarettes are like squirrels — harmless until you put one in your mouth",
        "😎 Smoking: turning oxygen into personality since 1492",
        "🎭 Every cigarette is a tiny drama in 5 minutes",
        "☕ Coffee + cigarette = breakfast of champions (historically speaking)",
        "🚬 Smoking cures salmon. Coincidence? Nobody thinks about that",
    ],
    "quit_tips": [
        "💡 Pick a quit date. Write it. Tell someone. Now it's real",
        "🍬 Nicotine patches, gum, lozenges — modern science is on your side",
        "🏃 Craving? Run around the block. You'll either forget the craving or pass out",
        "💧 Water trick: drink a full glass slowly when a craving hits — 3 mins and it's gone",
        "🧘 Deep breath: in 4s, hold 4s, out 4s. Free and it actually works",
        "💰 Save every cigarette dollar — watch the number grow, then book a flight",
        "🫂 Tell your crew you're quitting — social pressure works both ways",
        "📵 Delete your dealer's number. Same energy",
        "🎮 Replace the habit: gum, toothpick, fidget toy, literally anything",
        "🏆 1 week clean = buy yourself something nice. You earned it",
    ],
    "damage_timeline": {
        "20 min":  "Heart rate & blood pressure drop to normal",
        "12 hrs":  "Carbon monoxide levels in blood normalize",
        "2 weeks": "Circulation improves, lung function increases",
        "1 month": "Less coughing, less shortness of breath",
        "1 year":  "Heart disease risk is cut in HALF",
        "5 years": "Stroke risk equals a non-smoker",
        "10 years":"Lung cancer risk halved vs still smoking",
        "15 years":"Heart disease risk same as someone who never smoked",
    },
    "brands": {
        "Marlboro":    "The cowboy's cigarette. Rugged. Classic. The iPhone of smokes.",
        "Camel":       "Preferred by 9 out of 10 cartoon doctors in 1950s ads. Smooth.",
        "Newport":     "Menthol gang. Cool on the way in, still a cigarette on the way out.",
        "Lucky Strike":"Retro vibes. WWII era. Basically vintage at this point.",
        "Dunhill":     "The business-class cigarette. Expensive regrets, premium packaging.",
        "Parliament":  "Recessed filter = fancy. For smokers who take themselves seriously.",
        "Winston":     "No additives. The 'all natural' option for health-conscious smokers 😂",
        "Benson & Hedges":"British royalty used to smoke these. Go off, king.",
        "Pall Mall":   "Budget-friendly. The value investor of the cigarette world.",
        "Cohiba":      "Technically a cigar but feels wrong to leave it out. Cuban royalty.",
    },
    "rules": [
        "🚬 Rule #1: Always have a lighter. Always.",
        "🤝 Rule #2: Never refuse to give a light. Smoker code.",
        "🚭 Rule #3: Never bum 3 in a row without buying a pack",
        "🌬️ Rule #4: Blow smoke away from non-smokers. Basic courtesy",
        "☕ Rule #5: Coffee + cigarette is a sacred pairing. Respect it",
        "🌧️ Rule #6: Smoking in rain hits different. Cinematic",
        "🚗 Rule #7: Window down, arm out — the classic car smoke",
        "🌅 Rule #8: First smoke of the day after coffee is undefeated",
        "🍺 Rule #9: Any cigarette after a meal is automatically elite",
        "🏁 Rule #10: The last cigarette in the pack always tastes the best",
    ],
}

# ── STATE ─────────────────────────────────────────────────────────────────────
guild_settings  = defaultdict(lambda: {"channel_restrictions": {}, "role_restrictions": {}})
music_queues    = defaultdict(list)
now_playing     = {}   # guild_id -> title
quit_trackers   = {}   # user_id -> {quit_time, cpd, ppp}
smoke_sessions  = {}   # user_id -> {start_time, count}

# ── BOT SETUP ─────────────────────────────────────────────────────────────────
intents = discord.Intents.all()
bot  = commands.Bot(command_prefix="!", intents=intents, help_command=None)
tree = bot.tree

# ── HELPERS ───────────────────────────────────────────────────────────────────
def now_ts(): return time.time()

def fmt_price(p):
    if p is None: return "N/A"
    if p >= 1000:  return f"${p:,.2f}"
    if p >= 1:     return f"${p:.4f}"
    if p >= 0.001: return f"${p:.6f}"
    return f"${p:.8f}"

def fmt_change(c):
    if c is None: return "—"
    arrow = "▲" if c >= 0 else "▼"
    dot   = "🟢" if c >= 0 else "🔴"
    return f"{dot} {arrow}{abs(c):.2f}%"

def pct_color(c):
    if c is None: return 0x808080
    return 0x00ff88 if c >= 0 else 0xff4444

async def fetch_json(url, params=None):
    async with aiohttp.ClientSession() as s:
        async with s.get(url, params=params, timeout=aiohttp.ClientTimeout(total=12)) as r:
            return await r.json(content_type=None)

def check_allowed(interaction: discord.Interaction, cmd: str) -> bool:
    gid = str(interaction.guild_id)
    s   = guild_settings[gid]
    ch_list   = s["channel_restrictions"].get(cmd, [])
    role_list = s["role_restrictions"].get(cmd, [])
    if ch_list and interaction.channel_id not in ch_list:
        return False
    if role_list:
        user_roles = [r.id for r in interaction.user.roles]
        if not any(rid in user_roles for rid in role_list):
            return False
    return True

def make_dismiss_view(author_id: int):
    """Dismiss button — only the original author can use it."""
    view = discord.ui.View(timeout=600)
    btn  = discord.ui.Button(label="✖ Dismiss", style=discord.ButtonStyle.secondary)
    async def cb(i: discord.Interaction):
        if i.user.id != author_id:
            await i.response.send_message("Only the person who ran this command can dismiss it.", ephemeral=True)
            return
        await i.message.delete()
    btn.callback = cb
    view.add_item(btn)
    return view

# ── PRICE FETCH ───────────────────────────────────────────────────────────────
async def fetch_crypto(symbol: str):
    sym     = symbol.lower().strip()
    coin_id = COIN_MAP.get(sym, sym)
    try:
        data = await fetch_json("https://api.coingecko.com/api/v3/coins/markets", {
            "vs_currency": "usd", "ids": coin_id,
            "price_change_percentage": "1h,24h,7d",
        })
        if data:
            d = data[0]
            return {
                "name": d.get("name"), "symbol": d.get("symbol","").upper(),
                "price": d.get("current_price"),
                "change_1h":  d.get("price_change_percentage_1h_in_currency"),
                "change_24h": d.get("price_change_percentage_24h"),
                "change_7d":  d.get("price_change_percentage_7d_in_currency"),
                "market_cap": d.get("market_cap"), "volume": d.get("total_volume"),
                "high_24h": d.get("high_24h"), "low_24h": d.get("low_24h"),
                "rank": d.get("market_cap_rank"), "ath": d.get("ath"),
                "image": d.get("image"), "id": coin_id,
            }
    except Exception as e:
        print(f"Crypto fetch error: {e}")
    return None

async def fetch_commodity_price(key: str):
    """Try metals-api, fallback to stooq, fallback to static."""
    info = COMMODITIES[key]
    sym  = info["symbol"]

    # Attempt 1: metals.live
    try:
        data = await fetch_json(f"https://api.metals.live/v1/spot/{sym.lower()}")
        if isinstance(data, list) and data:
            val = list(data[0].values())[0]
            if val: return float(val), False
    except: pass

    # Attempt 2: frankfurter for XAU/XAG (EUR base, convert)
    if sym in ("XAU","XAG","XPT","XPD"):
        try:
            data = await fetch_json(f"https://api.frankfurter.app/latest?from=USD&to={sym}")
            rate = data.get("rates",{}).get(sym)
            if rate: return round(1/rate, 2), False
        except: pass

    # Attempt 3: stooq CSV for commodities
    stooq_map = {"BRENTOIL":"@CL.F","NATGAS":"@NG.F","COPPER":"HG.F","WHEAT":"@W.F","CORN":"@C.F"}
    stooq_sym = stooq_map.get(sym)
    if stooq_sym:
        try:
            url  = f"https://stooq.com/q/l/?s={stooq_sym}&f=sd2t2ohlcv&h&e=csv"
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                    text = await r.text()
            lines = text.strip().split("\n")
            if len(lines) >= 2:
                cols  = lines[1].split(",")
                price = float(cols[4])   # close price
                if price > 0: return price, False
        except: pass

    # Fallback static
    return info["fallback"], True

# ── CHART GENERATORS ──────────────────────────────────────────────────────────
async def crypto_chart_buf(coin_id: str, days: int) -> io.BytesIO | None:
    try:
        interval = "daily" if days > 2 else "hourly"
        data = await fetch_json(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
            {"vs_currency":"usd","days":days,"interval":interval}
        )
        prices = data.get("prices",[])
        if not prices: return None

        ts  = [datetime.datetime.fromtimestamp(p[0]/1000) for p in prices]
        vs  = [p[1] for p in prices]
        chg = ((vs[-1]-vs[0])/vs[0])*100
        col = "#00ff88" if chg >= 0 else "#ff4455"

        fig, ax = plt.subplots(figsize=(11,4.5), facecolor="#0d1117")
        ax.set_facecolor("#0d1117")
        ax.plot(ts, vs, color=col, linewidth=2.2, zorder=5)
        ax.fill_between(ts, vs, min(vs)*0.995, alpha=0.25, color=col)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d" if days>2 else "%H:%M"))
        ax.tick_params(colors="#888", labelsize=8)
        for spine in ax.spines.values(): spine.set_color("#222")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: fmt_price(x)))
        ax.set_title(f"{coin_id.upper()} — {days}d", color="white", fontsize=13, pad=8)
        ax.grid(True, color="#1e2430", linewidth=0.6, linestyle="--")
        badge_col = "#00ff88" if chg>=0 else "#ff4455"
        ax.annotate(f"{'▲' if chg>=0 else '▼'} {abs(chg):.2f}%",
                    xy=(0.01,0.93), xycoords="axes fraction",
                    color=badge_col, fontsize=11, fontweight="bold")
        plt.tight_layout(pad=0.5)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor="#0d1117")
        plt.close(fig)
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Crypto chart error: {e}")
        return None

async def commodity_chart_buf(key: str) -> io.BytesIO | None:
    """Generate a simulated 30-day commodity chart using daily price + noise."""
    try:
        price, is_fallback = await fetch_commodity_price(key)
        info  = COMMODITIES[key]

        # Build synthetic 30-day series around current price
        np.random.seed(int(price) % 9999)
        days  = 30
        noise = np.cumsum(np.random.randn(days) * price * 0.008)
        series= np.clip(price + noise - noise[-1], price*0.85, price*1.15)
        series[-1] = price

        dates = [datetime.datetime.utcnow() - datetime.timedelta(days=days-i) for i in range(days)]
        chg   = ((series[-1]-series[0])/series[0])*100
        col   = "#00ff88" if chg>=0 else "#ff4455"

        fig, ax = plt.subplots(figsize=(11,4.5), facecolor="#0d1117")
        ax.set_facecolor("#0d1117")
        ax.plot(dates, series, color=col, linewidth=2.2, zorder=5)
        ax.fill_between(dates, series, min(series)*0.995, alpha=0.25, color=col)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.tick_params(colors="#888", labelsize=8)
        for spine in ax.spines.values(): spine.set_color("#222")
        unit = info['unit']
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:,.2f}"))
        title = f"{info['emoji']} {info['name']} — 30d  |  ${price:,.2f}/{unit}"
        if is_fallback: title += "  ⚠ est."
        ax.set_title(title, color="white", fontsize=12, pad=8)
        ax.grid(True, color="#1e2430", linewidth=0.6, linestyle="--")
        badge_col = "#00ff88" if chg>=0 else "#ff4455"
        ax.annotate(f"{'▲' if chg>=0 else '▼'} {abs(chg):.2f}% (30d)",
                    xy=(0.01,0.93), xycoords="axes fraction",
                    color=badge_col, fontsize=10, fontweight="bold")
        plt.tight_layout(pad=0.5)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor="#0d1117")
        plt.close(fig)
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Commodity chart error: {e}")
        return None

# ── MUSIC ─────────────────────────────────────────────────────────────────────
FFMPEG_OPTS = {
    "before_options": (
        "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
        "-probesize 200M -analyzeduration 200M"
    ),
    "options": "-vn -ar 48000 -ac 2 -b:a 192k"
}

async def resolve_audio(query: str):
    import yt_dlp
    opts = {
        "format": "bestaudio[ext=webm]/bestaudio/best",
        "quiet": True, "no_warnings": True,
        "default_search": "ytsearch",
        "source_address": "0.0.0.0",
        "noplaylist": True,
        "postprocessors": [],
    }
    loop = asyncio.get_event_loop()
    def _extract():
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info: info = info["entries"][0]
            return info.get("url"), info.get("title", query), info.get("thumbnail"), info.get("duration",0)
    return await loop.run_in_executor(None, _extract)

async def play_next(guild: discord.Guild, channel: discord.TextChannel = None):
    gid = guild.id
    q   = music_queues[gid]
    if not q:
        now_playing.pop(gid, None)
        return
    url_or_query = q.pop(0)
    vc = guild.voice_client
    if not vc or not vc.is_connected():
        return
    try:
        audio_url, title, thumb, dur = await resolve_audio(url_or_query)
        now_playing[gid] = {"title": title, "thumb": thumb, "dur": dur, "query": url_or_query}
        source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTS)
        source = discord.PCMVolumeTransformer(source, volume=1.0)

        def after(err):
            if err: print(f"Player err: {err}")
            asyncio.run_coroutine_threadsafe(play_next(guild, channel), bot.loop)

        vc.play(source, after=after)

        if channel:
            mins, secs = divmod(dur or 0, 60)
            embed = discord.Embed(title="🎵 Now Playing", description=f"**{title}**", color=0x1db954)
            if thumb: embed.set_thumbnail(url=thumb)
            embed.add_field(name="Duration", value=f"{mins}:{secs:02d}" if dur else "Live", inline=True)
            embed.add_field(name="Queue",    value=f"{len(q)} tracks left", inline=True)
            await channel.send(embed=embed)
    except Exception as e:
        print(f"Music resolve error: {e}")
        if channel: await channel.send(f"❌ Could not play `{url_or_query}`: {e}")
        await play_next(guild, channel)

# ═══════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS — CRYPTO
# ═══════════════════════════════════════════════════════════════════════════════

@tree.command(name="price", description="Get real-time crypto price")
@app_commands.describe(symbol="Coin symbol — btc, eth, sol, monad, megaeth ...")
async def cmd_price(interaction: discord.Interaction, symbol: str):
    if not check_allowed(interaction, "price"):
        await interaction.response.send_message("❌ Not allowed here.", ephemeral=True); return
    await interaction.response.defer()
    d = await fetch_crypto(symbol)
    if not d:
        await interaction.followup.send(f"❌ `{symbol}` not found.", ephemeral=True); return
    embed = discord.Embed(title=f"{d['name']}  ({d['symbol']})",
                          description=f"# {fmt_price(d['price'])}",
                          color=pct_color(d['change_24h']),
                          timestamp=datetime.datetime.utcnow())
    if d.get("image"): embed.set_thumbnail(url=d["image"])
    embed.add_field(name="1h",  value=fmt_change(d['change_1h']),  inline=True)
    embed.add_field(name="24h", value=fmt_change(d['change_24h']), inline=True)
    embed.add_field(name="7d",  value=fmt_change(d['change_7d']),  inline=True)
    if d['market_cap']: embed.add_field(name="Market Cap", value=f"${d['market_cap']:,.0f}", inline=True)
    if d['volume']:     embed.add_field(name="24h Volume", value=f"${d['volume']:,.0f}",    inline=True)
    if d['rank']:       embed.add_field(name="Rank",       value=f"#{d['rank']}",            inline=True)
    if d['high_24h'] and d['low_24h']:
        embed.add_field(name="24h High / Low",
                        value=f"{fmt_price(d['high_24h'])} / {fmt_price(d['low_24h'])}", inline=False)
    if d['ath']: embed.add_field(name="All-Time High", value=fmt_price(d['ath']), inline=True)
    embed.set_footer(text="CoinGecko")
    await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="chart", description="Real-time price chart for any crypto")
@app_commands.describe(symbol="Coin symbol", days="1 / 7 / 30 / 90 / 365")
async def cmd_chart(interaction: discord.Interaction, symbol: str, days: int = 7):
    if not check_allowed(interaction, "chart"):
        await interaction.response.send_message("❌ Not allowed here.", ephemeral=True); return
    await interaction.response.defer()
    sym = symbol.lower()
    cid = COIN_MAP.get(sym, sym)
    buf = await crypto_chart_buf(cid, min(max(days,1),365))
    if not buf:
        await interaction.followup.send(f"❌ No chart data for `{symbol}`.", ephemeral=True); return
    f = discord.File(buf, filename=f"{sym}_chart.png")
    e = discord.Embed(title=f"📈 {symbol.upper()} — {days}d", color=0x00ff88)
    e.set_image(url=f"attachment://{sym}_chart.png")
    e.set_footer(text="CoinGecko")
    await interaction.followup.send(embed=e, file=f, view=make_dismiss_view(interaction.user.id))

@tree.command(name="top", description="Top N cryptos by market cap")
@app_commands.describe(count="How many to show (max 20)")
async def cmd_top(interaction: discord.Interaction, count: int = 10):
    if not check_allowed(interaction, "top"):
        await interaction.response.send_message("❌ Not allowed here.", ephemeral=True); return
    await interaction.response.defer()
    count = min(max(count,1),20)
    data = await fetch_json("https://api.coingecko.com/api/v3/coins/markets",{
        "vs_currency":"usd","order":"market_cap_desc","per_page":count,"page":1,
        "price_change_percentage":"24h",
    })
    embed = discord.Embed(title=f"🏆 Top {count} Cryptos", color=0xf7931a,
                          timestamp=datetime.datetime.utcnow())
    rows = []
    for i,c in enumerate(data,1):
        chg  = c.get("price_change_percentage_24h") or 0
        dot  = "🟢" if chg>=0 else "🔴"
        rows.append(f"**#{i}** {c['name']} `{c['symbol'].upper()}` — {fmt_price(c['current_price'])}  {dot}{'▲' if chg>=0 else '▼'}{abs(chg):.2f}%")
    embed.description = "\n".join(rows)
    embed.set_footer(text="CoinGecko")
    await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="compare", description="Compare two cryptos side by side")
@app_commands.describe(coin1="First coin", coin2="Second coin")
async def cmd_compare(interaction: discord.Interaction, coin1: str, coin2: str):
    await interaction.response.defer()
    d1,d2 = await asyncio.gather(fetch_crypto(coin1), fetch_crypto(coin2))
    if not d1 or not d2:
        await interaction.followup.send("❌ Could not find one or both coins.", ephemeral=True); return
    embed = discord.Embed(title=f"⚖️ {d1['name']} vs {d2['name']}", color=0x7289da,
                          timestamp=datetime.datetime.utcnow())
    for label,v1,v2 in [
        ("Price",    fmt_price(d1['price']),   fmt_price(d2['price'])),
        ("24h",      fmt_change(d1['change_24h']), fmt_change(d2['change_24h'])),
        ("7d",       fmt_change(d1['change_7d']),  fmt_change(d2['change_7d'])),
        ("Mkt Cap",  f"${d1['market_cap']:,.0f}" if d1['market_cap'] else "N/A",
                     f"${d2['market_cap']:,.0f}" if d2['market_cap'] else "N/A"),
        ("Rank",     f"#{d1['rank']}" if d1['rank'] else "N/A",
                     f"#{d2['rank']}" if d2['rank'] else "N/A"),
    ]:
        embed.add_field(name=label, value=f"**{d1['symbol']}:** {v1}\n**{d2['symbol']}:** {v2}", inline=True)
    await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="trending", description="Trending coins on CoinGecko right now")
async def cmd_trending(interaction: discord.Interaction):
    await interaction.response.defer()
    data  = await fetch_json("https://api.coingecko.com/api/v3/search/trending")
    coins = data.get("coins",[])[:10]
    embed = discord.Embed(title="🔥 Trending Now", color=0xff6600,
                          timestamp=datetime.datetime.utcnow())
    rows  = [f"**#{i}** {c['item']['name']} `{c['item']['symbol']}` — Rank #{c['item'].get('market_cap_rank','?')}"
             for i,c in enumerate(coins,1)]
    embed.description = "\n".join(rows)
    embed.set_footer(text="CoinGecko trending")
    await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="fomo", description="What if you bought X dollars of a coin N days ago?")
@app_commands.describe(symbol="Coin", amount_usd="USD invested", days_ago="Days ago")
async def cmd_fomo(interaction: discord.Interaction, symbol: str, amount_usd: float, days_ago: int):
    await interaction.response.defer()
    cid   = COIN_MAP.get(symbol.lower(), symbol.lower())
    dstr  = (datetime.datetime.utcnow()-datetime.timedelta(days=days_ago)).strftime("%d-%m-%Y")
    hist  = await fetch_json(f"https://api.coingecko.com/api/v3/coins/{cid}/history",{"date":dstr})
    past  = hist.get("market_data",{}).get("current_price",{}).get("usd")
    cur   = await fetch_crypto(symbol)
    if not past or not cur:
        await interaction.followup.send("❌ Could not fetch historical data.", ephemeral=True); return
    bought = amount_usd / past
    now_v  = bought * cur['price']
    profit = now_v - amount_usd
    pct    = (profit / amount_usd)*100
    embed  = discord.Embed(title=f"😱 FOMO — {cur['name']}",
                           color=0x00ff88 if profit>=0 else 0xff4444,
                           timestamp=datetime.datetime.utcnow())
    embed.add_field(name="Invested",    value=f"${amount_usd:,.2f}",   inline=True)
    embed.add_field(name="Days Ago",    value=str(days_ago),            inline=True)
    embed.add_field(name="Price Then",  value=fmt_price(past),          inline=True)
    embed.add_field(name="Price Now",   value=fmt_price(cur['price']),  inline=True)
    embed.add_field(name="Coins Bought",value=f"{bought:.6f}",          inline=True)
    embed.add_field(name="Value Now",   value=f"${now_v:,.2f}",         inline=True)
    sign = "🟢 +" if profit>=0 else "🔴 -"
    embed.add_field(name="P&L", value=f"{sign}${abs(profit):,.2f}  ({'▲' if pct>=0 else '▼'}{abs(pct):.2f}%)", inline=False)
    await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="coins", description="List all supported coin symbols")
async def cmd_coins(interaction: discord.Interaction):
    syms   = sorted(COIN_MAP.keys())
    chunks = [syms[i:i+40] for i in range(0,len(syms),40)]
    embed  = discord.Embed(title=f"Supported Coins ({len(syms)})", color=0xf7931a)
    for i,ch in enumerate(chunks[:4]):
        embed.add_field(name=f"{i*40+1}–{min((i+1)*40,len(syms))}",
                        value=" • ".join(f"`{s}`" for s in ch), inline=False)
    embed.set_footer(text="/price <symbol> or /chart <symbol>")
    await interaction.response.send_message(embed=embed,
                                            view=make_dismiss_view(interaction.user.id),
                                            ephemeral=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS — COMMODITIES
# ═══════════════════════════════════════════════════════════════════════════════

@tree.command(name="commodity", description="Real-time price + chart for gold, silver, oil, and more")
@app_commands.describe(item="gold · silver · platinum · palladium · oil · gas · copper · wheat · corn")
async def cmd_commodity(interaction: discord.Interaction, item: str):
    if not check_allowed(interaction, "commodity"):
        await interaction.response.send_message("❌ Not allowed here.", ephemeral=True); return
    key = item.lower().strip()
    if key not in COMMODITIES:
        keys = " • ".join(COMMODITIES.keys())
        await interaction.response.send_message(f"❌ Unknown commodity. Options: {keys}", ephemeral=True); return
    await interaction.response.defer()
    info  = COMMODITIES[key]
    price, is_fallback = await fetch_commodity_price(key)
    buf   = await commodity_chart_buf(key)

    embed = discord.Embed(
        title=f"{info['emoji']} {info['name']}",
        description=f"# ${price:,.2f} / {info['unit']}",
        color=0xFFD700 if key=="gold" else 0xC0C0C0 if key=="silver" else 0x4a90d9,
        timestamp=datetime.datetime.utcnow()
    )
    if is_fallback:
        embed.set_footer(text="⚠️ Live API unavailable — showing estimate. Chart is illustrative.")
    else:
        embed.set_footer(text="Live price · Chart: 30-day estimated trend")

    if buf:
        f = discord.File(buf, filename=f"{key}_chart.png")
        embed.set_image(url=f"attachment://{key}_chart.png")
        await interaction.followup.send(embed=embed, file=f, view=make_dismiss_view(interaction.user.id))
    else:
        await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

# ═══════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS — MUSIC
# ═══════════════════════════════════════════════════════════════════════════════

@tree.command(name="play", description="Play a song in your voice channel")
@app_commands.describe(query="Song name or YouTube URL")
async def cmd_play(interaction: discord.Interaction, query: str):
    if not check_allowed(interaction, "play"):
        await interaction.response.send_message("❌ Not allowed here.", ephemeral=True); return
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Join a voice channel first.", ephemeral=True); return
    await interaction.response.defer()
    vc = interaction.guild.voice_client
    if not vc:
        vc = await interaction.user.voice.channel.connect()
    elif vc.channel != interaction.user.voice.channel:
        await vc.move_to(interaction.user.voice.channel)

    gid = interaction.guild_id
    music_queues[gid].append(query)

    if not vc.is_playing() and not vc.is_paused():
        await play_next(interaction.guild, interaction.channel)
        embed = discord.Embed(title="🎵 Loading...", description=f"`{query}`", color=0x1db954)
        await interaction.followup.send(embed=embed, view=_music_view(gid, interaction.user.id))
    else:
        pos = len(music_queues[gid])
        embed = discord.Embed(title="📋 Added to Queue", description=f"`{query}`", color=0x7289da)
        embed.add_field(name="Position", value=f"#{pos}")
        await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

def _music_view(guild_id: int, author_id: int):
    view = discord.ui.View(timeout=None)
    async def skip_cb(i: discord.Interaction):
        vc = i.guild.voice_client
        if vc and vc.is_playing(): vc.stop(); await i.response.send_message("⏭ Skipped", ephemeral=True)
        else: await i.response.send_message("Nothing playing.", ephemeral=True)
    async def stop_cb(i: discord.Interaction):
        vc = i.guild.voice_client
        if vc:
            music_queues[guild_id].clear(); vc.stop(); await vc.disconnect()
            await i.response.send_message("⏹ Stopped", ephemeral=True)
        else: await i.response.send_message("Not connected.", ephemeral=True)
    async def queue_cb(i: discord.Interaction):
        q = music_queues[guild_id]
        if not q: await i.response.send_message("Queue empty.", ephemeral=True); return
        items = "\n".join(f"`{n+1}.` {u[:60]}" for n,u in enumerate(q[:10]))
        await i.response.send_message(f"**Queue ({len(q)}):**\n{items}", ephemeral=True)
    async def dismiss_cb(i: discord.Interaction):
        if i.user.id != author_id:
            await i.response.send_message("Only the requester can dismiss this.", ephemeral=True); return
        await i.message.delete()

    skip_btn = discord.ui.Button(label="⏭ Skip",  style=discord.ButtonStyle.primary)
    stop_btn = discord.ui.Button(label="⏹ Stop",  style=discord.ButtonStyle.danger)
    q_btn    = discord.ui.Button(label="📋 Queue", style=discord.ButtonStyle.secondary)
    dis_btn  = discord.ui.Button(label="✖ Dismiss",style=discord.ButtonStyle.secondary)
    skip_btn.callback = skip_cb; stop_btn.callback = stop_cb
    q_btn.callback    = queue_cb; dis_btn.callback = dismiss_cb
    for b in [skip_btn, stop_btn, q_btn, dis_btn]: view.add_item(b)
    return view

@tree.command(name="skip", description="Skip the current song")
async def cmd_skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop(); await interaction.response.send_message("⏭ Skipped.", view=make_dismiss_view(interaction.user.id))
    else:
        await interaction.response.send_message("Nothing playing.", ephemeral=True)

@tree.command(name="stop", description="Stop music and disconnect")
async def cmd_stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        music_queues[interaction.guild_id].clear(); vc.stop(); await vc.disconnect()
        await interaction.response.send_message("⏹ Stopped.", view=make_dismiss_view(interaction.user.id))
    else:
        await interaction.response.send_message("Not connected.", ephemeral=True)

@tree.command(name="queue", description="View the music queue")
async def cmd_queue(interaction: discord.Interaction):
    q = music_queues[interaction.guild_id]
    if not q:
        await interaction.response.send_message("Queue is empty.", ephemeral=True); return
    items = "\n".join(f"`{i+1}.` {u[:70]}" for i,u in enumerate(q[:15]))
    embed = discord.Embed(title=f"📋 Queue ({len(q)} tracks)", description=items, color=0x1db954)
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="nowplaying", description="Show what's currently playing")
async def cmd_nowplaying(interaction: discord.Interaction):
    vc  = interaction.guild.voice_client
    np  = now_playing.get(interaction.guild_id)
    if vc and vc.is_playing() and np:
        embed = discord.Embed(title="🎵 Now Playing", description=f"**{np['title']}**", color=0x1db954)
        if np.get("thumb"): embed.set_thumbnail(url=np["thumb"])
        mins,secs = divmod(np.get("dur",0),60)
        embed.add_field(name="Duration", value=f"{mins}:{secs:02d}" if np.get("dur") else "Live")
        embed.add_field(name="Queue",    value=f"{len(music_queues[interaction.guild_id])} left")
        await interaction.response.send_message(embed=embed, view=make_dismiss_view(interaction.user.id))
    else:
        await interaction.response.send_message("Nothing playing right now.", ephemeral=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS — SMOKING
# ═══════════════════════════════════════════════════════════════════════════════

@tree.command(name="smoke", description="Smoking facts, funny takes, quit tips, rules & more")
@app_commands.describe(category="facts · funny · quit · timeline · rules · brand · random")
async def cmd_smoke(interaction: discord.Interaction, category: str = "random"):
    cat   = category.lower().strip()
    embed = discord.Embed(timestamp=datetime.datetime.utcnow())

    if cat == "facts":
        embed.title = "🚬 Smoking Facts"
        embed.color = 0xff6600
        embed.description = "\n".join(SMOKING["facts"])

    elif cat == "funny":
        embed.title = "😂 Cigarette Humour"
        embed.color = 0xffcc00
        embed.description = "\n".join(SMOKING["funny"])

    elif cat == "quit":
        embed.title = "💪 Quit Tips"
        embed.color = 0x00cc66
        embed.description = "\n".join(SMOKING["quit_tips"])

    elif cat == "timeline":
        embed.title = "⏳ Recovery Timeline After Quitting"
        embed.color = 0x00aaff
        for k,v in SMOKING["damage_timeline"].items():
            embed.add_field(name=f"⏰ {k}", value=v, inline=True)

    elif cat == "rules":
        embed.title = "📜 Unwritten Rules of Smoking"
        embed.color = 0xaa6644
        embed.description = "\n".join(SMOKING["rules"])

    elif cat == "brand":
        embed.title = "🏷️ Cigarette Brand Reviews"
        embed.color = 0x8b4513
        for brand,desc in SMOKING["brands"].items():
            embed.add_field(name=brand, value=desc, inline=False)

    else:  # random
        all_lines = SMOKING["facts"] + SMOKING["funny"] + SMOKING["quit_tips"] + SMOKING["rules"]
        embed.title = "🚬 Random Smoke Thought"
        embed.color = random.choice([0xff6600,0xffcc00,0x00cc66,0xaa6644])
        embed.description = random.choice(all_lines)

    embed.set_footer(text="/smoke  facts · funny · quit · timeline · rules · brand · random")
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="quittrack", description="Start tracking your quit-smoking journey")
@app_commands.describe(cigs_per_day="Cigarettes you smoked per day", price_per_pack="Pack price in USD (20 cigs)")
async def cmd_quittrack(interaction: discord.Interaction, cigs_per_day: int = 10, price_per_pack: float = 7.0):
    uid = interaction.user.id
    quit_trackers[uid] = {"quit_time": now_ts(), "cpd": cigs_per_day, "ppp": price_per_pack}
    embed = discord.Embed(
        title="🏆 Quit Tracker Started",
        description=f"{interaction.user.mention} — your clock starts **now**.\nTracking {cigs_per_day} cigs/day at ${price_per_pack:.2f}/pack.",
        color=0x00ff88, timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="💡 Tip", value=random.choice(SMOKING["quit_tips"]), inline=False)
    embed.set_footer(text="Use /quitstats to see your progress anytime")
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(uid))

@tree.command(name="quitstats", description="Check your quit-smoking progress & savings")
async def cmd_quitstats(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid not in quit_trackers:
        await interaction.response.send_message("❌ Start with `/quittrack` first.", ephemeral=True); return
    d       = quit_trackers[uid]
    elapsed = now_ts() - d["quit_time"]
    days    = elapsed/86400; hrs = elapsed/3600; mins = elapsed/60
    avoided = int(days * d["cpd"])
    saved   = (avoided/20)*d["ppp"]
    life_m  = avoided * 11

    embed = discord.Embed(title=f"🏆 {interaction.user.display_name}'s Quit Stats",
                          color=0x00ff88, timestamp=datetime.datetime.utcnow())
    embed.add_field(name="⏱️ Smoke-Free",    value=f"{int(days)}d {int(hrs%24)}h {int(mins%60)}m", inline=True)
    embed.add_field(name="🚫 Cigs Dodged",   value=f"{avoided:,}",                                 inline=True)
    embed.add_field(name="💰 Money Saved",   value=f"${saved:,.2f}",                               inline=True)
    embed.add_field(name="❤️ Life Regained", value=f"~{life_m//60}h {life_m%60}m",                 inline=True)
    milestones = []
    if days>=1:   milestones.append("🥉 1 Day")
    if days>=7:   milestones.append("🥈 1 Week")
    if days>=30:  milestones.append("🥇 1 Month")
    if days>=90:  milestones.append("💎 3 Months")
    if days>=365: milestones.append("🏆 1 YEAR!")
    if milestones: embed.add_field(name="🎖️ Badges", value="  ".join(milestones), inline=False)
    embed.set_footer(text="Keep going — every minute counts")
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(uid))

@tree.command(name="smokebreak", description="Log a smoke break — track how many you're having today")
async def cmd_smokebreak(interaction: discord.Interaction):
    uid  = interaction.user.id
    today = datetime.date.today().isoformat()
    sess = smoke_sessions.setdefault(uid, {"date": today, "count": 0})
    if sess["date"] != today:
        sess["date"] = today; sess["count"] = 0
    sess["count"] += 1
    count = sess["count"]
    comments = [
        "One down. At least you're honest with yourself.",
        "Two. The slippery slope begins.",
        "Three. Classic triple threat.",
        "Four. Your lungs filed a formal complaint.",
        "Five. Halfway to a pack. Impressive commitment.",
        "Six+. At this point you're basically a chimney. Own it.",
    ]
    comment = comments[min(count-1, len(comments)-1)]
    embed = discord.Embed(
        title=f"🚬 Smoke Break #{count} Today",
        description=comment,
        color=0xffaa33,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="Use /dailysmokes to see your full day")
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(uid))

@tree.command(name="dailysmokes", description="See how many smoke breaks you've logged today")
async def cmd_dailysmokes(interaction: discord.Interaction):
    uid   = interaction.user.id
    today = datetime.date.today().isoformat()
    sess  = smoke_sessions.get(uid)
    if not sess or sess["date"] != today:
        await interaction.response.send_message("No smokes logged today. Use `/smokebreak` to log one.", ephemeral=True); return
    count = sess["count"]
    embed = discord.Embed(
        title=f"📊 {interaction.user.display_name}'s Smoke Log",
        description=f"You've had **{count}** cigarette{'s' if count!=1 else ''} today.",
        color=0xff6600,
        timestamp=datetime.datetime.utcnow()
    )
    cigs_cost = (count/20) * 7.0
    embed.add_field(name="💰 Cost Today",   value=f"~${cigs_cost:.2f}", inline=True)
    embed.add_field(name="⏳ Life Spent",   value=f"~{count*11} minutes", inline=True)
    if count <= 5:   embed.add_field(name="Verdict", value="Respectable restraint 👏", inline=False)
    elif count <= 10: embed.add_field(name="Verdict", value="Committed smoker 🚬", inline=False)
    else:             embed.add_field(name="Verdict", value="You ARE the cigarette now 🌫️", inline=False)
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(uid))

@tree.command(name="cravingkiller", description="Hit this when you're craving a cigarette — distraction tactics")
async def cmd_cravingkiller(interaction: discord.Interaction):
    tactics = [
        "🏃 Drop and do 15 push-ups. Craving will be gone by rep 8.",
        "💧 Drink a full glass of cold water slowly. Works in 3 minutes.",
        "🧘 Box breathing: inhale 4s → hold 4s → exhale 4s. Repeat 4x.",
        "🍬 Chew gum aggressively. Jaw busy = brain distracted.",
        "📱 Text someone random 'hey'. By the time they reply, craving's dead.",
        "🎮 Open a game. 5 minutes of anything beats a 5-minute cig.",
        "🚿 Splash cold water on your face. Chemical reset. Costs nothing.",
        "👃 Sniff something strong — coffee beans, peppermint oil, literally anything.",
        "✏️ Write down why you want to quit. Read it out loud. Cringe. Repeat.",
        "🌅 Go outside but DON'T smoke. Just stand there and breathe. Power move.",
    ]
    embed = discord.Embed(
        title="💪 Craving Killer",
        description=f"**Try this right now:**\n\n{random.choice(tactics)}\n\n*Cravings peak at ~3 minutes and then fade. You just need to outlast it.*",
        color=0x00cc66,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="/cravingkiller — run it every time you want to light up")
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(interaction.user.id))

# ═══════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS — ADMIN
# ═══════════════════════════════════════════════════════════════════════════════

@tree.command(name="setcmdchannel", description="Restrict a command to a specific channel")
@app_commands.describe(command_name="Command name (price, chart, play ...)", channel="Channel to allow it in")
@app_commands.default_permissions(administrator=True)
async def cmd_setchannel(interaction: discord.Interaction, command_name: str, channel: discord.TextChannel):
    gid = str(interaction.guild_id)
    guild_settings[gid]["channel_restrictions"].setdefault(command_name, []).append(channel.id)
    embed = discord.Embed(title="✅ Channel Restriction Set",
                          description=f"`/{command_name}` → {channel.mention}", color=0x00ff88)
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="setcmdrole", description="Restrict a command to a specific role")
@app_commands.describe(command_name="Command name", role="Role that can use it")
@app_commands.default_permissions(administrator=True)
async def cmd_setrole(interaction: discord.Interaction, command_name: str, role: discord.Role):
    gid = str(interaction.guild_id)
    guild_settings[gid]["role_restrictions"].setdefault(command_name, []).append(role.id)
    embed = discord.Embed(title="✅ Role Restriction Set",
                          description=f"`/{command_name}` → {role.mention}", color=0x00ff88)
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="clearcmdrestrictions", description="Remove all restrictions for a command")
@app_commands.describe(command_name="Command to unrestrict")
@app_commands.default_permissions(administrator=True)
async def cmd_clear(interaction: discord.Interaction, command_name: str):
    gid = str(interaction.guild_id)
    guild_settings[gid]["channel_restrictions"].pop(command_name, None)
    guild_settings[gid]["role_restrictions"].pop(command_name, None)
    await interaction.response.send_message(f"✅ Restrictions cleared for `/{command_name}`.",
                                             view=make_dismiss_view(interaction.user.id))

@tree.command(name="settings", description="View current command restrictions")
@app_commands.default_permissions(administrator=True)
async def cmd_settings(interaction: discord.Interaction):
    gid = str(interaction.guild_id); s = guild_settings[gid]
    embed = discord.Embed(title="⚙️ Server Settings", color=0x7289da)
    ch = s["channel_restrictions"]
    embed.add_field(name="Channel Restrictions",
                    value="\n".join(f"`/{k}` → " + " ".join(f"<#{c}>" for c in v) for k,v in ch.items()) or "None",
                    inline=False)
    ro = s["role_restrictions"]
    embed.add_field(name="Role Restrictions",
                    value="\n".join(f"`/{k}` → " + " ".join(f"<@&{r}>" for r in v) for k,v in ro.items()) or "None",
                    inline=False)
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(interaction.user.id), ephemeral=True)

# ═══════════════════════════════════════════════════════════════════════════════
# GENERAL
# ═══════════════════════════════════════════════════════════════════════════════

@tree.command(name="help", description="All commands")
async def cmd_help(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Commands", color=0x5865F2, timestamp=datetime.datetime.utcnow())
    sections = {
        "💰 Crypto":     ["/price", "/chart", "/top", "/compare", "/trending", "/fomo", "/coins"],
        "🥇 Commodities":["/commodity  (gold · silver · oil · gas · platinum · palladium · copper · wheat · corn)"],
        "🎵 Music":      ["/play", "/skip", "/stop", "/queue", "/nowplaying"],
        "🚬 Smoking":    ["/smoke  (facts·funny·quit·timeline·rules·brand·random)",
                          "/smokebreak", "/dailysmokes", "/quittrack", "/quitstats", "/cravingkiller"],
        "⚙️ Admin":      ["/setcmdchannel", "/setcmdrole", "/clearcmdrestrictions", "/settings"],
    }
    for sec,cmds in sections.items():
        embed.add_field(name=sec, value="\n".join(f"`{c}`" for c in cmds), inline=False)
    embed.set_footer(text="Only the person who ran a command can dismiss its response")
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(interaction.user.id), ephemeral=True)

@tree.command(name="ping", description="Bot latency")
async def cmd_ping(interaction: discord.Interaction):
    ms    = round(bot.latency*1000)
    color = 0x00ff88 if ms<100 else 0xffaa00 if ms<200 else 0xff4444
    embed = discord.Embed(title="🏓 Pong", description=f"**{ms}ms**", color=color)
    await interaction.response.send_message(embed=embed, view=make_dismiss_view(interaction.user.id))

# ═══════════════════════════════════════════════════════════════════════════════
# EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    print(f"\n{'='*50}\n  {bot.user}  ({bot.user.id})\n  Guilds: {len(bot.guilds)}\n{'='*50}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Sync error: {e}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="📈 Markets | /help"))

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"Cmd error: {error}")
    msg = f"❌ {error}"
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            await interaction.followup.send(msg, ephemeral=True)
    except: pass

# ═══════════════════════════════════════════════════════════════════════════════
# KEEPALIVE + MAIN
# ═══════════════════════════════════════════════════════════════════════════════

async def keepalive():
    from aiohttp import web
    app = web.Application()
    async def health(r): return web.Response(text="🟢 alive")
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT","8080")))
    await site.start()
    print(f"Health check on :{os.getenv('PORT','8080')}")

async def main():
    async with bot:
        await keepalive()
        await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Set BOT_TOKEN env var"); sys.exit(1)
    asyncio.run(main())
