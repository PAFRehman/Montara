import os, sys, asyncio, time, random, io, datetime, re, json
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
    "gold":      {"symbol":"XAU","name":"Gold",              "emoji":"🥇","unit":"oz",     "fallback":3320.0,"coingecko_proxy":None},
    "silver":    {"symbol":"XAG","name":"Silver",            "emoji":"🥈","unit":"oz",     "fallback":32.5,  "coingecko_proxy":None},
    "platinum":  {"symbol":"XPT","name":"Platinum",          "emoji":"⚪","unit":"oz",     "fallback":980.0, "coingecko_proxy":None},
    "palladium": {"symbol":"XPD","name":"Palladium",         "emoji":"⚙️","unit":"oz",     "fallback":970.0, "coingecko_proxy":None},
    "oil":       {"symbol":"BRENTOIL","name":"Brent Crude",  "emoji":"🛢️","unit":"bbl",    "fallback":85.0,  "coingecko_proxy":None},
    "gas":       {"symbol":"NATGAS","name":"Natural Gas",    "emoji":"🔥","unit":"MMBtu",  "fallback":2.8,   "coingecko_proxy":None},
    "copper":    {"symbol":"COPPER","name":"Copper",         "emoji":"🟤","unit":"lb",     "fallback":4.2,   "coingecko_proxy":None},
    "wheat":     {"symbol":"WHEAT","name":"Wheat",           "emoji":"🌾","unit":"bu",     "fallback":560.0, "coingecko_proxy":None},
    "corn":      {"symbol":"CORN","name":"Corn",             "emoji":"🌽","unit":"bu",     "fallback":450.0, "coingecko_proxy":None},
    "coffee":    {"symbol":"KC.F","name":"Coffee (Arabica)", "emoji":"☕","unit":"lb",     "fallback":2.75,  "coingecko_proxy":None},
    "sugar":     {"symbol":"SB.F","name":"Sugar #11",       "emoji":"🍬","unit":"lb",     "fallback":0.145, "coingecko_proxy":None},
    "cocoa":     {"symbol":"CC.F","name":"Cocoa",           "emoji":"🍫","unit":"ton",    "fallback":3800.0,"coingecko_proxy":None},
    "cotton":    {"symbol":"CT.F","name":"Cotton",          "emoji":"👕","unit":"lb",     "fallback":0.79,  "coingecko_proxy":None},
    "lumber":    {"symbol":"LB.F","name":"Lumber",          "emoji":"🪵","unit":"board ft","fallback":590.0,"coingecko_proxy":None},
    "oj":        {"symbol":"OJ.F","name":"Orange Juice",    "emoji":"🍊","unit":"lb",     "fallback":1.60,  "coingecko_proxy":None},
    "cattle":    {"symbol":"LE.F","name":"Live Cattle",     "emoji":"🐄","unit":"lb",     "fallback":2.45,  "coingecko_proxy":None},
    "hogs":      {"symbol":"HE.F","name":"Lean Hogs",       "emoji":"🐖","unit":"lb",     "fallback":1.02,  "coingecko_proxy":None},
    "feeder":    {"symbol":"GF.F","name":"Feeder Cattle",   "emoji":"🐂","unit":"lb",     "fallback":3.60,  "coingecko_proxy":None},
    "milk":      {"symbol":"DL.F","name":"Class III Milk",  "emoji":"🥛","unit":"cwt",    "fallback":17.5,  "coingecko_proxy":None},
}

