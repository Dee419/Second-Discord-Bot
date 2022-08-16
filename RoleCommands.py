import discord
import json
import asyncio
from discord.ext import commands
from discord.utils import get
from Embed import create_embed

# Adds a role reaction to the database
def add_to_rr_db(ctx, message, emoji, role):
    with open('DataBase.json') as file:
        data = json.load(file)
    if f"{ctx.guild.id}" not in data['servers']:
        # If the server is not yet in the database we return None so the bot can know
        return None

    rm_entry = {
        "emoji": emoji,
        "role_id": role.id
    }
    try:
        data['servers'][f"{ctx.guild.id}"]['role_messages'][f"{message.id}"]['role_id'] = role.id
        already = True
    except:
        data['servers'][f"{ctx.guild.id}"]['role_messages'][f"{message.id}"].append(rm_entry)
        already = False
    with open('DataBase.json', 'w') as file:
        json.dump(data, file, indent=4)
    if already:
        # If it was already in there we must return 1 so that the bot can send the message that it only changed the role
        return 1
    else:
        # If it wasn't already in there we must return 0 so that the bot can send the message that the command worked
        return 0

# Removes a role reaction from the database
def remove_from_rr_db(ctx, message, emoji):
    with open('DataBase.json') as file:
        data = json.load(file)
    if f"{ctx.guild.id}" not in data['servers']:
        # If the server is not yet in the database we return None so the bot can know
        return None
    
    role_message = data['servers'][f"{ctx.guild.id}"]['role_messages'][f"{message.id}"]
    if role_message is None or len(role_message) == 0:
        return
    # First we need to find the entry
    index = 0
    for role_reaction in role_message:
        if role_reaction['emoji'] == emoji:
            data['servers'][f"{ctx.guild.id}"]['role_messages'][f"{message.id}"].pop(index)
            with open('DataBase.json', 'w') as file:
                json.dump(data, file, indent=4)
            # We found it, so let's return True so that we can let the bot know
            return True
        index += 1
    # We didn't find it, we have to let the bot know so that it can raise an error
    return False

