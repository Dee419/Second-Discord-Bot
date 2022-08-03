import discord
import json
import datetime
from discord.ext import commands
from Embed import create_embed

# Import cogs
from AdminCommands import Admin_Commands
from FunCommands import Fun_Commands

print("Setting up intents")
intents = discord.Intents.default()
intents.members = True
intents.messages = True

print("Initializing bot and loading cogs")
bot = commands.Bot(command_prefix='.', intents=intents)
bot.add_cog(Admin_Commands(bot))
bot.add_cog(Fun_Commands(bot))

# Used to see when the bot is available
@bot.event
async def on_ready():
    print("Bot started!")

@bot.event
async def on_guild_join(guild):
    with open('DataBase.json') as file:
        data = json.load(file)
    for server in data['servers']:
        # First check if the server is already in the database
        if server['guild_id'] == guild.id:
            return
    # If the server is not yet in the database we must add it to the database
    to_add = {
        "guild_id": guild.id,
        "chat_log_channel_id": 0,
        "welcome_channel": 0
    }
    data['servers'].append(to_add)
    with open('DataBase.json', 'w') as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_message_delete(message):
    # First check if the server is in the database
    chat_log_channel_id = None
    with open('DataBase.json') as file:
        data = json.load(file)
    for server in data['servers']:
        if server['guild_id'] == message.guild.id:
            chat_log_channel_id = server['chat_log_channel_id']
    if chat_log_channel_id is not None and chat_log_channel_id != 0:
        chat_log_channel = bot.get_channel(chat_log_channel_id)
        
        time = (datetime.datetime.now()).strftime("%H:%M:%S")
        today = (datetime.date.today()).strftime("%d/%m/%Y")
        created_at = (message.created_at + datetime.timedelta(hours=2)).strftime("%a, %d %b %Y %H:%M:%S")
        if message.content == "":
            content = "**No text to display**"
        else:
            content = message.content
        if len(message.attachments) > 0:
            embed = create_embed(f":wastebasket: {message.author}'s message sent on {created_at} CET was deleted ({message.id})", f"{content}", f"Channel: {message.channel.name} | {today} - {time} CET | User ID: {message.author.id}", color="ERROR")
            for image in message.attachments:
                embed.add_field(name="**Deleted attachment:**", value=f"{image}", inline=False)
        else:
            embed = create_embed(f":wastebasket: {message.author}'s message sent on {created_at} CET was deleted ({message.id})", f"{content}", f"Channel: {message.channel.name} | {today} - {time} CET | User ID: {message.author.id}", color="ERROR")
        await chat_log_channel.send(embed = embed)

@bot.event
async def on_message_edit(before, after):
    # First check if the server is in the database
    chat_log_channel_id = None
    with open('DataBase.json') as file:
        data = json.load(file)
    for server in data['servers']:
        if server['guild_id'] == before.guild.id:
            chat_log_channel_id = server['chat_log_channel_id']
    if chat_log_channel_id is not None and chat_log_channel_id != 0:
        chat_log_channel = bot.get_channel(chat_log_channel_id)
        
        time = (datetime.datetime.now()).strftime("%H:%M:%S")
        today = (datetime.date.today()).strftime("%d/%m/%Y")
        if before.content == "":
            before_content = "**No text to display**"
        else:
            before_content = before.content
        embed = create_embed(f":screwdriver: {before.author} edited message ({before.id})", "", color="WARNING")
        embed.set_footer(text=f"Channel: {before.channel.name} | {today} - {time} CET | User ID: {before.author.id}")
        embed.add_field(name=f"**Old message:**", value=f"{before_content}", inline=False)
        embed.add_field(name=f"**New message:**", value=f"{after.content}", inline=False)
        await chat_log_channel.send(embed = embed)
    
print("Starting bot")
bot.run("OTg3MzE4NTkwMTkxNTgzMzAy.GmC2Kq.7bdFq5L1JZq-vUSd6EePT2m8F7pKR1AMhVSMY0")