# ── SMOKING DATA ──────────────────────────────────────────────────────────────
SMOKING = {
    "funny": [
        ("🚬 Cigarettes: the only product that kills its best customers.", None),
        ("💨 7,000+ chemicals in smoke — but hey, at least it's organic.", None),
        ("😂 A cigarette is like a friend — it hangs around, costs money, and slowly kills you.", None),
        ("🤔 Cigarettes are like squirrels — harmless until you put one in your mouth.", None),
        ("😎 Smoking: turning oxygen into personality since 1492.", None),
        ("🎭 Every cigarette is a tiny drama in 5 minutes.", None),
        ("🚬 Smoking cures salmon. Coincidence? Nobody thinks about that.", None),
        ("🏃 A smoker ran a marathon once. He needed 6 cigarette breaks but finished.", None),
        ("🌫️ Smoking doesn't kill you, it just makes you look cool while slowly regretting it.", None),
        ("💨 Smokers never get cold in winter — they've always got a light.", None),
        ("🧯 Smoking is just a hobby — you collect ash and regret.", None),
        ("🎪 Lighting up outside in the rain? That's not addiction, that's dedication.", None),
        ("📦 A smoker's greatest fear? Reaching in the pack and touching cardboard.", None),
        ("⏰ 'I'll quit Monday' — said every smoker since 1965.", None),
        ("🔦 Smokers are the most prepared people — always got a lighter, always got a reason.", None),
    ],
    "health": [
        ("🫁 Smoker's lungs look like charcoal filters — useful for Brita, bad for breathing.", None),
        ("❤️ Smoking increases heart disease risk by 2–4x. Your heart's working overtime.", None),
        ("🧠 Nicotine rewires your brain's reward system — it literally hijacks your dopamine.", None),
        ("⏳ Each cigarette costs ~11 minutes of life. That's 3.5 years per pack-a-day smoker.", None),
        ("🔬 Secondhand smoke contains 70 known carcinogens. Sharing is NOT caring.", None),
        ("👃 Smoking kills your sense of smell within months. Food starts tasting like cardboard.", None),
        ("🦷 Smokers are 3x more likely to lose their teeth. The mouth suffers first.", None),
        ("💪 Smoking reduces muscle recovery time by up to 40% — athletes hate this one.", None),
        ("👁️ Macular degeneration risk doubles with smoking. Your vision is literally burning.", None),
        ("🩸 Carbon monoxide from smoke binds to hemoglobin 200x stronger than oxygen.", None),
        ("🧬 Smoking damages DNA in ways that can persist even after quitting.", None),
        ("💊 Smokers need higher doses of many medications — drugs metabolize faster.", None),
        ("🤰 Smoking during pregnancy reduces infant birth weight by an average of 200g.", None),
        ("🛌 Nicotine disrupts REM sleep — smokers average 30 min less deep sleep per night.", None),
        ("⚗️ Formaldehyde, arsenic, benzene, cadmium — all in cigarette smoke. You're a chemistry lab.", None),
    ],
    "dangerous": [
        ("☠️ Tobacco kills 8 million people globally every year. More than malaria, HIV, and tuberculosis combined.", None),
        ("🔥 Cigarettes are the #1 cause of preventable house fires worldwide.", None),
        ("💰 Big Tobacco knew cigarettes were addictive since the 1950s. They hid it for 40 years.", None),
        ("🧪 Cigarette filters don't protect you — they're marketing illusions. Proven useless.", None),
        ("📊 1 in 2 lifetime smokers will die from a tobacco-related illness. That's not a stat, it's a coin flip.", None),
        ("🏭 Tobacco farming destroys 600 million trees per year for curing and packaging.", None),
        ("👦 90% of adult smokers started before age 18. The industry KNEW.", None),
        ("💉 Nicotine is classified as a Schedule III drug in many countries — as addictive as heroin.", None),
        ("🌍 Tobacco companies specifically targeted developing nations when Western regulations tightened.", None),
        ("🚼 800,000 deaths/year are attributed to secondhand smoke exposure. Innocent bystanders.", None),
        ("🧒 Children of smokers are 3x more likely to become smokers themselves. The cycle is engineered.", None),
        ("💸 The healthcare cost of smoking globally exceeds $1.4 TRILLION per year.", None),
        ("🎯 Menthol cigarettes were proven to be specifically marketed to Black communities in the US.", None),
        ("📱 Vaping companies use the same psychological hooks Big Tobacco used on kids in the 80s.", None),
        ("⚖️ Tobacco is the only legal product that, when used as intended, kills the user.", None),
    ],
    "rules": [
        ("🚬 Rule #1: Always have a lighter. Always. Pockets without lighters are just pockets.", None),
        ("🤝 Rule #2: Never refuse to give a light. Smoker code is sacred.", None),
        ("🚭 Rule #3: Never bum 3 in a row without buying a pack. You're a guest, not a supplier.", None),
        ("🌬️ Rule #4: Blow smoke away from non-smokers. Basic humanity.", None),
        ("☕ Rule #5: Coffee + cigarette is a sacred pairing. It shall not be disrespected.", None),
        ("🌧️ Rule #6: Smoking in rain hits different. It's cinematic. Own it.", None),
        ("🚗 Rule #7: Window down, arm out — the classic car smoke. Timeless.", None),
        ("🌅 Rule #8: First smoke after morning coffee? Undefeated. Hall of fame.", None),
        ("🍺 Rule #9: Post-meal cigarette is automatically elite. No debate.", None),
        ("🏁 Rule #10: Last cigarette in the pack always tastes the best. Science.", None),
        ("🧂 Rule #11: Never tap ash on someone's floor. You're a smoker, not an animal.", None),
        ("👀 Rule #12: If someone's clearly trying to quit, don't offer them one. Respect the journey.", None),
        ("🎶 Rule #13: Night smoke + good music = unreplicable vibe. Guard this.", None),
        ("📵 Rule #14: Don't smoke during a serious conversation. People deserve your full attention.", None),
        ("🏠 Rule #15: Always ask before smoking inside someone's space. Always.", None),
    ],
    "brands": [
        ("🏷️ Marlboro: The cowboy's cigarette. Rugged, iconic. The iPhone of cigarettes — you just know what it is.", None),
        ("🏷️ Camel: 'More doctors smoke Camels' they said in 1950. Aged like milk. Still a classic.", None),
        ("🏷️ Newport: Menthol gang rises. Cool on the way in, cancer on the way out. Very consistent.", None),
        ("🏷️ Lucky Strike: WWII era vibes. Basically a vintage collectible that also destroys your lungs.", None),
        ("🏷️ Dunhill: The business-class cigarette. You're paying for the feeling of premium regret.", None),
        ("🏷️ Parliament: Recessed filter = 'I'm fancy about my addiction.' Respect the commitment.", None),
        ("🏷️ Winston: 'No additives.' For the health-conscious smoker. The kale salad of cigarettes. 😂", None),
        ("🏷️ Benson & Hedges: British royalty smoked these. You're basically committing treason against your lungs.", None),
        ("🏷️ Pall Mall: Budget-friendly. The value investor of cigarettes. Same death, less wallet pain.", None),
        ("🏷️ Cohiba: A Cuban cigar that costs more per stick than most people's lunch. Elite suffering.", None),
        ("🏷️ Sobranie Black Russian: Gold tip, black paper, $100+/pack. Villain cigarette. Supervillain, actually.", None),
        ("🏷️ American Spirit: 'Natural tobacco.' Like saying your arsenic is organic. Impressive marketing.", None),
        ("🏷️ Clove Djarums: Indonesian, smells like a bakery, hits like a freight train. Cultural artifact.", None),
        ("🏷️ Rothmans: The sophisticate's choice. Bond would smoke these if he needed to look even more mysterious.", None),
        ("🏷️ More (the long ones): 120mm cigarettes for people who felt regular cigarettes weren't commitment enough.", None),
    ],
}

# ── GIVEAWAY STORE ────────────────────────────────────────────────────────────
active_giveaways = {}  # message_id -> giveaway_data

# ── STATE ─────────────────────────────────────────────────────────────────────
guild_settings  = defaultdict(lambda: {"channel_restrictions": {}, "role_restrictions": {}})
music_queues    = defaultdict(list)
now_playing     = {}

