from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Check the bot's status")
    async def ping(self, ctx):
        await ctx.send("Pong")


def setup(bot):
    bot.add_cog(General(bot))
