import os
import discord
from discord.ext import commands

# ------------------------------
# Fonctions d'extraction par salon
# ------------------------------

def extract_winamax(content):
    lines = [line.strip() for line in content.splitlines() if line.strip() != ""]
    for i, line in enumerate(lines):
        if line.startswith("La Grosse Cote Boostée"):
            return "\n".join(lines[i:i+3])
    return None


def extract_betclic(content):
    lines = [line.strip() for line in content.splitlines() if line.strip() != ""]
    if not lines:
        return None
    words = lines[0].split()
    filtered = [word for word in words if not word.startswith("@")]
    first_line = " ".join(filtered)
    extracted = [first_line] + lines[1:4]
    return "\n".join(extracted)


def extract_unibet(content):
    lines = [line.strip() for line in content.splitlines() if line.strip() != ""]
    if len(lines) < 2:
        return None
    extracted = lines[1:]
    extracted = [line for line in extracted if not line.startswith("http")]
    return "\n".join(extracted)


def extract_zebet(content):
    lines = [line.strip() for line in content.splitlines() if line.strip() != ""]
    if not lines:
        return None
    words = lines[0].split()
    filtered = [word for word in words if not word.startswith("@")]
    first_line = " ".join(filtered)
    extracted = [first_line]
    for line in lines[1:]:
        if line.startswith("http"):
            break
        extracted.append(line)
    return "\n".join(extracted)


# ------------------------------
# Configuration du bot et des salons
# ------------------------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_CONFIG = {
    1349321379601842176: {
        "role_id": 1349362506413375579,  # Rôle pour Winamax
        "extractor": extract_winamax
    },
    1349321396513148989: {
        "role_id": 1349362562743009342,  # Rôle pour Betclic
        "extractor": extract_betclic
    },
    1349321427106533376: {
        "role_id": 1349362656397627462,  # Rôle pour Unibet
        "extractor": extract_unibet
    },
    1349321459402674177: {
        "role_id": 1349362610121736333,  # Rôle pour ParionsSport / Zebet
        "extractor": extract_zebet
    }
}

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    config = CHANNEL_CONFIG.get(message.channel.id)
    if config:
        extracted_text = config["extractor"](message.content)
        if not extracted_text:
            return

        role = message.guild.get_role(config["role_id"])
        if role:
            extracted_text += f" {role.mention}"
        else:
            extracted_text += " (rôle non trouvé)"

        try:
            await message.delete()
        except Exception as e:
            print(f"Erreur lors de la suppression du message : {e}")

        await message.channel.send(extracted_text)

    await bot.process_commands(message)

# ------------------------------
# Lancement du bot avec TOKEN protégé
# ------------------------------

TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

bot.run(TOKEN)