class Role_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Reaction add listener for role reactions
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        emoji = payload.emoji
        member = payload.member
        guild = self.bot.get_guild(payload.guild_id)
        with open('DataBase.json') as file:
            data = json.load(file)

        role_message = data['servers'][f"{guild.id}"]['role_messages'][f"{message.id}"]
        if role_message is None or len(role_message) == 0:
            return
        for role_reaction in role_message:
            if role_reaction['emoji'] == str(emoji) and not member.bot:
                role = guild.get_role(role_reaction['role_id'])
                await member.add_roles(role)
                embed = create_embed(f":white_check_mark: You have a new role!", f"You received the role named **{role.name}** on __{guild.name}__", color="SUCCESS")
                channel = await member.create_dm()
                await channel.send(embed=embed)
                return

    # Reaction remove listener for role reactions
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        emoji = payload.emoji
        guild = self.bot.get_guild(payload.guild_id)
        member = get(guild.members, id=payload.user_id)
        with open('DataBase.json') as file:
            data = json.load(file)
         
        role_message = data['servers'][f"{guild.id}"]['role_messages'][f"{message.id}"]
        if role_message is None or len(role_message) == 0:
            return
        for role_reaction in role_message:
            if role_reaction['emoji'] == str(emoji) and not member.bot:
                role = guild.get_role(role_reaction['role_id'])
                await member.remove_roles(role)
                embed = create_embed(f":white_check_mark: You have a new role!", f"You received the role named **{role.name}** on __{guild.name}__", color="SUCCESS")
                channel = await member.create_dm()
                await channel.send(embed=embed)
                return

    # Authors note:
    # Not sure why you wouldn't use the raw version over the normal one since you can get all the information from the payload anyways


    # Setup command for role reactions
    @commands.command(help="Starts the setup for a role reaction message. Start by providing the message id")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def rmsetup(self, ctx, role_message=None):
        if role_message is None:
            embed = create_embed(f":information_source: Role message setup info", f"Starts the setup for **adding** a role reaction message. Start by providing the message id\nExample: `.rmsetup {ctx.message.id}`", color="INFO")
            await ctx.reply(embed=embed)
            return
        # Since we do not know the channel in question we need to try each channel
        found = False
        for channel in ctx.guild.channels:
            try:
                role_message = await channel.fetch_message(role_message)
                found = True
                break
            except:
                pass
        if not found:
            raise commands.BadArgument

        await ctx.send("React with the emoji you would like to use")
        def first_check(reaction, user):
            return user == ctx.author 
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=first_check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond")
        else:
            emoji = reaction.emoji[0]
            print(f"{user.name}#{user.discriminator} reacted with {emoji}")

            await ctx.send('Please provide the id of the role')
            def check(message):
                return message.channel == ctx.channel and message.author == ctx.author
            try:
                user_input = await self.bot.wait_for('message', check=check)
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond")
            else:
                print(f"{user.name}#{user.discriminator} provided {user_input.content}")
                try:
                    role = ctx.guild.get_role(int(user_input.content))
                except:
                    raise commands.BadArgument
                else:
                    await role_message.add_reaction(emoji)
                    code = add_to_rr_db(ctx, role_message, emoji, role)
                    if code == 0:
                        embed = create_embed(f":information_source: Successfully added reaction role", f"Added reaction role to message {role_message.id} with emoji {emoji} for role {role.mention}", color="SUCCESS")
                        await ctx.reply(embed=embed)
                    elif code == 1:
                        embed = create_embed(f":warning: Changed role for reaction role", f"Reaction role for message {role_message.id} with emoji {emoji} already existed. Changed role to {role.mention}", color="WARNING")
                        await ctx.reply(embed=embed)
                    else:
                        raise commands.CommandInvokeError

    # Removal command for role reactions
    @commands.command(help="Starts the removal of a role reaction message. Start by providing the message id")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def rmremove(self, ctx, role_message=None):
        if role_message is None:
            embed = create_embed(f":information_source: Role message remove info", f"Starts the **removal** a role reaction message. Start by providing the message id\nExample: `.rmremove {ctx.message.id}`", color="INFO")
            await ctx.reply(embed=embed)
            return
        # Since we do not know the channel in question we need to try each channel
        found = False
        for channel in ctx.guild.channels:
            try:
                role_message = await channel.fetch_message(role_message)
                found = True
                break
            except:
                pass
        if not found:
            raise commands.BadArgument
        
        await ctx.send("Give the ordinal position of the emoji. In other words; how far in the line is the emoji?\nExample: `3` in case the emoji is the third in the list of reactions")
        def check(message):
            return message.channel == ctx.channel and message.author == ctx.author
        try:
            user_input = await self.bot.wait_for('message', check=check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond")
        else:
            user_input = int(user_input.content) - 1
            emoji = role_message.reactions[user_input].emoji
            await ctx.send(f"You chose {emoji}")
            print(f"{ctx.author.name}#{ctx.author.discriminator} provided {user_input}")
            if user_input < 0 or user_input > len(role_message.reactions):
                raise commands.BadArgument
            elif remove_from_rr_db(ctx, role_message, emoji):
                embed = create_embed(f":information_source: Successfully removed reaction role", f"Removed reaction role to message {role_message.id} with emoji {emoji}", color="SUCCESS")
                await ctx.reply(embed=embed)
            else:
                raise commands.CommandInvokeError

    # Error handlers
    @rmsetup.error
    async def rmsetup_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = create_embed(f":x: Role message setup failed", f"Given input is invalid", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            embed = create_embed(f":x: Role message setup failed", f"Server not found in database, please use `.addservertodatabase`", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: Role message setup failed", f"You don't have permission to use this command!", color="ERROR")
            await ctx.reply(embed=embed)

    @rmsetup.error
    async def rmsetup_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = create_embed(f":x: Role message remove failed", f"Given input is invalid", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            embed = create_embed(f":x: Role message remove failed", f"Server not found in database, please use `.addservertodatabase`", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: Role message remove failed", f"You don't have permission to use this command!", color="ERROR")
            await ctx.reply(embed=embed)