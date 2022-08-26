import discord
from discord.ext import commands

class TestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = "Test Commands"
    
    @commands.command()
    async def test(self, ctx):
        await ctx.reply("Hello, world!")

    class CheckMenu(discord.ui.View):
        def __init__(self, ctx, *, timeout: float = 30.0):
            super().__init__(timeout=timeout)
            self.ctx = ctx
    
        @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
        async def button_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id == self.ctx.author.id:
                await interaction.response.send_message("It's true!")
                self.stop()

        @discord.ui.button(label='No', style=discord.ButtonStyle.red)
        async def button_no(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id == self.ctx.author.id:
                await interaction.response.send_message("It's not true")
                self.stop()

    @commands.command()
    async def check(self, ctx):
        view = self.CheckMenu(ctx=ctx)
        await ctx.send("Yes or no?", view=view)

async def setup(bot):
    await bot.add_cog(TestCommands(bot))