# ── BOT SETUP ─────────────────────────────────────────────────────────────────
intents = discord.Intents.all()
bot  = commands.Bot(command_prefix="!", intents=intents, help_command=None)
tree = bot.tree

# ── HELPERS ───────────────────────────────────────────────────────────────────
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

async def fetch_json(url, params=None, headers=None):
    async with aiohttp.ClientSession() as s:
        async with s.get(url, params=params, headers=headers,
                         timeout=aiohttp.ClientTimeout(total=12)) as r:
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

# ── COMMODITY LIVE PRICE (multi-source with robust fallbacks) ─────────────────
async def fetch_commodity_price(key: str):
    info = COMMODITIES[key]
    sym  = info["symbol"]

    if sym in ("XAU","XAG","XPT","XPD"):
        try:
            data = await fetch_json(f"https://api.metals.live/v1/spot/{sym.lower()}")
            if isinstance(data, list) and data:
                val = list(data[0].values())[0]
                if val and float(val) > 0:
                    return float(val), False, "metals.live"
        except: pass

        try:
            data = await fetch_json(f"https://api.frankfurter.app/latest?from=USD&to={sym}")
            rate = data.get("rates", {}).get(sym)
            if rate and float(rate) > 0:
                return round(1 / float(rate), 2), False, "frankfurter"
        except: pass

        try:
            metal_map = {"XAU": "gold", "XAG": "silver", "XPT": "platinum", "XPD": "palladium"}
            metal_name = metal_map[sym]
            data = await fetch_json(
                f"https://commodities-api.com/api/latest?access_key=demo&base=USD&symbols={sym}",
            )
            rate = data.get("data", {}).get("rates", {}).get(sym)
            if rate and float(rate) > 0:
                return round(1 / float(rate), 2), False, "commodities-api"
        except: pass

    stooq_map = {
        "BRENTOIL": "@CL.F", "NATGAS": "@NG.F", "COPPER": "HG.F",
        "WHEAT": "@W.F",    "CORN":   "@C.F",
        "KC.F":  "KC.F",    "SB.F":   "SB.F",  "CC.F":  "CC.F",
        "CT.F":  "CT.F",    "LB.F":   "LB.F",  "OJ.F":  "OJ.F",
        "LE.F":  "LE.F",    "HE.F":   "HE.F",  "GF.F":  "GF.F",
        "DL.F":  "DL.F",
        "XAU": "XAUUSD","XAG": "XAGUSD","XPT": "XPTUSD","XPD": "XPDUSD",
    }
    stooq_sym = stooq_map.get(sym)
    if stooq_sym:
        try:
            url = f"https://stooq.com/q/l/?s={stooq_sym}&f=sd2t2ohlcv&h&e=csv"
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    text = await r.text()
            lines = [l for l in text.strip().split("\n") if l and "N/D" not in l]
            if len(lines) >= 2:
                cols  = lines[-1].split(",")
                price = float(cols[4])
                if price > 0:
                    return price, False, "stooq"
        except: pass

    yf_map = {
        "XAU": "GC=F", "XAG": "SI=F", "XPT": "PL=F", "XPD": "PA=F",
        "BRENTOIL": "BZ=F", "NATGAS": "NG=F", "COPPER": "HG=F",
        "WHEAT": "ZW=F", "CORN": "ZC=F",
        "KC.F": "KC=F", "SB.F": "SB=F", "CC.F": "CC=F",
        "CT.F": "CT=F", "LB.F": "LBS=F", "OJ.F": "OJ=F",
        "LE.F": "LE=F", "HE.F": "HE=F", "GF.F": "GF=F",
    }
    yf_sym = yf_map.get(sym)
    if yf_sym:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_sym}?interval=1d&range=1d"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            data = await fetch_json(url, headers=headers)
            result = data.get("chart", {}).get("result", [])
            if result:
                meta  = result[0].get("meta", {})
                price = meta.get("regularMarketPrice") or meta.get("previousClose")
                if price and float(price) > 0:
                    return float(price), False, "yahoo"
        except: pass

    return info["fallback"], True, "fallback"

async def fetch_commodity_history(key: str, days: int = 30):
    info    = COMMODITIES[key]
    sym     = info["symbol"]
    yf_map  = {
        "XAU": "GC=F", "XAG": "SI=F", "XPT": "PL=F", "XPD": "PA=F",
        "BRENTOIL": "BZ=F", "NATGAS": "NG=F", "COPPER": "HG=F",
        "WHEAT": "ZW=F", "CORN": "ZC=F",
        "KC.F": "KC=F", "SB.F": "SB=F", "CC.F": "CC=F",
        "CT.F": "CT=F", "LB.F": "LBS=F", "OJ.F": "OJ=F",
        "LE.F": "LE=F", "HE.F": "HE=F", "GF.F": "GF=F",
    }
    yf_sym  = yf_map.get(sym)
    now_ts  = int(time.time())
    period1 = now_ts - days * 86400

    if yf_sym:
        try:
            url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_sym}"
                   f"?interval=1d&period1={period1}&period2={now_ts}")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            data = await fetch_json(url, headers=headers)
            result = data.get("chart", {}).get("result", [])
            if result:
                timestamps = result[0].get("timestamp", [])
                closes     = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
                pairs = [(datetime.datetime.fromtimestamp(t), c)
                         for t, c in zip(timestamps, closes) if c is not None]
                if len(pairs) >= 5:
                    return pairs, False
        except Exception as e:
            print(f"Yahoo history error: {e}")

    live_price, _, _ = await fetch_commodity_price(key)
    np.random.seed(int(live_price * 13) % 99991)
    noise  = np.cumsum(np.random.randn(days) * live_price * 0.008)
    series = np.clip(live_price + noise - noise[-1], live_price * 0.82, live_price * 1.18)
    series[-1] = live_price
    dates  = [datetime.datetime.utcnow() - datetime.timedelta(days=days-i-1) for i in range(days)]
    return list(zip(dates, series.tolist())), True

