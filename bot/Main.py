import discord
from discord.ext import commands
from discord import app_commands
import datetime

# Configuration
ALLOWED_SERVER_IDS = [1352986883302359071]  # Replace with your server IDs
BOT_TOKEN = "MTM2Mzg4MzAzMjEwMDA3NzU3OA.GGM_jz.Z0-_M6YIAk4KdIrYLV8zjrEQIgJD3355Jx8S-o"  # Replace with your bot token

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

# Custom responses
CUSTOM_COMMANDS = {
    "uncopylockedmega": "Here are the uncopylocked files from MEGA: [1.https://mega.nz/folder/Qg4QSA7L#aVDYnY3fy8CqNvI_1LFGfA 2.https://mega.nz/folder/p0gXDYTB#v4Q4ljt2x2nOYDeUptbBTA 3.https://mega.nz/folder/k95yiQ5b#TehXlS1IO6ALrWyC-Na42w]",
    "uncopylockedgofile": "Here are the uncopylocked files from GoFile: [1.https://gofile.io/d/zZtiA2]",
    "youtube": "Check out my YouTube channel: [https://www.youtube.com/@streetlord528]",
    "abdi": """**Available Commands:**

**Custom Commands:**
!uncopylockedmega - Sends files from MEGA
!uncopylockedgofile - Sends files from GoFile
!youtube - Sends my YouTube channel
?membercount - Shows server member count
?abdi - Shows this help menu

**Slash Commands:**
/kick <member> <reason> - Kicks a member
/ban <member> <reason> - Bans a member
/warn <member> <reason> - Warns a member
/timeout <member> <duration> <reason> - Timeouts a member (1y, 1m, 1w, 1d)
/untimeout <member> - Removes timeout from member
/lock - Locks the current channel
/unlock - Unlocks the current channel
/lock <channel> <duration> - Locks specific channel
/unlock <channel> - Unlocks specific channel
/givemods <game> - Provides mods for specified game (GTA 5, Roblox, CSGO, Minecraft)"""
}

async def is_allowed_server(interaction_or_ctx):
    """Check if the command is being used in an allowed server"""
    guild_id = interaction_or_ctx.guild.id if hasattr(interaction_or_ctx, 'guild') else interaction_or_ctx.message.guild.id
    return guild_id in ALLOWED_SERVER_IDS

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # Check all current servers and leave unauthorized ones
    for guild in bot.guilds:
        if guild.id not in ALLOWED_SERVER_IDS:
            print(f"Leaving unauthorized server: {guild.name} (ID: {guild.id})")
            await guild.leave()
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.event
async def on_guild_join(guild):
    """Automatically leave any server that isn't whitelisted"""
    if guild.id not in ALLOWED_SERVER_IDS:
        print(f"Left unauthorized server: {guild.name} (ID: {guild.id})")
        await guild.leave()
        try:
            owner = await guild.fetch_member(guild.owner_id)
            await owner.send(f"Sorry, this bot is private and can only be used in specific servers.")
        except:
            pass

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Ignore messages from non-whitelisted servers
    if message.guild and message.guild.id not in ALLOWED_SERVER_IDS:
        return
    
    # Handle custom commands
    for cmd, response in CUSTOM_COMMANDS.items():
        if message.content.lower().startswith(f'!{cmd}'):
            await message.channel.send(response)
            return
    
    await bot.process_commands(message)

@bot.command()
async def membercount(ctx):
    if not await is_allowed_server(ctx):
        return
    await ctx.send(f"Total members: {ctx.guild.member_count}")

# Slash commands with server restriction check
async def server_check(interaction: discord.Interaction) -> bool:
    if interaction.guild_id not in ALLOWED_SERVER_IDS:
        await interaction.response.send_message("❌ This bot is private and cannot be used in this server.", ephemeral=True)
        return False
    return True

@bot.tree.command(name="kick", description="Kicks a member from the server")
@app_commands.describe(member="The member to kick", reason="The reason for kicking")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not await server_check(interaction):
        return
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("You don't have permission to kick members!", ephemeral=True)
        return
    
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member.mention} has been kicked. Reason: {reason}")

