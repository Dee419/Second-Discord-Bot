import discord
import os
import asyncio
import json
import datetime
from discord.ext import commands
from Embed import create_embed

print("Loading intents")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
print("Initializing bot")
bot = commands.Bot(command_prefix='.', intents=intents, case_insensitive=True)
non_cached_messages = []

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    print("Bot started!")
    with open('DataBase.json') as file:
        data = json.load(file)
    for guild in bot.guilds:
        print(f"Checking bans for {guild.name}")
        if str(guild.id) in data['servers']:
            added_bans = 0
            async for entry in guild.bans():
                if str(entry.user.id) in data['servers'][f"{guild.id}"]['moderation']:
                    # The user is on the server and has been punished before (according to the database), let's check if all of their bans are on the database
                    try:
                        for db_entry in data['servers'][f"{guild.id}"]['moderation'][f"{entry.user.id}"]['BAN']:
                            if entry.reason == db_entry['reason']:
                                found = True
                                break
                    except:
                        found = False
                    if not found:
                        time = (datetime.datetime.now()).strftime("%H:%M:%S")
                        today = (datetime.date.today()).strftime("%d/%m/%Y")
                        id = data['last_id'] + 1
                        data['last_id'] = id
                        action_entry = {
                            "id": id,
                            "reason": f"{entry.reason}",
                            "date": f"{today}",
                            "time": f"{time}"
                        }
                        try:
                            data['servers'][f"{guild.id}"]['moderation'][f"{entry.user.id}"]['BAN'].append(action_entry)
                            added_bans += 1
                        except:
                            # This should never fail, but we'll try it anyways just to be sure
                            try:
                                data['servers'][f"{guild.id}"]['moderation'][f"{entry.user.id}"]['BAN'] = [action_entry]
                                added_bans += 1
                            except:
                                print(f"Failed to add ban for {entry.user.name}#{entry.user.discriminator}")
                else:
                    found = False
                    # The user is on the server and has been punished before but they're not in the database
                    time = (datetime.datetime.now()).strftime("%H:%M:%S")
                    today = (datetime.date.today()).strftime("%d/%m/%Y")
                    # print(f"TIME: {time}\nDATE: {today}")
                    id = data['last_id'] + 1
                    data['last_id'] = id
                    action_entry = {
                        "id": id,
                        "reason": f"{entry.reason}",
                        "date": f"{today}",
                        "time": f"{time}"
                    }
                    # Try to add to the user's punishments
                    user_entry = {
                        f"{'BAN'}": [
                            action_entry
                        ]
                    }
                    try:
                        # This should never fail, but we'll try it anyways just to be sure
                        data['servers'][f"{guild.id}"]['moderation'][f"{entry.user.id}"] = user_entry
                        added_bans += 1
                    except:
                        print(f"Failed to add ban for {entry.user.name}#{entry.user.discriminator}")
            if not found:
                with open('DataBase.json', 'w') as file:
                    json.dump(data, file, indent=4)
            if added_bans > 0:
                print(f"Added {added_bans} missing bans for {guild.name}")
            else:
                print(f"There we no missing bans on {guild.name}")

@bot.event
async def on_member_ban(guild, user):
    time = datetime.datetime.now()
    today = datetime.date.today()
    found = False
    with open('DataBase.json') as file:
        data = json.load(file)
    try:
        ban_entries = data['servers'][f"{guild.id}"]['moderation'][f"{user.id}"]['BAN']
    except:
        ban_entries = []
    for entry in ban_entries:
        if entry['date'] == today and (time - datetime.timedelta(seconds=5) < entry['time']):
            found = True
            break
    if not found:
        id = data['last_id'] + 1
        data['last_id'] = id
        time = time.strftime("%H:%M:%S")
        today = today.strftime("%d/%m/%Y")
        action_entry = {
            "id": id,
            "reason": f"No reason found",
            "date": f"{today}",
            "time": f"{time}"
        }
        # Try to add to the user's punishments
        try:
            data['servers'][f"{guild.id}"]['moderation'][f"{user.id}"]['BAN'].append(action_entry)
        except:
            try:
                # Try and add the type with the entry in there
                data['servers'][f"{guild.id}"]['moderation'][f"{user.id}"]['BAN'] = [action_entry]
            except:
                # It could be that the user is not in the database yet
                user_entry = {
                    'BAN': [
                        action_entry
                    ]
                }
                data['servers'][f"{guild.id}"]['moderation'][f"{user.id}"] = user_entry
        with open('DataBase.json', 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Added a ban for {entry.user.name}#{entry.user.discriminator} to the database")

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
            f"{guild.id}": {
                "chat_log_channel_id": 0,
                "welcome_channel_id": 0,
                "moderation": {
                    
                },
                "role_messages": {
                    
                }
            }
        }
    data['servers'].append(to_add)
    with open('DataBase.json', 'w') as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_raw_message_delete(payload):
    message = payload.cached_message
    guild_id = payload.guild_id
    chat_log_channel_id = None
    with open('DataBase.json') as file:
        data = json.load(file)
    try:
        chat_log_channel_id = data['servers'][f"{guild_id}"]['chat_log_channel_id']
    except:
        pass
    if message is not None and chat_log_channel_id is not None and chat_log_channel_id != 0:
        # Ignore messages where the content stays the same or the author is a bot
        if message.author.bot:
            return
        # We have the message in our cache and we have the chat log channel
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
    elif chat_log_channel_id is not None and chat_log_channel_id != 0:
        # We don't have the message in our cache but we do have the chat log channel
        chat_log_channel = bot.get_channel(chat_log_channel_id)
        
        time = (datetime.datetime.now()).strftime("%H:%M:%S")
        today = (datetime.date.today()).strftime("%d/%m/%Y")
        embed = create_embed(f":wastebasket: Message ({payload.message_id}) was deleted", f"*Content could not be retrieved*", f"Channel: {bot.get_channel(payload.channel_id).name} | {today} - {time} CET | This message was not saved in my cache", color="ERROR")
        await chat_log_channel.send(embed = embed)