# ── CHART GENERATORS ──────────────────────────────────────────────────────────
async def crypto_chart_buf(coin_id: str, days: int) -> io.BytesIO | None:
    try:
        interval = "daily" if days > 2 else "hourly"
        data = await fetch_json(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
            {"vs_currency": "usd", "days": days, "interval": interval}
        )
        prices = data.get("prices", [])
        if not prices: return None

        ts  = [datetime.datetime.fromtimestamp(p[0] / 1000) for p in prices]
        vs  = [p[1] for p in prices]
        chg = ((vs[-1] - vs[0]) / vs[0]) * 100
        col = "#00ff88" if chg >= 0 else "#ff4455"

        fig, ax = plt.subplots(figsize=(12, 5), facecolor="#0d1117")
        ax.set_facecolor("#0d1117")
        ax.plot(ts, vs, color=col, linewidth=2.2, zorder=5)
        ax.fill_between(ts, vs, min(vs) * 0.995, alpha=0.22, color=col)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d" if days > 2 else "%H:%M"))
        ax.tick_params(colors="#888", labelsize=8)
        for spine in ax.spines.values(): spine.set_color("#222")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: fmt_price(x)))
        ax.set_title(f"{coin_id.upper()} — {days}d", color="white", fontsize=13, pad=8)
        ax.grid(True, color="#1e2430", linewidth=0.6, linestyle="--")
        badge_col = "#00ff88" if chg >= 0 else "#ff4455"
        ax.annotate(f"{'▲' if chg >= 0 else '▼'} {abs(chg):.2f}%",
                    xy=(0.01, 0.93), xycoords="axes fraction",
                    color=badge_col, fontsize=11, fontweight="bold")
        ax.annotate(fmt_price(vs[-1]),
                    xy=(1.0, vs[-1]), xycoords=("axes fraction", "data"),
                    xytext=(5, 0), textcoords="offset points",
                    color="white", fontsize=8, va="center")
        plt.tight_layout(pad=0.8)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#0d1117")
        plt.close(fig)
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Crypto chart error: {e}")
        return None

async def commodity_chart_buf(key: str, days: int = 30) -> io.BytesIO | None:
    try:
        info  = COMMODITIES[key]
        pairs, is_estimated = await fetch_commodity_history(key, days)
        if not pairs: return None

        dates  = [p[0] for p in pairs]
        series = [p[1] for p in pairs]
        chg    = ((series[-1] - series[0]) / series[0]) * 100
        col    = "#00ff88" if chg >= 0 else "#ff4455"

        fig, ax = plt.subplots(figsize=(12, 5), facecolor="#0d1117")
        ax.set_facecolor("#0d1117")
        ax.plot(dates, series, color=col, linewidth=2.2, zorder=5)
        ax.fill_between(dates, series, min(series) * 0.995, alpha=0.22, color=col)

        if days <= 7:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        elif days <= 90:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))

        ax.tick_params(colors="#888", labelsize=8)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=20, ha="right")
        for spine in ax.spines.values(): spine.set_color("#222")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.2f}"))

        unit = info['unit']
        title = f"{info['emoji']} {info['name']} — {days}d  |  ${series[-1]:,.2f}/{unit}"
        if is_estimated: title += "  ⚠ est."
        ax.set_title(title, color="white", fontsize=12, pad=8)
        ax.grid(True, color="#1e2430", linewidth=0.6, linestyle="--")

        badge_col = "#00ff88" if chg >= 0 else "#ff4455"
        ax.annotate(f"{'▲' if chg >= 0 else '▼'} {abs(chg):.2f}% ({days}d)",
                    xy=(0.01, 0.93), xycoords="axes fraction",
                    color=badge_col, fontsize=10, fontweight="bold")

        ax.axhline(max(series), color="#444", linewidth=0.8, linestyle=":", alpha=0.7)
        ax.axhline(min(series), color="#444", linewidth=0.8, linestyle=":", alpha=0.7)
        ax.annotate(f"H: ${max(series):,.2f}", xy=(0.01, 0.06), xycoords="axes fraction",
                    color="#aaa", fontsize=7)
        ax.annotate(f"L: ${min(series):,.2f}", xy=(0.13, 0.06), xycoords="axes fraction",
                    color="#aaa", fontsize=7)

        plt.tight_layout(pad=0.8)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#0d1117")
        plt.close(fig)
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Commodity chart error: {e}")
        return None

# ── MUSIC — RAILWAY-OPTIMIZED YTDLP ──────────────────────────────────────────
FFMPEG_OPTS = {
    "before_options": (
        "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
        "-probesize 200M -analyzeduration 200M "
        "-reconnect_at_eof 1"
    ),
    "options": (
        "-vn -ar 48000 -ac 2 -b:a 192k "
        "-af loudnorm=I=-14:TP=-1.5:LRA=11,volume=1.5"
    ),
}

