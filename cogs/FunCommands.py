import asyncio
import json
import requests
from Embed import create_embed
from discord.ext import commands
from random import randint

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = "Fun Commands"

    @commands.command(help="Allows the user to play Rock Paper Scissors against the bot")
    async def rps(self, ctx):
        moves = ['🪨', '🧻', '✂️']
        bot_move = moves[randint(0, 2)]
        message = await ctx.send(f"Choose your weapon of choice..")
        for emoji in moves:
            await message.add_reaction(emoji)
        def check(reaction, user):
            return user.id == ctx.author.id and \
            str(reaction.emoji) in ['🪨', '🧻', '✂️']

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f"You took too long to respond :(")
        else:
            if ctx.guild != None:
                bot_member = ctx.guild.get_member(self.bot.user.id)
            else:
                bot_member = None
            if bot_member != None:
                await message.remove_reaction(emoji='🪨', member=bot_member)
                await message.remove_reaction(emoji='🧻', member=bot_member)
                await message.remove_reaction(emoji='✂️', member=bot_member)
            await message.edit(content = "Rock")
            await asyncio.sleep(0.35)
            await message.edit(content = "Rock, paper")
            await asyncio.sleep(0.35)
            await message.edit(content = "Rock, paper, scissors!")
            await asyncio.sleep(0.35)
            if reaction.emoji == '🪨':
                if bot_move == '🪨': # Player chooses rock, ai chooses rock -> T
                    await message.edit(content = f"We both chose {reaction.emoji}.\nIt's a tie!")
                elif bot_move == '🧻': # Player chooses rock, ai chooses paper -> A
                    await message.edit(content = f"You chose {reaction.emoji} and I chose {bot_move}. Paper beats rock.\nI win, {ctx.author.mention}!")
                else: # Player chooses rock, ai chooses scissors -> P
                    await message.edit(content = f"You chose {reaction.emoji} and I chose {bot_move}. Rock beats scissors\nYou win, {ctx.author.mention}!")
            elif reaction.emoji == '🧻':
                if bot_move == '🪨': # Player chooses paper, ai chooses rock -> P
                    await message.edit(content = f"You chose {reaction.emoji} and I chose {bot_move}. Paper beats rock.\nYou win, {ctx.author.mention}!")
                elif bot_move == '🧻': # Player chooses paper, ai chooses paper -> T
                    await message.edit(content = f"We both chose {reaction.emoji}.\nIt's a tie, {ctx.author.mention}!")
                else: # Player chooses paper, ai chooses scissors -> A
                    await message.edit(content = f"You chose {reaction.emoji} and I chose {bot_move}. Scissors beats paper\nI win, {ctx.author.mention}!")
            else:
                if bot_move == '🪨': # Player chooses scissors, ai chooses rock -> A
                    await message.edit(content = f"You chose {reaction.emoji} and I chose {bot_move}. Rock beats scissors.\nI win, {ctx.author.mention}!")
                elif bot_move == '🧻': # Player chooses scissors, ai chooses paper -> P
                    await message.edit(content = f"You chose {reaction.emoji} and I chose {bot_move}. Scissors beats paper\nYou win, {ctx.author.mention}!")
                else: # Player chooses scissors, ai chooses scissors -> T
                    await message.edit(content = f"We both chose {reaction.emoji}.\nIt's a tie, {ctx.author.mention}!")

    @commands.command(help="Allows the user to get a random cat image")
    async def cat(self, ctx):
        cat_url = 'http://aws.random.cat/meow'
        image_url = json.loads(requests.get(cat_url).content)["file"]
        embed = create_embed("Cat", "", color="INFO", url=image_url)
        embed.set_image(url=image_url)
        await ctx.reply(embed=embed)
    
    @commands.command(help="Every single person is my enemy~")
    async def misery(self, ctx):
        oh_the_misery = "https://tenor.com/view/oh-the-misery-oh-the-misery-everybody-wants-to-be-my-enemy-gif-25368312"
        everybody_wants_to_be_my_enemy = "https://tenor.com/view/everybody-wants-to-be-my-gif-25137901"
        spare_the_sympathy = "https://tenor.com/view/spare-spare-the-sympathy-the-sympathy-wawa-cat-gif-25825252"
        message = await ctx.reply(oh_the_misery)
        await asyncio.sleep(2.6)
        await message.edit(content=everybody_wants_to_be_my_enemy)
        await asyncio.sleep(3.1)
        await message.edit(content=spare_the_sympathy)
        await asyncio.sleep(2.4)
        await message.edit(content=everybody_wants_to_be_my_enemy)
        await asyncio.sleep(3.4)
        await message.edit(content=":cat:")

    @commands.command(help="Pets CatBot :)")
    async def pet(self, ctx):
        chance = randint(0, 4)
        match chance:
            case 0:
                await ctx.reply("Purr :cat:")
            case 1:
                await ctx.reply("Purrr :cat:")
            case 2:
                await ctx.reply("Purrrr :cat:")
            case 4:
                await ctx.reply("Purrrrr :cat:")

async def setup(bot):
    await bot.add_cog(FunCommands(bot))