@bot.tree.command(name="ban", description="Bans a member from the server")
@app_commands.describe(member="The member to ban", reason="The reason for banning")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not await server_check(interaction):
        return
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("You don't have permission to ban members!", ephemeral=True)
        return
    
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member.mention} has been banned. Reason: {reason}")

@bot.tree.command(name="warn", description="Warns a member")
@app_commands.describe(member="The member to warn", reason="The reason for warning")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not await server_check(interaction):
        return
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You don't have permission to warn members!", ephemeral=True)
        return
    
    await interaction.response.send_message(f"{member.mention} has been warned. Reason: {reason}")

@bot.tree.command(name="timeout", description="Timeouts a member")
@app_commands.describe(
    member="The member to timeout",
    duration="Duration (1y, 1m, 1w, 1d)",
    reason="The reason for timeout"
)
async def timeout(interaction: discord.Interaction, member: discord.Member, duration: str, reason: str):
    if not await server_check(interaction):
        return
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You don't have permission to timeout members!", ephemeral=True)
        return
    
    # Parse duration
    try:
        amount = int(duration[:-1])
        unit = duration[-1].lower()
        
        if unit == 'y':
            delta = datetime.timedelta(days=amount*365)
        elif unit == 'm':
            delta = datetime.timedelta(days=amount*30)
        elif unit == 'w':
            delta = datetime.timedelta(weeks=amount)
        elif unit == 'd':
            delta = datetime.timedelta(days=amount)
        else:
            raise ValueError
        
        await member.timeout(delta, reason=reason)
        await interaction.response.send_message(
            f"{member.mention} has been timed out for {duration}. Reason: {reason}"
        )
    except:
        await interaction.response.send_message("Invalid duration format! Use like 1y, 1m, 1w, 1d", ephemeral=True)

@bot.tree.command(name="untimeout", description="Removes timeout from a member")
@app_commands.describe(member="The member to untimeout")
async def untimeout(interaction: discord.Interaction, member: discord.Member):
    if not await server_check(interaction):
        return
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You don't have permission to untimeout members!", ephemeral=True)
        return
    
    await member.timeout(None)
    await interaction.response.send_message(f"Timeout removed for {member.mention}")

@bot.tree.command(name="lock", description="Locks the current channel")
async def lock(interaction: discord.Interaction):
    if not await server_check(interaction):
        return
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("You don't have permission to lock channels!", ephemeral=True)
        return
    
    channel = interaction.channel
    await channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Channel locked!")

@bot.tree.command(name="unlock", description="Unlocks the current channel")
async def unlock(interaction: discord.Interaction):
    if not await server_check(interaction):
        return
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("You don't have permission to unlock channels!", ephemeral=True)
        return
    
    channel = interaction.channel
    await channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Channel unlocked!")

@bot.tree.command(name="givemods", description="Provides mods for specified game")
@app_commands.describe(game="The game to get mods for")
@app_commands.choices(game=[
    app_commands.Choice(name="GTA 5", value="gta5"),
    app_commands.Choice(name="Roblox", value="roblox"),
    app_commands.Choice(name="CSGO", value="csgo"),
    app_commands.Choice(name="Minecraft", value="minecraft")
])
async def givemods(interaction: discord.Interaction, game: app_commands.Choice[str]):
    if not await server_check(interaction):
        return
    mod_links = {
        "gta5": "Here are GTA 5 mods: [https://gofile.io/d/dwL4h8]",
        "roblox": "Here are Roblox mods: [coming soon...]",
        "csgo": "Here are CSGO mods Make sure to get the pin: [https://undetek.com/free-cs2-cheats-download/]",
        "minecraft": "Here are Minecraft mods: [Comming soon...]"
    }
    await interaction.response.send_message(mod_links[game.value])

bot.run("MTM2Mzg4MzAzMjEwMDA3NzU3OA.GGM_jz.Z0-_M6YIAk4KdIrYLV8zjrEQIgJD3355Jx8S-o")