def _build_ydl_opts(strategy: str = "default") -> dict:
    cookie_file    = os.getenv("YTDLP_COOKIES", "")
    cookie_browser = os.getenv("YTDLP_COOKIES_BROWSER", "")
    proxy          = os.getenv("YTDLP_PROXY", "")
    custom_ua      = os.getenv("YTDLP_USER_AGENT", "")
    po_token       = os.getenv("YOUTUBE_PO_TOKEN", "")

    base = {
        "format": (
            "bestaudio[ext=webm][acodec=opus][abr>90]/"
            "bestaudio[ext=m4a][acodec=aac][abr>90]/"
            "bestaudio[abr>90]/bestaudio/best"
        ),
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "source_address": "0.0.0.0",
        "noplaylist": True,
        "geo_bypass": True,
        "socket_timeout": 15,
        "retries": 3,
        "fragment_retries": 5,
        "http_headers": {
            "User-Agent": custom_ua or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Sec-Fetch-Mode": "navigate",
        },
    }

    if proxy:
        base["proxy"] = proxy

    # Strategy-specific player client selection with PO token support
    strategy_map = {
        "default":     {"player_client": ["web", "web_creator", "android", "tv_embedded"]},
        "web_creator":   {"player_client": ["web_creator"], "po_token": [po_token] if po_token else []},
        "android":     {"player_client": ["android", "android_music"]},
        "tv":          {"player_client": ["tv_embedded", "web_embedded"]},
        "web_embedded":{"player_client": ["web_embedded"], "player_skip": ["webpage", "configs", "js"]},
        "ios":         {"player_client": ["ios", "ios_music"]},
        "mweb":        {"player_client": ["mweb"]},
    }

    base["extractor_args"] = {
        "youtube": {
            **strategy_map.get(strategy, strategy_map["default"]),
            "player_skip": [],
        }
    }

    # Add PO token to default strategy too if available
    if po_token and strategy == "default":
        base["extractor_args"]["youtube"]["po_token"] = [po_token]

    if cookie_file and os.path.exists(cookie_file):
        base["cookies"] = cookie_file
    elif cookie_browser:
        base["cookiesfrombrowser"] = (cookie_browser,)

    return base

async def get_spotify_token() -> str | None:
    client_id     = os.getenv("SPOTIFY_CLIENT_ID", "")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return None
    try:
        import base64
        creds   = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {creds}",
                   "Content-Type": "application/x-www-form-urlencoded"}
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://accounts.spotify.com/api/token",
                data={"grant_type": "client_credentials"},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get("access_token")
    except Exception as e:
        print(f"Spotify token error: {e}")
    return None

