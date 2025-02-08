# bot.py

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# AMP API
import ampapi

# Load environment variables from .env file
load_dotenv()

####################
# Retrieve sensitive information
####################
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Error: DISCORD_BOT_TOKEN is not set in .env")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID")) if os.getenv("DISCORD_GUILD_ID") else None
WELCOME_CHANNEL_ID = int(os.getenv("DISCORD_WELCOME_CHANNEL_ID")) if os.getenv("DISCORD_WELCOME_CHANNEL_ID") else None

# AMP-related credentials from .env
AMP_HOST = os.getenv("AMP_HOST", "127.0.0.1")
AMP_USERNAME = os.getenv("AMP_USERNAME", "admin")
AMP_PASSWORD = os.getenv("AMP_PASSWORD", "password")

####################
# Create bot instance
####################
intents = discord.Intents.all()

# Disable the default help command so we can use our own
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"🚀 Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    """Sends a welcome message when a user joins the server."""
    if WELCOME_CHANNEL_ID:
        channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            embed = create_embed(
                title="👋 Welcome!",
                description=f"Welcome to the server, {member.mention}! We're glad to have you here! 🎉",
                color=0x00FF00
            )
            await channel.send(embed=embed)

####################
# Utility: Create an embed
####################
def create_embed(title: str, description: str, color: int = 0x3498DB) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    return embed

####################
# AMP Client Setup
####################
# Minimal example using provided environment variables
# For a real environment, ensure you are using SSL if appropriate.

api_params = ampapi.dataclass.APIParams(AMP_HOST, AMP_USERNAME, AMP_PASSWORD)
bridge: ampapi.Bridge = ampapi.Bridge(api_params=api_params)

####################
# Slash Ping Command
####################
@bot.slash_command(name="ping", guild_ids=[GUILD_ID], description="Replies with Pong!")
async def ping_slash(ctx):
    """Slash command that responds with an embedded Pong message."""
    latency_ms = round(bot.latency * 1000)
    embed = create_embed(
        title="🏓 Pong!",
        description=f"⌛ Latency: {latency_ms} ms",
        color=0x1ABC9C
    )
    await ctx.respond(embed=embed)

####################
# Server Info Commands
####################
@bot.slash_command(name="discordinfo", guild_ids=[GUILD_ID], description="Displays basic server info.")
async def serverinfo_slash(ctx):
    """Displays basic server info via slash command."""
    guild = ctx.guild

    embed = create_embed(
        title="🛠️ Server Info",
        description=f"Some basic info about {guild.name}",
        color=0x5865F2
    )

    embed.add_field(name="Server Name", value=guild.name, inline=False)
    embed.add_field(name="Server ID", value=guild.id, inline=False)
    embed.add_field(name="Owner", value=str(guild.owner), inline=False)
    embed.add_field(name="Member Count", value=guild.member_count, inline=False)

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await ctx.respond(embed=embed)

####################
# Custom Help Commands
####################
@bot.slash_command(name="help", guild_ids=[GUILD_ID], description="Show list of available slash commands.")
async def help_slash(ctx):
    """Displays a list of available commands (slash-based)."""
    embed = create_embed(
        title="❓ Help",
        description="List of available slash commands:",
        color=0x3498DB
    )
    embed.add_field(name="/ping", value="Responds with bot latency.", inline=False)
    embed.add_field(name="/discordinfo", value="Currently shows Discord guild info.", inline=False)
    embed.add_field(name="/serverinfo", value="Queries AMP for server data (like “uptime” and “state”).", inline=False)
    embed.add_field(name="/instances", value="Show all available instances.", inline=False)
    embed.add_field(name="/start_instance <instance_name>", value="Start a specified instance.", inline=False)
    embed.add_field(name="/stop_instance <instance_name>", value="Stop a specified instance.", inline=False)
    
    await ctx.respond(embed=embed)

####################
# Basic AMP Command
####################
@bot.slash_command(name="serverinfo", guild_ids=[GUILD_ID], description="Retrieve basic info from AMP.")
async def ampinfo_slash(ctx):
    """Displays the status of the server instance."""
    try:
        # Initialize Core module
        _core = ampapi.Core()
        
        # Fetch info from AMP
        info_data = await _core.get_status(format_data=False)
        
        # Determine server status
        server_status = "🟢 Running" if info_data.get("state", 0) == 999 else "🔴 Stopped"
        uptime = info_data.get("uptime", "Unknown")

        # Create embed response
        embed = create_embed(
            title="🟢 Server Status",
            description="Current server instance information.",
            color=0xFFA500
        )
        embed.add_field(name="🔹 Status", value=server_status, inline=False)
        embed.add_field(name="⏳ Uptime", value=str(uptime), inline=False)
    
    except Exception as e:
        embed = create_embed(
            title="❌ Server Error",
            description=f"An error occurred while retrieving server info.\n```{str(e)}```",
            color=0xFF0000
        )

    await ctx.respond(embed=embed)

####################
# Command to show all available instances
####################
@bot.slash_command(name="instances", guild_ids=[GUILD_ID], description="Show all available instances.")
async def instances_slash(ctx):
    """Displays a list of available instances in the Server."""
    try:
        ads_module = ampapi.ADSModule()
        controllers = await ads_module.get_instances()
        
        if not controllers or not controllers[0].available_instances:
            embed = create_embed(
                title="📜 Instances List",
                description="No instances found.",
                color=0xFFA500
            )
        else:
            controller = controllers[0]  # Assuming the first returned element is the Controller
            
            embed = create_embed(
                title=f"📜 Instances on the server",
                description=f"Total Instances: {len(controller.available_instances) - 1}",
                color=0xFFA500
            )
            _counter = 1;
            for instance in controller.available_instances[1:]:  # Skip the first instance
                instance_status = "🟢 Running" if instance.running else "🔴 Stopped"
                embed.add_field(
                    name=f"[{_counter}] {instance.friendly_name}",
                    value=f"**Status:** {instance_status}\n**Instance ID**: {instance.instance_id}\n**Instance Name**: {instance.instance_name}",
                    inline=False
                )
                _counter += 1
    except Exception as e:
        embed = create_embed(
            title="❌ Server Error",
            description=f"An error occurred while retrieving instances.\n```{str(e)}```",
            color=0xFF0000
        )
    
    await ctx.respond(embed=embed)

####################
# Command to start an instance with error handling
####################
@bot.slash_command(name="start_instance", guild_ids=[GUILD_ID], description="Start a specified instance.")
async def start_instance_slash(ctx, instance_name: str):
    """Starts a given Server instance."""
    try:
        ads_module = ampapi.ADSModule()
        result = await ads_module.start_instance(instance_name)
        
        if not isinstance(result, ampapi.dataclass.ActionResult) or not result.status:
            reason = result.reason if hasattr(result, 'reason') else "Please, make sure the instance name is correct."
            raise ValueError(reason)

        embed = create_embed(
            title="✅ Instance Started",
            description=f"Successfully started instance: **{instance_name}**",
            color=0x00FF00
        )
    except ValueError as e:
        embed = create_embed(
            title="❌ Instance Start Failed",
            description=f"Failed to start instance: **{instance_name}**\n**Reason:** {str(e)}",
            color=0xFF0000
        )
    except Exception as e:
        embed = create_embed(
            title="❌ Server Error",
            description=f"An unexpected error occurred.\n```{str(e)}```",
            color=0xFF0000
        )
    
    await ctx.respond(embed=embed)

####################
# Command to stop an instance with error handling
####################
@bot.slash_command(name="stop_instance", guild_ids=[GUILD_ID], description="Stop a specified instance.")
async def stop_instance_slash(ctx, instance_name: str):
    """Stops a given Server instance."""
    try:
        ads_module = ampapi.ADSModule()
        result = await ads_module.stop_instance(instance_name)
        
        if not isinstance(result, ampapi.dataclass.ActionResult) or not result.status:
            reason = result.reason if hasattr(result, 'reason') else "Please, make sure the instance name is correct."
            raise ValueError(reason)

        embed = create_embed(
            title="🛑 Instance Stopped",
            description=f"Successfully stopped instance: **{instance_name}**",
            color=0xFFA500
        )
    except ValueError as e:
        embed = create_embed(
            title="❌ Instance Stop Failed",
            description=f"Failed to stop instance: **{instance_name}**\n**Reason:** {str(e)}",
            color=0xFF0000
        )
    except Exception as e:
        embed = create_embed(
            title="❌ Server Error",
            description=f"An unexpected error occurred.\n```{str(e)}```",
            color=0xFF0000
        )
    
    await ctx.respond(embed=embed)

####################
# Run the bot
####################
if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not set in .env")
    else:
        bot.run(TOKEN)
