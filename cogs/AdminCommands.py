import discord
import json
import datetime
from discord.ext import commands
from Embed import create_embed

# Adds a moderation entry to the database
def add_to_moderation_db(ctx, target, reason, type):
    with open(f"./Database/{ctx.guild.id}/moderation.json") as file:
        moderation_data = json.load(file)

    time = (datetime.datetime.now()).strftime("%H:%M:%S")
    today = (datetime.date.today()).strftime("%d/%m/%Y")
    action_entry = {
        "reason": f"{reason}",
        "date": f"{today}",
        "time": f"{time}"
    }
    # Try to add to the user's punishments
    try:
        moderation_data[f"{target.id}"][f"{type}"].append(action_entry)
    except:
        try:
            # Try and add the type with the entry in there
            moderation_data[f"{target.id}"][f"{type}"] = [action_entry]
        except:
            # It could be that the user is not in the database yet
            try:
                user_entry = {
                    f"{type}": [
                        action_entry
                    ]
                }
                moderation_data[f"{target.id}"] = user_entry
            except:
                # All hope is lost
                return False
    with open(f"./Database/{ctx.guild.id}/moderation.json", 'w') as file:
        json.dump(moderation_data, file, indent=4)
    return True

# Returns an embed of all the punishments of a user depending on the type
def list_helper(ctx, target, type: str):
    if target is None:
        target = ctx.author
    with open(f"./Database/{ctx.guild.id}/moderation.json") as file:
        moderation_data = json.load(file)
    try:
        entries = moderation_data[f"{target.id}"][f"{type.upper()}"]
    except:
        entries = {}
    if len(entries) > 0:
        embed = create_embed(f"{type.capitalize()}s for {target.name}#{target.discriminator}", "")
        for entry in entries:
            embed.add_field(name=f"{type.capitalize()} for {target.name}#{target.discriminator}", value=f"\n**Reason**: {entry['reason']}\n**Date**: {entry['date']}\n**Time**: {entry['time']} CET\n", inline=False)
        return embed
    else:
        embed = create_embed(f"No {type}s found", f"No {type}s found for {target.name}#{target.discriminator}")
        return embed