async def resolve_spotify(url_or_id: str) -> dict | None:
    sp_re = re.compile(
        r'https?://open\.spotify\.com/(track|album|playlist|artist)/([a-zA-Z0-9]+)'
    )
    m = sp_re.search(url_or_id)
    if not m:
        return None

    sp_type = m.group(1)
    sp_id   = m.group(2)

    try:
        oembed_url = f"https://open.spotify.com/oembed?url=https://open.spotify.com/{sp_type}/{sp_id}"
        async with aiohttp.ClientSession() as s:
            async with s.get(oembed_url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    data   = await r.json()
                    title  = data.get("title", "")
                    artist = data.get("author_name", "")

                    if sp_type == "track":
                        search = f"{artist} - {title} official audio"
                    elif sp_type == "album":
                        search = f"{artist} {title} full album"
                    elif sp_type == "playlist":
                        search = f"{artist} {title} playlist"
                    else:
                        search = f"{artist} best songs"

                    return {
                        "title":        title,
                        "artist":       artist,
                        "album":        title if sp_type == "album" else "",
                        "duration_ms":  0,
                        "search_query": search,
                        "source":       "oembed",
                    }
    except Exception as e:
        print(f"Spotify oEmbed error: {e}")

    token = await get_spotify_token()
    if token and sp_type == "track":
        try:
            headers = {"Authorization": f"Bearer {token}"}
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"https://api.spotify.com/v1/tracks/{sp_id}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as r:
                    if r.status == 200:
                        d       = await r.json()
                        title   = d.get("name", "")
                        artists = ", ".join(a["name"] for a in d.get("artists", []))
                        album   = d.get("album", {}).get("name", "")
                        dur_ms  = d.get("duration_ms", 0)
                        return {
                            "title":        title,
                            "artist":       artists,
                            "album":        album,
                            "duration_ms":  dur_ms,
                            "search_query": f"{artists} - {title} official audio",
                            "source":       "spotify_api",
                        }
        except Exception as e:
            print(f"Spotify API track error: {e}")

    return {
        "title":        f"Spotify {sp_type}",
        "artist":       "",
        "album":        "",
        "duration_ms":  0,
        "search_query": f"spotify {sp_type} {sp_id}",
        "source":       "fallback",
    }

def smart_search_query(raw: str) -> str:
    raw = raw.strip()
    if re.match(r'https?://', raw):
        return raw

    dash_match = re.match(r'^(.+?)\s*[-–]\s*(.+)$', raw)
    if dash_match:
        artist = dash_match.group(1).strip()
        song   = dash_match.group(2).strip()
        return f"{artist} - {song} official audio"

    by_match = re.match(r'^(.+?)\s+by\s+(.+)$', raw, re.IGNORECASE)
    if by_match:
        song   = by_match.group(1).strip()
        artist = by_match.group(2).strip()
        return f"{artist} - {song} official audio"

    kv = {}
    for key in ("artist", "song", "track"):
        match = re.search(rf'{key}[:\s]+([^,\n]+)', raw, re.IGNORECASE)
        if match:
            kv[key] = match.group(1).strip()
    if "artist" in kv and ("song" in kv or "track" in kv):
        song = kv.get("song") or kv.get("track")
        return f"{kv['artist']} - {song} official audio"

    return f"{raw} audio"

async def resolve_audio(query: str):
    import yt_dlp

    original_query = query.strip()
    spotify_info   = None

    if "open.spotify.com" in original_query:
        spotify_info = await resolve_spotify(original_query)
        if spotify_info:
            query = spotify_info["search_query"]
            print(f"Spotify → YouTube search: {query}")
        else:
            query = re.sub(r'https?://\S+', '', original_query).strip() or original_query

    elif not re.match(r'https?://', original_query):
        query = smart_search_query(original_query)
        print(f"Smart search query: {query}")

    # Try strategies with PO token first, then fall back
    strategies = ["web_creator", "default", "android", "tv", "ios", "mweb", "web_embedded"]
    loop = asyncio.get_event_loop()

    last_error = None
    for strategy in strategies:
        opts = _build_ydl_opts(strategy)
        try:
            def _extract(q=query, o=opts):
                with yt_dlp.YoutubeDL(o) as ydl:
                    info = ydl.extract_info(q, download=False)
                    if "entries" in info:
                        info = info["entries"][0]

                    fmts = [
                        f for f in info.get("formats", [])
                        if f.get("acodec") != "none"
                        and f.get("vcodec") in ("none", None, "")
                        and f.get("url")
                    ]
                    if fmts:
                        fmts.sort(key=lambda f: (f.get("abr") or 0), reverse=True)
                        url = fmts[0]["url"]
                    else:
                        url = info.get("url")

                    yt_title = info.get("title", q)
                    return url, yt_title, info.get("thumbnail"), info.get("duration", 0)

            url, yt_title, thumb, dur = await loop.run_in_executor(None, _extract)
            print(f"Resolved '{query}' using strategy: {strategy}")

            if spotify_info:
                if spotify_info.get("artist"):
                    display_title = f"{spotify_info['artist']} — {spotify_info['title']}"
                else:
                    display_title = spotify_info['title']
                if spotify_info.get("album") and spotify_info["album"] != spotify_info["title"]:
                    display_title += f"\n*{spotify_info['album']}*"
            else:
                display_title = yt_title

            return url, display_title, thumb, dur

        except Exception as e:
            last_error = e
            err_str = str(e)
            if "Sign in to confirm" in err_str or "bot" in err_str.lower() or "po_token" in err_str.lower():
                print(f"Strategy '{strategy}' blocked, retrying... ({e})")
                await asyncio.sleep(0.5)
                continue
            raise

    raise Exception(f"All bypass strategies failed. Last error: {last_error}")

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
            embed.add_field(name="Quality",  value="🔊 HD 192kbps", inline=True)
            await channel.send(embed=embed)

    except Exception as e:
        print(f"Music resolve error: {e}")
        err_msg = str(e)
        if channel:
            if "Sign in" in err_msg or "bot" in err_msg.lower():
                embed = discord.Embed(
                    title="⚠️ YouTube Bot Detection (Railway)",
                    description=(
                        f"Could not play `{url_or_query}`\n\n"
                        "**Railway Fix Steps:**\n"
                        "1. **Export fresh cookies** from browser using [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbllbjcglkphssphfagmcdpc)\n"
                        "2. **Get PO Token**: Run `yt-dlp --extractor-args \"youtube:player-client=web\" --print \"%(po_token)s\" \"https://youtube.com/watch?v=dQw4w9WgXcQ\"` locally\n"
                        "3. **Set Railway env vars:**\n"
                        "   - `YOUTUBE_COOKIES_CONTENT` = paste cookies.txt content\n"
                        "   - `YOUTUBE_PO_TOKEN` = your PO token\n"
                        "   - `YTDLP_USER_AGENT` = your browser's User-Agent\n"
                        "4. **Redeploy**\n\n"
                        "If still failing, use a residential proxy: `YTDLP_PROXY=http://user:pass@host:port`"
                    ),
                    color=0xff4444
                )
                await channel.send(embed=embed)
            else:
                await channel.send(f"❌ Could not play `{url_or_query}`: {err_msg[:200]}")
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
    buf = await crypto_chart_buf(cid, min(max(days, 1), 365))
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
    count = min(max(count, 1), 20)
    data = await fetch_json("https://api.coingecko.com/api/v3/coins/markets", {
        "vs_currency": "usd", "order": "market_cap_desc", "per_page": count, "page": 1,
        "price_change_percentage": "24h",
    })
    embed = discord.Embed(title=f"🏆 Top {count} Cryptos", color=0xf7931a,
                          timestamp=datetime.datetime.utcnow())
    rows = []
    for i, c in enumerate(data, 1):
        chg = c.get("price_change_percentage_24h") or 0
        dot = "🟢" if chg >= 0 else "🔴"
        rows.append(f"**#{i}** {c['name']} `{c['symbol'].upper()}` — {fmt_price(c['current_price'])}  {dot}{'▲' if chg >= 0 else '▼'}{abs(chg):.2f}%")
    embed.description = "\n".join(rows)
    embed.set_footer(text="CoinGecko")
    await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="compare", description="Compare two cryptos side by side")
@app_commands.describe(coin1="First coin", coin2="Second coin")
async def cmd_compare(interaction: discord.Interaction, coin1: str, coin2: str):
    await interaction.response.defer()
    d1, d2 = await asyncio.gather(fetch_crypto(coin1), fetch_crypto(coin2))
    if not d1 or not d2:
        await interaction.followup.send("❌ Could not find one or both coins.", ephemeral=True); return
    embed = discord.Embed(title=f"⚖️ {d1['name']} vs {d2['name']}", color=0x7289da,
                          timestamp=datetime.datetime.utcnow())
    for label, v1, v2 in [
        ("Price",   fmt_price(d1['price']),          fmt_price(d2['price'])),
        ("24h",     fmt_change(d1['change_24h']),     fmt_change(d2['change_24h'])),
        ("7d",      fmt_change(d1['change_7d']),      fmt_change(d2['change_7d'])),
        ("Mkt Cap", f"${d1['market_cap']:,.0f}" if d1['market_cap'] else "N/A",
                    f"${d2['market_cap']:,.0f}" if d2['market_cap'] else "N/A"),
        ("Rank",    f"#{d1['rank']}" if d1['rank'] else "N/A",
                    f"#{d2['rank']}" if d2['rank'] else "N/A"),
    ]:
        embed.add_field(name=label,
                        value=f"**{d1['symbol']}:** {v1}\n**{d2['symbol']}:** {v2}", inline=True)
    await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="trending", description="Trending coins on CoinGecko right now")