@bot.event
async def on_raw_message_edit(payload):
    with open('DataBase.json') as file:
        data = json.load(file)
    message = payload.cached_message
    guild_id = payload.guild_id
    chat_log_channel_id = data['servers'][f"{guild_id}"]['chat_log_channel_id']
    if message is None:
        # We will try and retrieve the message from non_cached_messages
        for non_cached_message in non_cached_messages:
            if non_cached_message.id == payload.message_id:
                message = non_cached_message
    if message is not None and chat_log_channel_id is not None and chat_log_channel_id != 0:
        # We have the message in our cache and we have the chat log channel
        chat_log_channel = bot.get_channel(chat_log_channel_id)
        
        time = (datetime.datetime.now()).strftime("%H:%M:%S")
        today = (datetime.date.today()).strftime("%d/%m/%Y")
        before = message
        after = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        # Ignore messages where the content stays the same or the author is a bot
        if before.content == after.content or before.author.bot:
            return
        if before.content == "":
            before_content = "**No text to display**"
        else:
            before_content = before.content
        embed = create_embed(f":screwdriver: {before.author} edited message ({before.id})", "", color="WARNING")
        embed.set_footer(text=f"Channel: {before.channel.name} | {today} - {time} CET | User ID: {before.author.id}")
        embed.add_field(name=f"**Old message:**", value=f"{before_content}", inline=False)
        embed.add_field(name=f"**New message:**", value=f"{after.content}", inline=False)
        await chat_log_channel.send(embed = embed)
    elif chat_log_channel_id is not None and chat_log_channel_id != 0:
        # We don't have the message in our cache but we do have the chat log channel
        chat_log_channel = bot.get_channel(chat_log_channel_id)

        time = (datetime.datetime.now()).strftime("%H:%M:%S")
        today = (datetime.date.today()).strftime("%d/%m/%Y")
        after = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        before_content = "*Content could not be retrieved*"
        embed = create_embed(f":screwdriver: {after.author} edited message ({after.id})", "", color="WARNING")
        embed.set_footer(text=f"Channel: {after.channel.name} | {today} - {time} CET | User ID: {after.author.id} | This message was not saved in my cache")
        embed.add_field(name=f"**Old message:**", value=f"{before_content}", inline=False)
        embed.add_field(name=f"**New message:**", value=f"{after.content}", inline=False)
        non_cached_messages.append(after)
        await chat_log_channel.send(embed = embed)

@bot.event
async def on_member_join(member):
    with open('DataBase.json') as file:
        data = json.load(file)
    chat_log_channel_id = data['servers'][f"{member.guild.id}"]['chat_log_channel_id']
    if chat_log_channel_id is not None and chat_log_channel_id != 0:
        # We have the chat log channel
        chat_log_channel = bot.get_channel(chat_log_channel_id)
        time = (datetime.datetime.now()).strftime("%H:%M:%S")
        today = (datetime.date.today()).strftime("%d/%m/%Y")
        embed = create_embed(f"{member.name}#{member.discriminator} has joined the server", f"{member.name}#{member.discriminator} ({member.id}) has joined the server", f"{today} - {time} CET", color="SUCCESS")
        await chat_log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    with open('DataBase.json') as file:
        data = json.load(file)
    chat_log_channel_id = data['servers'][f"{member.guild.id}"]['chat_log_channel_id']
    if chat_log_channel_id is not None and chat_log_channel_id != 0:
        # We have the chat log channel
        chat_log_channel = bot.get_channel(chat_log_channel_id)
        time = (datetime.datetime.now()).strftime("%H:%M:%S")
        today = (datetime.date.today()).strftime("%d/%m/%Y")
        embed = create_embed(f"{member.name}#{member.discriminator} has left the server", f"{member.name}#{member.discriminator} ({member.id}) has left the server", f"{today} - {time} CET", color="ERROR")
        await chat_log_channel.send(embed=embed)

print("Loading token")
with open('token.txt') as file:
    token = file.readline()

print("Starting main()")
async def main():
    async with bot:
        print("Loading extensions")
        await load_extensions()
        print("Starting bot")
        await bot.start(token)
asyncio.run(main())