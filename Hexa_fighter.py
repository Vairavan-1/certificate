# Hexa_fighter.py
# A Telegram bot that analyzes Pokémon battles using type effectiveness.
import asyncio
import requests
from telethon import TelegramClient, events

# ==========================================
# 🔐 CONFIGURATION (ENTER YOUR KEYS HERE)
# ==========================================
API_ID = 28040000       # Get from my.telegram.org
API_HASH = '550c3d7584aeb83bca45df5671522428'   # Get from my.telegram.org
BOT_TOKEN = '7235199113:AAFrts9BlJzMMpMSgfApJNqS9eRn3yBW-AQ' # Get from @BotFather

# ==========================================
# 🏆 YOUR GOD SQUAD (EXACT MOVESETS)
# ==========================================
MY_TEAM = {
    'snorlax': {
        'Giga Impact': 'normal',
        'Earthquake': 'ground',
        'Wild Charge': 'electric',
        'Rock Slide': 'rock'
    },
    'zacian': {
        'Giga Impact': 'normal',
        'Iron Head': 'steel',
        'Wild Charge': 'electric',
        'Close Combat': 'fighting'
    },
    'excadrill': {
        'Giga Impact': 'normal',
        'Earthquake': 'ground',
        'Smart Strike': 'steel',
        'Rock Slide': 'rock'
    },
    'dragonite': {
        'Outrage': 'dragon',
        'Earthquake': 'ground',
        'Aerial Ace': 'flying',
        'Thunderbolt': 'electric'
    },
    'zoroark': { 
        'Hyper Beam': 'normal',
        'Flamethrower': 'fire',
        'Sludge Bomb': 'poison',
        'Shadow Ball': 'ghost'
    },
    'charizard': {
        'Hyper Beam': 'normal',
        'Fire Blast': 'fire',
        'Flamethrower': 'fire',
        'Air Slash': 'flying'
    }
}

# ==========================================
# 🧠 TYPE CHART (ATTACKER vs DEFENDER)
# ==========================================
TYPE_CHART = {
    'normal':   {'rock': 0.5, 'ghost': 0, 'steel': 0.5},
    'fire':     {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 2, 'bug': 2, 'rock': 0.5, 'dragon': 0.5, 'steel': 2},
    'water':    {'fire': 2, 'water': 0.5, 'grass': 0.5, 'ground': 2, 'rock': 2, 'dragon': 0.5},
    'electric': {'water': 2, 'electric': 0.5, 'grass': 0.5, 'ground': 0, 'flying': 2, 'dragon': 0.5},
    'grass':    {'fire': 0.5, 'water': 2, 'grass': 0.5, 'poison': 0.5, 'ground': 2, 'flying': 0.5, 'bug': 0.5, 'rock': 2, 'dragon': 0.5, 'steel': 0.5},
    'ice':      {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 0.5, 'ground': 2, 'flying': 2, 'dragon': 2, 'steel': 0.5},
    'fighting': {'normal': 2, 'ice': 2, 'poison': 0.5, 'flying': 0.5, 'psychic': 0.5, 'bug': 0.5, 'rock': 2, 'ghost': 0, 'dark': 2, 'steel': 2, 'fairy': 0.5},
    'poison':   {'grass': 2, 'poison': 0.5, 'ground': 0.5, 'rock': 0.5, 'ghost': 0.5, 'steel': 0, 'fairy': 2},
    'ground':   {'fire': 2, 'electric': 2, 'grass': 0.5, 'poison': 2, 'flying': 0, 'bug': 0.5, 'rock': 2, 'steel': 2},
    'flying':   {'electric': 0.5, 'grass': 2, 'fighting': 2, 'bug': 2, 'rock': 0.5, 'steel': 0.5},
    'psychic':  {'fighting': 2, 'poison': 2, 'psychic': 0.5, 'dark': 0, 'steel': 0.5},
    'bug':      {'fire': 0.5, 'grass': 2, 'fighting': 0.5, 'poison': 0.5, 'flying': 0.5, 'psychic': 2, 'ghost': 0.5, 'dark': 2, 'steel': 0.5, 'fairy': 0.5},
    'rock':     {'fire': 2, 'ice': 2, 'fighting': 0.5, 'ground': 0.5, 'flying': 2, 'bug': 2, 'steel': 0.5},
    'ghost':    {'normal': 0, 'psychic': 2, 'ghost': 2, 'dark': 0.5},
    'dragon':   {'dragon': 2, 'steel': 0.5, 'fairy': 0},
    'dark':     {'fighting': 0.5, 'psychic': 2, 'ghost': 2, 'dark': 0.5, 'fairy': 0.5},
    'steel':    {'fire': 0.5, 'water': 0.5, 'electric': 0.5, 'ice': 2, 'rock': 2, 'steel': 0.5, 'fairy': 2},
    'fairy':    {'fire': 0.5, 'fighting': 2, 'poison': 0.5, 'dragon': 2, 'dark': 2, 'steel': 0.5}
}