# Returns an embed of all the punishments of a given type on a server
async def all_list_helper(ctx, type: str, bot):
    with open(f"./Database/{ctx.guild.id}/moderation.json") as file:
        moderation_data = json.load(file)
    try:
        member_entries = moderation_data
    except:
        member_entries = {}
    embed = create_embed(f"All {type}s on this server", "")
    found = False
    for member_entry in member_entries:
        try:
            entries = moderation_data[f"{member_entry}"][f"{type.upper()}"]
        except:
            entries = {}
        for entry in entries:
            target = await bot.fetch_user(int(member_entry))
            embed.add_field(name=f"{type.capitalize()} for {target.name}#{target.discriminator}", value=f"\n**Reason**: {entry['reason']}\n**Date**: {entry['date']}\n**Time**: {entry['time']} CET\n", inline=False)
            found = True
    if not found:
        embed = create_embed(f"No {type}s found on this server", f"No {type}s found on this server. Wow, good job!")
        return embed
    return embed

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = "Admin Commands"

    # Kick command
    @commands.command(help="Allows the user to kick a member")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, target: discord.Member=None, *args):
        if target == None:
            embed = create_embed(f":information_source: Kick info", f"Allows the user to kick a member.\nExample: `.kick 206398035654213633 Toxic Behaviour`", color="INFO")
            await ctx.reply(embed=embed)
        elif target == self.bot.user:
            raise commands.BadArgument
        else:
            if len(args) > 0:
                reason = ""
                for arg in args:
                    reason += arg + " "
                reason = reason[:-1]
            else:
                reason = "no reason given"
            if not add_to_moderation_db(ctx, target, reason, "KICK"):
                raise commands.CommandInvokeError("NotFoundInDatabase")
            await target.kick(reason=reason)
            embed = create_embed(f":white_check_mark: Kick successfull", f"{target.name}#{target.discriminator} has been kicked for {reason}!", time=True, color="SUCCESS")
            await ctx.reply(embed=embed)
            
            embed = create_embed(f":warning: You have been kicked!", f"You have been kicked from **{ctx.guild.name}** for {reason}!", color="ERROR")
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
        elif target == self.bot.user:
            raise commands.BadArgument
        else:
            if len(args) > 0:
                reason = ""
                for arg in args:
                    reason += arg + " "
                reason = reason[:-1]
            else:
                reason = "no reason given"
            if not add_to_moderation_db(ctx, target, reason, "BAN"):
                raise commands.CommandInvokeError("NotFoundInDatabase")
            try:
                await ctx.guild.ban(target, reason=reason)
            except:
                try:
                    await ctx.guild.ban(target.id, reason=reason)
                except:
                    raise commands.UserNotFound
            embed = create_embed(f":white_check_mark: Ban successfull", f"{target.name}#{target.discriminator} has been banned for {reason}!", time=True, color="SUCCESS")
            await ctx.reply(embed=embed)

            embed = create_embed(f":warning: You have been banned!", f"You have been banned from **{ctx.guild.name}** for {reason}!", color="ERROR")
            channel = await target.create_dm()
            try:
                await channel.send(embed=embed)
            except:
                return

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
            if not add_to_moderation_db(ctx, target, reason, "WARN"):
                raise commands.CommandInvokeError("NotFoundInDatabase")
            embed = create_embed(f":white_check_mark: Warned successfull", f"{target.name}#{target.discriminator} has been warned for {reason}!", time=True, color="SUCCESS")
            await ctx.reply(embed=embed)

            embed = create_embed(f":warning: You have been warned!", f"You have been warned on **{ctx.guild.name}** for {reason}!", color="WARNING")
            channel = await target.create_dm()
            await channel.send(embed=embed)

    # Set log channel command
    @commands.command(help="Allows the user to set the log channel. The log channel logs all deleted and edited messages and also logs members entering and leaving the server", aliases=['sclc', 'setclc'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setchatlogchannel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        with open(f"./Database/{ctx.guild.id}/general.json") as file:
            general_data = json.load(file)
        try:
            general_data['chat_log_channel_id'] = channel.id
        except:
            raise commands.CommandInvokeError("NotFoundInDatabase")
        with open(f"./Database/{ctx.guild.id}/general.json", 'w') as file:
            json.dump(general_data, file, indent=4)
        embed = create_embed(":white_check_mark: Successfully changed the chat log channel", f"Changed the chat log channel to {channel.mention}", color="SUCCESS")
        await ctx.reply(embed=embed)

    @commands.command(help="Lists all of the warns of a specific user", aliases=['listwarnings'])
    @commands.guild_only()
    async def listwarns(self, ctx, target=None):
        if target is not None and target != 'all':
            target = await self.bot.fetch_user(int(target))
            if target is None:
                raise commands.BadArgument
            embed = list_helper(ctx, target, "warn")
            await ctx.reply(embed=embed)
        elif target == 'all':
            if ctx.author.guild_permissions.administrator:
                embed = await all_list_helper(ctx, "warn", self.bot)
                await ctx.reply(embed=embed)
            else:
                raise commands.MissingPermissions
        else:
            embed = list_helper(ctx, ctx.author, "warn")
            await ctx.reply(embed=embed)
    
    @commands.command(help="Lists all of the kicks of a specific user")
    @commands.guild_only()
    async def listkicks(self, ctx, target=None):
        if target is not None and target != 'all':
            target = await self.bot.fetch_user(int(target))
            if target is None:
                raise commands.BadArgument
            embed = list_helper(ctx, target, "kick")
            await ctx.reply(embed=embed)
        elif target == 'all':
            if ctx.author.guild_permissions.administrator:
                embed = await all_list_helper(ctx, "kick", self.bot)
                await ctx.reply(embed=embed)
            else:
                raise commands.MissingPermissions
        else:
            embed = list_helper(ctx, ctx.author, "kick")
            await ctx.reply(embed=embed)

    @commands.command(help="Lists all of the bans of a specific user")
    @commands.guild_only()
    async def listbans(self, ctx, target=None):
        if target is not None and target != 'all':
            target = await self.bot.fetch_user(int(target))
            if target is None:
                raise commands.BadArgument
            embed = list_helper(ctx, target, "ban")
            await ctx.reply(embed=embed)
        elif target == 'all':
            if ctx.author.guild_permissions.administrator:
                embed = await all_list_helper(ctx, "ban", self.bot)
                await ctx.reply(embed=embed)
            else:
                raise commands.MissingPermissions
        else:
            embed = list_helper(ctx, ctx.author, "ban")
            await ctx.reply(embed=embed)

    # Error handlers
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: Kick failed", f"You don't have permission to kick members!", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = create_embed(f":x: Kick failed", f"I don't have permission to kick members!", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            embed = create_embed(f":x: Kick failed", f"Something went wrong, please contact my developer", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = create_embed(f":x: Kick failed", f"I can't kick myself. Just manually kick me if you really want me gone :(", color="ERROR")
            await ctx.reply(embed=embed)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: Ban failed", f"You don't have permission to ban users!", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = create_embed(f":x: Ban failed", f"I don't have permission to ban users!", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            embed = create_embed(f":x: Ban failed", f"Something went wrong, please contact my developer", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = create_embed(f":x: Ban failed", f"I can't ban myself. Just manually ban me if you really want me gone ;-;", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.MemberNotFound):
            embed = create_embed(f":x: Ban failed", f"I can't ban users who are not on the server", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.UserNotFound):
            embed = create_embed(f":x: Ban failed", f"The user given does not exist", color="ERROR")
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
        elif isinstance(error, commands.CommandInvokeError):
            embed = create_embed(f":x: Warn failed", f"Something went wrong, please contact my developer", color="ERROR")
            await ctx.reply(embed=embed)
        
    @setchatlogchannel.error
    async def setchatlogchannel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: Set chat log channel failed", f"You don't have permission to change the chat log channel!", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            embed = create_embed(f":x: List punishments failed", f"Something went wrong, please contact my developer", color="ERROR")
            await ctx.reply(embed=embed)

    @listwarns.error
    async def listwarns_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = create_embed(f":x: List punishments failed", f"Given target is not a valid member", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: List punishments failed", f"You do not have the permission to list all warns", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            embed = create_embed(f":x: List punishments failed", f"Something went wrong, please contact my developer", color="ERROR")
            await ctx.reply(embed=embed)

    @listkicks.error
    async def listkicks_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = create_embed(f":x: List punishments failed", f"Given target is not a valid member", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: List punishments failed", f"You do not have the permission to list all warns", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            embed = create_embed(f":x: List punishments failed", f"Something went wrong, please contact my developer", color="ERROR")
            await ctx.reply(embed=embed)

    @listbans.error
    async def listbans_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = create_embed(f":x: List punishments failed", f"Given target is not a valid member", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = create_embed(f":x: List punishments failed", f"You do not have the permission to list all warns", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            embed = create_embed(f":x: List punishments failed", f"Something went wrong, please contact my developer", color="ERROR")
            await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))