async def cmd_trending(interaction: discord.Interaction):
    await interaction.response.defer()
    data  = await fetch_json("https://api.coingecko.com/api/v3/search/trending")
    coins = data.get("coins", [])[:10]
    embed = discord.Embed(title="🔥 Trending Now", color=0xff6600,
                          timestamp=datetime.datetime.utcnow())
    rows = [
        f"**#{i}** {c['item']['name']} `{c['item']['symbol']}` — Rank #{c['item'].get('market_cap_rank', '?')}"
        for i, c in enumerate(coins, 1)
    ]
    embed.description = "\n".join(rows)
    embed.set_footer(text="CoinGecko trending")
    await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="fomo", description="What if you bought X dollars of a coin N days ago?")
@app_commands.describe(symbol="Coin", amount_usd="USD invested", days_ago="Days ago")
async def cmd_fomo(interaction: discord.Interaction, symbol: str, amount_usd: float, days_ago: int):
    await interaction.response.defer()
    cid  = COIN_MAP.get(symbol.lower(), symbol.lower())
    dstr = (datetime.datetime.utcnow() - datetime.timedelta(days=days_ago)).strftime("%d-%m-%Y")
    hist = await fetch_json(f"https://api.coingecko.com/api/v3/coins/{cid}/history", {"date": dstr})
    past = hist.get("market_data", {}).get("current_price", {}).get("usd")
    cur  = await fetch_crypto(symbol)
    if not past or not cur:
        await interaction.followup.send("❌ Could not fetch historical data.", ephemeral=True); return
    bought = amount_usd / past
    now_v  = bought * cur['price']
    profit = now_v - amount_usd
    pct    = (profit / amount_usd) * 100
    embed  = discord.Embed(title=f"😱 FOMO — {cur['name']}",
                           color=0x00ff88 if profit >= 0 else 0xff4444,
                           timestamp=datetime.datetime.utcnow())
    embed.add_field(name="Invested",     value=f"${amount_usd:,.2f}",  inline=True)
    embed.add_field(name="Days Ago",     value=str(days_ago),           inline=True)
    embed.add_field(name="Price Then",   value=fmt_price(past),         inline=True)
    embed.add_field(name="Price Now",    value=fmt_price(cur['price']), inline=True)
    embed.add_field(name="Coins Bought", value=f"{bought:.6f}",         inline=True)
    embed.add_field(name="Value Now",    value=f"${now_v:,.2f}",        inline=True)
    sign = "🟢 +" if profit >= 0 else "🔴 -"
    embed.add_field(name="P&L", value=f"{sign}${abs(profit):,.2f}  ({'▲' if pct >= 0 else '▼'}{abs(pct):.2f}%)", inline=False)
    await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="coins", description="List all supported coin symbols")