# ==========================================
# ⚙️ LOGIC ENGINE
# ==========================================

def get_multiplier(move_type, defender_types):
    """Calculates damage based on one or two enemy types."""
    mult = 1.0
    for dtype in defender_types:
        if move_type in TYPE_CHART:
            # If relationship exists, multiply. If not, stays same (1.0).
            mult *= TYPE_CHART[move_type].get(dtype, 1.0)
    return mult

def get_enemy_types(name):
    """Fetches real data from the cloud (PokeAPI)."""
    try:
        # Handling special names (e.g. Tapu Koko -> tapu-koko)
        clean_name = name.lower().replace(' ', '-').replace('.', '')
        url = f"https://pokeapi.co/api/v2/pokemon/{clean_name}"
        
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            return [t['type']['name'] for t in data['types']]
        else:
            return None
    except:
        return None

# ==========================================
# 🤖 BOT HANDLER
# ==========================================

bot = TelegramClient('battle_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern=r'(?i)(.+) vs (.+)'))
async def battle_analysis(event):
    text = event.text
    parts = text.split(' vs ')
    
    if len(parts) < 2: return

    enemy_name = parts[0].strip()
    my_name = parts[1].strip().lower()

    # 1. Validate My Pokemon
    if my_name not in MY_TEAM:
        valid_list = ", ".join([n.title() for n in MY_TEAM.keys()])
        await event.reply(f"❌ **Error:** '{my_name}' is not in your team.\n**Available:** {valid_list}")
        return

    # 2. Get Enemy Data (API Call)
    status_msg = await event.reply(f"📡 Scanning **{enemy_name}**...")
    enemy_types = get_enemy_types(enemy_name)

    if not enemy_types:
        await status_msg.edit(f"❌ **Error:** Could not find '{enemy_name}' in the database.\nTry checking spelling (e.g., 'Ho-Oh', 'Tapu Koko').")
        return

    # 3. Calculate Moves
    moves_data = []
    my_moves = MY_TEAM[my_name]

    for move_name, move_type in my_moves.items():
        dmg = get_multiplier(move_type, enemy_types)
        moves_data.append((dmg, move_name, move_type))

    # Sort: Highest damage first
    moves_data.sort(key=lambda x: x[0], reverse=True)
    best_move = moves_data[0]

    # 4. Create Response
    # Header Icon
    if best_move[0] >= 4.0: head = "☠️ **INSTANT KILL**"
    elif best_move[0] >= 2.0: head = "🔥 **SUPER EFFECTIVE**"
    elif best_move[0] < 1.0: head = "⚠️ **DISADVANTAGE**"
    else: head = "⚔️ **NEUTRAL MATCH**"

    response = (
        f"{head}\n"
        f"👹 **Target:** {enemy_name.upper()} ({' / '.join(enemy_types).upper()})\n"
        f"🛡️ **Using:** {my_name.title()}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 **USE THIS:** `{best_move[1]}`\n"
        f"✨ **Type:** {best_move[2].upper()}\n"
        f"💥 **Power:** {best_move[0]}x Multiplier\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📜 **All Options:**\n"
    )

    for dmg, name, mtype in moves_data:
        icon = "✅"
        if dmg >= 2.0: icon = "🌟"
        if dmg < 1.0: icon = "🔻"
        if dmg == 0.0: icon = "🚫"
        response += f"{icon} **{name}**: {dmg}x\n"

    await status_msg.delete()
    await event.reply(response)

# ==========================================
# 🚀 SYSTEM START
# ==========================================
print("✅ Battle Computer Online. Connect via Telegram.")
bot.run_until_disconnected()