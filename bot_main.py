import discord
from discord.ext import commands

# ------------------------------
# Fonctions d'extraction par salon
# ------------------------------

def extract_winamax(content):
    """
    Pour le salon Winamax (ID : 1338248759578071161)
    Message d'origine :
      @Winamax_10 #GrosseCoteBoostéeWinamax 
      
      La Grosse Cote Boostée : Philadelphia Eagles - Kansas City Chiefs
      Kansas City Chiefs gagne le Super Bowl : 1.86 → 2.5 ! :rocket: 
      BOOST de 34.4%
      https://astuces-paris-sportifs.fr/winamax
      
      :arrow_right: http://discord.gg/YjBjctWwnR : Bots de conversion...
      
    On conserve uniquement la partie :
      La Grosse Cote Boostée : Philadelphia Eagles - Kansas City Chiefs
      Kansas City Chiefs gagne le Super Bowl : 1.86 → 2.5 ! :rocket: 
      BOOST de 34.4%
    """
    # On découpe le message en lignes en supprimant les espaces superflus et en ignorant les lignes vides.
    lines = [line.strip() for line in content.splitlines() if line.strip() != ""]
    for i, line in enumerate(lines):
        if line.startswith("La Grosse Cote Boostée"):
            # On prend cette ligne et les deux suivantes
            return "\n".join(lines[i:i+3])
    return None


def extract_betclic(content):
    """
    Pour le salon Betclic (ID : 1338248781711544411)
    Message d'origine :
      @Betclic_10 SUPER  BOOOOST 
       Paris SG  -  Monaco 
       O. Dembélé ou M. Biereth buteur 
       1,53  →  2,10 
      https://astuces-paris-sportifs.fr/betclic
      
      :arrow_right: http://discord.gg/YjBjctWwnR : Bots de conversion...
      
    On conserve uniquement :
      SUPER  BOOOOST 
       Paris SG  -  Monaco 
       O. Dembélé ou M. Biereth buteur 
       1,53  →  2,10
    """
    lines = [line.strip() for line in content.splitlines() if line.strip() != ""]
    if not lines:
        return None
    # Sur la première ligne, on retire le mot commençant par '@'
    words = lines[0].split()
    filtered = [word for word in words if not word.startswith("@")]
    first_line = " ".join(filtered)
    # On suppose que le texte à garder s'étale sur 4 lignes (la première + les 3 suivantes)
    extracted = [first_line] + lines[1:4]
    return "\n".join(extracted)


def extract_unibet(content):
    """
    Pour le salon Unibet (ID : 1338248845712298085)
    Message d'origine :
      @Unibet_Flash_10 Flash Bet (10€ max)
      
      Football - Ligue des Champions - 29/01 18:30
      Stuttgart - Paris SG
      Barcola, Dembélé ou Doué buteur
      Remboursé si un joueur non titulaire
      1.64 -> 2.1
      BOOST de 28.0%
      https://astuces-paris-sportifs.fr/unibet
      
    On conserve uniquement (en supprimant la première ligne) :
      Football - Ligue des Champions - 29/01 18:30
      Stuttgart - Paris SG
      Barcola, Dembélé ou Doué buteur
      Remboursé si un joueur non titulaire
      1.64 -> 2.1
      BOOST de 28.0%
    """
    lines = [line.strip() for line in content.splitlines() if line.strip() != ""]
    if len(lines) < 2:
        return None
    # On ignore la première ligne (qui contient la mention et le titre Flash Bet)
    extracted = lines[1:]
    # On arrête dès qu'une ligne commence par "http"
    extracted = [line for line in extracted if not line.startswith("http")]
    return "\n".join(extracted)


def extract_zebet(content):
    """
    Pour le salon ParionsSport / Zebet (ID : 1338248892109684857)
    Message d'origine :
      @Fdj_10 @Zebet_10 Cote Boostee 10€ FDJ et Zebet 
      
      CB Live - Marseille marque le 1er but du match ? 
      1.55 → 1.85 ! 
      BOOST de 19.4% 
      https://astuces-paris-sportifs.fr/zebet
      https://astuces-paris-sportifs.fr/fdj
      
      :arrow_right: http://discord.gg/YjBjctWwnR : Bots de conversion...
      
    On conserve uniquement :
      Cote Boostee 10€ FDJ et Zebet 
      CB Live - Marseille marque le 1er but du match ? 
      1.55 → 1.85 ! 
      BOOST de 19.4%
    """
    lines = [line.strip() for line in content.splitlines() if line.strip() != ""]
    if not lines:
        return None
    # Sur la première ligne, on retire tous les mots qui commencent par '@'
    words = lines[0].split()
    filtered = [word for word in words if not word.startswith("@")]
    first_line = " ".join(filtered)
    extracted = [first_line]
    # On ajoute les lignes suivantes jusqu'à rencontrer une ligne débutant par "http"
    for line in lines[1:]:
        if line.startswith("http"):
            break
        extracted.append(line)
    return "\n".join(extracted)


# ------------------------------
# Configuration du bot et des salons
# ------------------------------

intents = discord.Intents.default()
intents.message_content = True  # N'oubliez pas d'activer cette option dans le portail développeur

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionnaire de configuration par salon :
# Pour chaque salon, on définit :
#   - "role_id"   : l'identifiant du rôle à mentionner
#   - "extractor" : la fonction qui extrait la partie du message souhaitée
CHANNEL_CONFIG = {
    1338248759578071161: {
        "role_id": 1338490009304436817,  # Rôle pour Winamax
        "extractor": extract_winamax
    },
    1338248781711544411: {
        "role_id": 1338549047174107227,  # Rôle pour Betclic
        "extractor": extract_betclic
    },
    1338248845712298085: {
        "role_id": 1338549108121669682,  # Rôle pour Unibet
        "extractor": extract_unibet
    },
    1338248892109684857: {
        "role_id": 1338549141743337583,  # Rôle pour ParionsSport / Zebet
        "extractor": extract_zebet
    }
}

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    # On ignore les messages envoyés par des bots pour éviter les boucles infinies.
    if message.author.bot:
        return

    # Vérifier si le message provient d'un salon configuré
    config = CHANNEL_CONFIG.get(message.channel.id)
    if config:
        # Extraction du contenu souhaité via la fonction dédiée
        extracted_text = config["extractor"](message.content)
        if not extracted_text:
            # Si l'extraction n'a rien donné, on quitte.
            return

        # Récupération du rôle à mentionner dans le serveur
        role = message.guild.get_role(config["role_id"])
        if role:
            extracted_text += f" {role.mention}"
        else:
            extracted_text += " (rôle non trouvé)"

        # Suppression du message original
        try:
            await message.delete()
        except Exception as e:
            print(f"Erreur lors de la suppression du message : {e}")

        # Envoi du nouveau message dans le même salon
        await message.channel.send(extracted_text)

    # Permettre le traitement ultérieur d'éventuelles commandes
    await bot.process_commands(message)

# Démarrage du bot
bot.run("MTMzODU0Njk4NDE3NjMyMDUxMg.GaC-GK.UrZEJXmVM1oazKsivBQ3-5BLFunrhGfJQ4gD_c")
