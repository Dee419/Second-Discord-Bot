import discord
import json
from discord.ext import commands
from Embed import create_embed

class Admin_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Kick command
    @commands.command(help="Allows the user to kick a member")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, target: discord.Member=None, *args):
        if target == None:
            embed = create_embed(f":information_source: Kick info", f"Allows the user to kick a member.\nExample: `.kick 206398035654213633 Toxic Behaviour`", color="INFO")
            await ctx.reply(embed=embed)
        else:
            if len(args) > 0:
                for arg in args:
                    reason += arg + " "
                reason = reason[:-1]
            else:
                reason = "no reason given"
            embed = create_embed(f":white_check_mark: Kick successfull", f"{target.name}#{target.discriminator} has been kicked for {reason}!", time=True, color="SUCCESS")
            await ctx.reply(embed=embed)
            await target.kick(reason=reason)
            
            embed = create_embed(f":warning: You have been warned!", f"You have been warned on {ctx.guild.name} for {reason}!", color="ERROR")
            channel = await target.create_dm()
            await channel.send(embed=embed)

    # Ban command
    @commands.command(help="Allows the user to ban a user")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, target: discord.User=None, *args):
        if target == None:
            embed = create_embed(f":information_source: Ban info", f"Allows the user to ban a user. The user in question does not need to be on the server.\nExample: `.ban 206398035654213633 Hate Speech`", color="INFO")
            await ctx.reply(embed=embed)
        else:
            if len(args) > 0:
                for arg in args:
                    reason += arg + " "
                reason = reason[:-1]
            else:
                reason = "no reason given"
            embed = create_embed(f":white_check_mark: Ban successfull", f"{target.name}#{target.discriminator} has been banned for {reason}!", time=True, color="SUCCESS")
            await ctx.reply(embed=embed)
            await target.ban(reason=reason)

            embed = create_embed(f":warning: You have been warned!", f"You have been warned on {ctx.guild.name} for {reason}!", color="ERROR")
            channel = await target.create_dm()
            await channel.send(embed=embed)

    # Purge command
    @commands.command(help="Allows the user to purge a given amount of messages")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount, member: discord.Member=None):
        amount = int(amount)
        if amount < 1:
            embed = create_embed(f":x: Purge failed", f"Invalid amount given", color="ERROR")
            await ctx.reply(embed=embed)
        elif member == None:
            await ctx.channel.purge(limit=amount)
            embed = create_embed(f":white_check_mark: Purged successfully", f"Purged {amount} messages successfully!", color="SUCCESS")
            await ctx.send(embed=embed, delete_after=3)
        else:
            message_list = []
            async for message in ctx.channel.history():
                if message.author == member:
                    message_list.append(message)
            await ctx.channel.delete_messages(message_list)
            embed = create_embed(f":white_check_mark: Purged successfully", f"Purged {amount} messages of {member.name}#{member.discriminator} successfully!", color="SUCCESS")
            await ctx.send(embed=embed, delete_after=3)

    # Warn command
    @commands.command(help="Allows the user to warn a member")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, target: discord.Member=None, *args):
        embed = create_embed(":warning: THIS COMMAND IS STILL IN DEVELOPMENT", "While the command says the person in question has been warned **in reality nothing has been added yet to any sort of database**", color="WARNING")
        await ctx.send(embed=embed)
        if target == None:
            embed = create_embed(f":information_source: Warn info", f"Allows the user to warn a member.\nExample: `.warn 206398035654213633 Suggestive Image`", color="INFO")
            await ctx.reply(embed=embed)
        else:
            reason = ""
            if len(args) > 0:
                for arg in args:
                    reason += arg + " "
                reason = reason[:-1]
            else:
                reason = "no reason given"
            embed = create_embed(f":white_check_mark: Warned successfull", f"{target.name}#{target.discriminator} has been warned for {reason}!", time=True, color="SUCCESS")
            await ctx.reply(embed=embed)

            embed = create_embed(f":warning: You have been warned!", f"You have been warned on {ctx.guild.name} for {reason}!", color="WARNING")
            channel = await target.create_dm()
            await channel.send(embed=embed)

    # Set chat log channel command
    @commands.command(help="Allows the user to purge a given amount of messages")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setchatlogchannel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        with open('DataBase.json') as file:
            data = json.load(file)
        for server in data['servers']:
            if server['guild_id'] == ctx.guild.id:
                server['chat_log_channel_id'] = channel.id
                break
        with open('DataBase.json', 'w') as file:
            json.dump(data, file, indent=4)
        embed = create_embed(":white_check_mark: Successfully changed the chat log channel", f"Changed the chat log channel to {channel.mention}", color="SUCCESS")
        await ctx.reply(embed=embed)

    # Add server to database command
    @commands.command(help="Allows the user to add the server to the database in case the server is not currently in the database")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def addservertodatabase(self, ctx):
        with open('DataBase.json') as file:
            data = json.load(file)
        for server in data['servers']:
            # First check if the server is already in the database
            if server['guild_id'] == ctx.guild.id:
                embed = create_embed(":warning: Add server to database failed", "Server is already in the database", color="WARNING")
                await ctx.reply(embed=embed)
                return
        # If the server is not yet in the database we must add it to the database
        to_add = {
            "guild_id": ctx.guild.id,
            "chat_log_channel_id": 0,
            "welcome_channel": 0
        }
        data['servers'].append(to_add)
        with open('DataBase.json', 'w') as file:
            json.dump(data, file, indent=4)
        embed = create_embed(":white_check_mark: Successfully added the server to the database", f"Added this server to the database. Remember to use `.setchatlogchannel` to set the chat log channel", color="SUCCESS")
        await ctx.reply(embed=embed)
        
    # Error handlers
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: Kick failed", f"You don't have permission to kick members!", color="ERROR")
            await ctx.reply(embed=embed)
        if isinstance(error, commands.BotMissingPermissions):
            embed = create_embed(f":x: Kick failed", f"I don't have permission to kick members!", color="ERROR")
            await ctx.reply(embed=embed)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: Ban failed", f"You don't have permission to ban users!", color="ERROR")
            await ctx.reply(embed=embed)
        if isinstance(error, commands.BotMissingPermissions):
            embed = create_embed(f":x: Ban failed", f"I don't have permission to ban users!", color="ERROR")
            await ctx.reply(embed=embed)

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = create_embed(f":information_source: Purge info", f"Allows the user to purge a given amount of messages. You can also choose whose messages are to be purged.\nExample: `.purge 10 206398035654213633`", color="INFO")
            await ctx.reply(embed=embed)

    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: Warn failed", f"You don't have permission to warn members!", color="ERROR")
            await ctx.reply(embed=embed)
        
    @setchatlogchannel.error
    async def setchatlogchannel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: Set chat log channel failed", f"You don't have permission to change the chat log channel!", color="ERROR")
            await ctx.reply(embed=embed)

    @addservertodatabase.error
    async def addservertodatabase_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: Add server to database failed", f"You don't have permission to add the server to the database!", color="ERROR")
            await ctx.reply(embed=embed)