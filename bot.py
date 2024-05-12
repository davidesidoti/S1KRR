import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ============== On bot ready


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='!help'))


# ============== Welcome message
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(os.environ.get("SERVER_SPAM_CHANNEL_ID"))
    if channel:
        embed = discord.Embed(title="Benvenuto",
                              description="Leggi le regole e pace.",
                              colour=0xffa000)
        embed.set_image(
            url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnPe5ZpSXK6mfSfR8MSdBeVn6wKC37Gyrxc9MEljKsIw&s")

        embed.set_thumbnail(
            url="https://i.pinimg.com/564x/74/fe/63/74fe63c3739ac9587132fb27ca98efe3.jpg")
        await channel.send(embed=embed)

# ============== Ping command


@bot.command()
async def ping(ctx):
    embed = discord.Embed(title="Il tuo ordine McDonald",
                          colour=0xffa000)
    embed.add_field(name="Richiesta",
                    value=f"<@{ctx.message.author.id}>:\n> !ping",
                    inline=False)
    embed.add_field(name="Risposta",
                    value="<@1238971228597911603>:\n> Pong!",
                    inline=False)
    embed.set_thumbnail(
        url="https://i.pinimg.com/564x/74/fe/63/74fe63c3739ac9587132fb27ca98efe3.jpg")
    await ctx.send(embed=embed)

# ============== Help command


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Assistenza McDonald",
                          description="Tutto quello che posso fare:",
                          colour=0xffa000)
    embed.add_field(name="!ping",
                    value="Se tutto funziona, ti rispondo con pong.\n> Utilizzo:\n```\n!ping\n```",
                    inline=True)
    embed.add_field(name="!ruota",
                    value="Gira la ruota per quando non sai cosa fare.\n> Utilizzo (rimpiazza A, B, C e D con le opzioni che vuoi, separate da virgola:\n```\n!ruota A, B, C, D\n```",
                    inline=True)
    embed.set_thumbnail(
        url="https://i.pinimg.com/564x/74/fe/63/74fe63c3739ac9587132fb27ca98efe3.jpg")
    await ctx.send(embed=embed)

# ============== Ruota command


@bot.command()
async def ruota(ctx, *, arg):
    options = arg.split(',')
    for i in range(len(options)):
        options[i] = options[i].strip()
    selected = random.choice(options)

    embed = discord.Embed(title="La Ruota",
                          colour=0xffa000)
    counter = 1
    for option in options:
        if option == selected:
            embed.add_field(name=f"> Opzione {counter}",
                            value=f"> ✅ {option}",
                            inline=False)
        else:
            embed.add_field(name=f"Opzione {counter}",
                value=f"❌ {option}",
                inline=False)
        counter += 1

    embed.set_thumbnail(
        url="https://cdn-1.webcatalog.io/catalog/wheel-of-names/wheel-of-names-icon-filled-256.png?v=1714776921766")
    await ctx.send(embed=embed)


# Run the bot
bot.run(os.environ.get("DISCORD_TOKEN"))