async def cmd_coins(interaction: discord.Interaction):
    syms   = sorted(COIN_MAP.keys())
    chunks = [syms[i:i+40] for i in range(0, len(syms), 40)]
    embed  = discord.Embed(title=f"Supported Coins ({len(syms)})", color=0xf7931a)
    for i, ch in enumerate(chunks[:4]):
        embed.add_field(name=f"{i*40+1}–{min((i+1)*40, len(syms))}",
                        value=" • ".join(f"`{s}`" for s in ch), inline=False)
    embed.set_footer(text="/price <symbol> or /chart <symbol>")
    await interaction.response.send_message(embed=embed,
                                            view=make_dismiss_view(interaction.user.id),
                                            ephemeral=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS — COMMODITIES
# ═══════════════════════════════════════════════════════════════════════════════

COMMODITY_CHOICES = [
    app_commands.Choice(name="🥇 Gold",             value="gold"),
    app_commands.Choice(name="🥈 Silver",           value="silver"),
    app_commands.Choice(name="⚪ Platinum",         value="platinum"),
    app_commands.Choice(name="⚙️ Palladium",        value="palladium"),
    app_commands.Choice(name="🛢️ Oil (Brent)",      value="oil"),
    app_commands.Choice(name="🔥 Natural Gas",      value="gas"),
    app_commands.Choice(name="🟤 Copper",           value="copper"),
    app_commands.Choice(name="🌾 Wheat",            value="wheat"),
    app_commands.Choice(name="🌽 Corn",             value="corn"),
    app_commands.Choice(name="☕ Coffee",           value="coffee"),
    app_commands.Choice(name="🍬 Sugar",            value="sugar"),
    app_commands.Choice(name="🍫 Cocoa",            value="cocoa"),
    app_commands.Choice(name="👕 Cotton",           value="cotton"),
    app_commands.Choice(name="🪵 Lumber",           value="lumber"),
    app_commands.Choice(name="🍊 Orange Juice",     value="oj"),
    app_commands.Choice(name="🐄 Live Cattle",      value="cattle"),
    app_commands.Choice(name="🐖 Lean Hogs",        value="hogs"),
    app_commands.Choice(name="🐂 Feeder Cattle",    value="feeder"),
    app_commands.Choice(name="🥛 Milk",             value="milk"),
]

CHART_DAYS_CHOICES = [
    app_commands.Choice(name="7 Days",   value=7),
    app_commands.Choice(name="14 Days",  value=14),
    app_commands.Choice(name="30 Days",  value=30),
    app_commands.Choice(name="90 Days",  value=90),
    app_commands.Choice(name="180 Days", value=180),
    app_commands.Choice(name="365 Days", value=365),
]

@tree.command(name="commodity", description="Real-time price + chart for commodities")
@app_commands.describe(
    item="Choose a commodity",
    days="Chart timeframe (default: 30 days)"
)
@app_commands.choices(item=COMMODITY_CHOICES, days=CHART_DAYS_CHOICES)
async def cmd_commodity(interaction: discord.Interaction,
                        item: app_commands.Choice[str],
                        days: app_commands.Choice[int] = None):
    if not check_allowed(interaction, "commodity"):
        await interaction.response.send_message("❌ Not allowed here.", ephemeral=True); return

    key      = item.value
    day_val  = days.value if days else 30

    if key not in COMMODITIES:
        await interaction.response.send_message("❌ Unknown commodity.", ephemeral=True); return

    await interaction.response.defer()
    info                    = COMMODITIES[key]
    price, is_fallback, src = await fetch_commodity_price(key)
    buf                     = await commodity_chart_buf(key, day_val)

    color_map = {
        "gold": 0xFFD700, "silver": 0xC0C0C0, "platinum": 0xE5E4E2,
        "palladium": 0xB7B7B7, "oil": 0x2d2d2d, "gas": 0xFF6B35,
    }
    color = color_map.get(key, 0x4a90d9)

    embed = discord.Embed(
        title=f"{info['emoji']} {info['name']} — Live Price",
        description=f"# ${price:,.4f} / {info['unit']}",
        color=color,
        timestamp=datetime.datetime.utcnow()
    )

    if not is_fallback:
        embed.set_footer(text=f"Live price via {src} · Chart: {day_val}d real data (Yahoo Finance)")
    else:
        embed.set_footer(text=f"⚠️ Live fetch failed — showing estimate · Source: {src}")
        embed.add_field(name="⚠️ Note", value="Live price API unavailable. Chart is estimated.", inline=False)

    if buf:
        f = discord.File(buf, filename=f"{key}_chart.png")
        embed.set_image(url=f"attachment://{key}_chart.png")
        await interaction.followup.send(embed=embed, file=f, view=make_dismiss_view(interaction.user.id))
    else:
        await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

@tree.command(name="commodities", description="Show all commodity prices at once")
async def cmd_commodities_all(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="📊 Live Commodity Prices", color=0xFFD700,
                          timestamp=datetime.datetime.utcnow())

    keys = ["gold", "silver", "oil", "gas", "copper", "wheat", "corn", "coffee"]
    results = await asyncio.gather(*[fetch_commodity_price(k) for k in keys])

    for key, (price, is_fb, src) in zip(keys, results):
        info = COMMODITIES[key]
        flag = " ⚠" if is_fb else ""
        embed.add_field(
            name=f"{info['emoji']} {info['name']}{flag}",
            value=f"**${price:,.2f}** / {info['unit']}",
            inline=True
        )

    embed.set_footer(text="Prices via Yahoo Finance / stooq / metals.live · ⚠ = estimated")
    await interaction.followup.send(embed=embed, view=make_dismiss_view(interaction.user.id))

# ═══════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS — MUSIC
# ═══════════════════════════════════════════════════════════════════════════════

@tree.command(name="play", description="Play a song in your voice channel")
@app_commands.describe(query="Song name, YouTube URL, or Spotify track URL")
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
        embed.set_footer(text="🔊 HD 192kbps · loudnorm enabled")
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
        if vc and vc.is_playing():
            vc.stop()
            await i.response.send_message("⏭ Skipped", ephemeral=True)
        else:
            await i.response.send_message("Nothing playing.", ephemeral=True)

    async def stop_cb(i: discord.Interaction):
        vc = i.guild.voice_client
        if vc:
            music_queues[guild_id].clear(); vc.stop(); await vc.disconnect()
            await i.response.send_message("⏹ Stopped & disconnected", ephemeral=True)
        else:
            await i.response.send_message("Not connected.", ephemeral=True)

    async def queue_cb(i: discord.Interaction):
        q = music_queues[guild_id]
        if not q:
            await i.response.send_message("Queue is empty.", ephemeral=True); return
        items = "\n".join(f"`{n+1}.` {u[:60]}" for n, u in enumerate(q[:10]))
        await i.response.send_message(f"**Queue ({len(q)}):**\n{items}", ephemeral=True)

    async def dismiss_cb(i: discord.Interaction):
        if i.user.id != author_id:
            await i.response.send_message("Only the requester can dismiss this.", ephemeral=True); return
        await i.message.delete()

    skip_btn = discord.ui.Button(label="⏭ Skip",   style=discord.ButtonStyle.primary)
    stop_btn = discord.ui.Button(label="⏹ Stop",   style=discord.ButtonStyle.danger)
    q_btn    = discord.ui.Button(label="📋 Queue",  style=discord.ButtonStyle.secondary)
    dis_btn  = discord.ui.Button(label="✖ Dismiss", style=discord.ButtonStyle.secondary)
    skip_btn.callback = skip_cb
    stop_btn.callback = stop_cb
    q_btn.callback    = queue_cb
    dis_btn.callback  = dismiss_cb
    for b in [skip_btn, stop_btn, q_btn, dis_btn]:
        view.add_item(b)
    return view

@tree.command(name="skip", description="Skip the current song")
async def cmd_skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭ Skipped.", view=make_dismiss_view(interaction.user.id))
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
    items = "\n".I see — you're on **Railway**, not Montara. Railway's datacenter IPs are heavily flagged by YouTube. Here's the exact fix.

---

## Railway-Specific Cookie Setup

### The Problem
Railway datacenter IPs are heavily flagged by YouTube. Even with cookies, you often need:
1. **Fresh cookies** (exported within last 30 min)
2. **Matching User-Agent**
3. **PO Token** (YouTube's new bot protection, May 2026)

---

## Step-by-Step: Export Cookies for Railway

### 1. Install Cookie Extension
- **Chrome**: [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbllbjcglkphssphfagmcdpc)
- **Firefox**: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

### 2. Get Your PO Token (CRITICAL - YouTube's new requirement)

YouTube now requires a **PO Token** alongside cookies for cloud IPs.

**Option A - Automatic (Recommended)**
```bash
# Run this ONCE on your local machine with Python installed
pip install yt-dlp
yt-dlp --extractor-args "youtube:player-client=web" --print "%(po_token)s" "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
