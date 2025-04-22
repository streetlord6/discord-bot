import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread

# Initialize Flask app for keeping the bot alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

class ModMenus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="modmenus", description="Get mod menus for games")
    @app_commands.describe(game="Select a game")
    @app_commands.choices(game=[
        app_commands.Choice(name="GTA 5", value="gta5"),
        app_commands.Choice(name="Roblox", value="roblox"),
        app_commands.Choice(name="Minecraft", value="minecraft")
    ])
    async def modmenu(self, interaction: discord.Interaction, game: app_commands.Choice[str]):
        menus = {
            "gta5": "🔫 GTA 5 Mod Menus:\n- gofile: [https://gofile.io/d/qeTnso]",
            "roblox": "🧩 Roblox Exploits:\n- gofile: [coming soon...]",
            "minecraft": "⛏ Minecraft Hacks:\n- gofile: [Coming soon...]"
        }
        await interaction.response.send_message(menus[game.value])

async def setup(bot):
    await bot.add_cog(ModMenus(bot))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('wsg')
    try:
        await setup(bot)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Start the Flask server and run the bot
keep_alive()
bot.run("MTM2Mzg4MzAzMjEwMDA3NzU3OA.GGM_jz.Z0-_M6YIAk4KdIrYLV8zjrEQIgJD3355Jx8S-o")  # Replace with your actual token