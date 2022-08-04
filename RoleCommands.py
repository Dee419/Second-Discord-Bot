import discord
import json
import asyncio
from discord.ext import commands
from Embed import create_embed

def add_to_rm_db(ctx, message, emoji, role):
    with open('DataBase.json') as file:
        data = json.load(file)

    rm_entry = {
        "message_id": message.id,
        "emoji": emoji,
        "role_id": role.id
    }
    # First go through all the servers
    exists = False
    index = 0
    for server in data['servers']:
        if server['guild_id'] == ctx.guild.id:
            exists = True
            already = False
            # Once we found the server we have to check if there is already a reaction message with the same emoji id
            for role_message in server['role_messages']:
                if role_message['message_id'] == message.id and role_message['emoji'] == emoji:
                    # If so we'll just change the role id to the new role
                    role_message['role_id'] = role.id
                    already = True
                    break
            # If we haven't found a reaction message with the same emoji we'll just add the rm_entry to the server in the database
            if not already:
                data['servers'][index]['role_messages'].append(rm_entry)
            # Then we dump it into the json like usual
            with open('DataBase.json', 'w') as file:
                json.dump(data, file, indent=4)
            if already:
                # If it was already in there we must return False so that the bot can send the message that it only changed the role
                return 1
            else:
                # If it wasn't already in there we must return True so that the bot can send the message that the command worked
                return 0
        else:
            index += 1
    # If the server doesn't exist we must raise an exception
    if not exists:
        return None

class Role_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Starts the setup for a role reaction message")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def rmsetup(self, ctx, role_message: discord.Message=None):
        if role_message == None:
            raise commands.BadArgument
        else:
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
                    print(message.content)
                    print(message.channel, ctx.channel, message.author, ctx.author)
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
                        code = add_to_rm_db(ctx, role_message, emoji, role)
                        if code == 0:
                            embed = create_embed(f":information_source: Successfully added reaction role", f"Added reaction role to message {role_message.id} with emoji {emoji} for role {role.mention}", color="SUCCESS")
                            await ctx.reply(embed=embed)
                        elif code == 1:
                            embed = create_embed(f":warning: Changed role for reaction role", f"Reaction role for message {role_message.id} with emoji {emoji} already existed. Changed role to {role.mention}", color="WARNING")
                            await ctx.reply(embed=embed)
                        else:
                            raise commands.CommandInvokeError

    @rmsetup.error
    async def rmsetup_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = create_embed(f":x: Role message setup failed", f"Given input is invalid", color="ERROR")
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            embed = create_embed(f":x: Add role message to database failed", f"Server not found in database, please use `.addservertodatabase`", color="ERROR")
            await ctx.reply(embed=embed)