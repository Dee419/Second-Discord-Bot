import discord
from discord.ext import commands

from AdminCommands import Admin_Commands
from FunCommands import Fun_Commands

print("Setting up intents")
intents = discord.Intents.default()
intents.members = True
intents.messages = True
print("Setting up bot")
bot = commands.Bot(command_prefix='.', intents=intents)
bot.add_cog(Admin_Commands(bot))
bot.add_cog(Fun_Commands(bot))

# Used to see when the bot is available
@bot.event
async def on_ready():
    print("Bot started!")

print("Starting bot")
bot.run("OTg3MzE4NTkwMTkxNTgzMzAy.GmC2Kq.7bdFq5L1JZq-vUSd6EePT2m8F7pKR1AMhVSMY0")