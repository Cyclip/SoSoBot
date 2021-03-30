import discord
from discord.ext import commands

from functions import translation


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CHAR_LIMIT = 100
        self.languages = translation.getLanguages()

    @commands.command(aliases=["t", "trans"], description="Text translation service")
    @commands.cooldown(2, 4)
    async def translate(self, ctx, toCode: str, *text):
        async with ctx.typing():
            text = ' '.join(text)
            if len(text) > self.CHAR_LIMIT:
                e = discord.Embed(
                    title=f"⛔ Text is too long ({len(text)}/{self.CHAR_LIMIT} chars)",
                    description=f"Shorten your input by {len(text)-self.CHAR_LIMIT} characters",
                    color=0xFF0000,
                )
                e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                return await ctx.send(embed=e)
            elif len(text) == 0:
                e = discord.Embed(
                    title="⛔ Missing text argument",
                    description="Add some text to translate",
                    color=0xFF0000,
                )
                e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                return await ctx.send(embed=e)

            currentLang = translation.identifyLanguage(text)
            targetLang = toCode

            translated = translation.translate(text, currentLang, targetLang)

            embed = discord.Embed(
                title=translated,
                color=0x2e9ce2,
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.avatar_url,
            )
            embed.set_footer(text=f"Translated {self.languages[currentLang]} to {self.languages[targetLang]}")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
