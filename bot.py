import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# On bot ready


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='!help'))

# Ping command


@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Run the bot
bot.run(os.environ.get("DISCORD_TOKEN"))
