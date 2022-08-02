import discord
import datetime

INFO = discord.Color.from_rgb(114, 137, 218)
SUCCESS = discord.Color.from_rgb(59, 165, 93)
ERROR = discord.Color.from_rgb(220, 20, 60)
WARNING = discord.Color.from_rgb(255, 215, 0)

def create_embed(title, description, footer=None, time=None, color="INFO"):
    if color == "WARNING":
        color = WARNING
    elif color == "SUCCESS":
        color = SUCCESS
    elif color == "ERROR":
        color = ERROR
    else:
        color = INFO
    embed = discord.Embed(title=title, description=description, color=color)

    if time == True:
        embed.timestamp = datetime.datetime.now()
    if footer is not None and isinstance(footer, str):
        embed.set_footer(text=footer)
    return embed