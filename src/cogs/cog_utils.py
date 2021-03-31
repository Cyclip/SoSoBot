import discord
from discord.ext import commands

from functions import translation


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CHAR_LIMIT = 100
        self.languages = translation.getLanguages()

    @commands.command(aliases=["lang", "langs"], description="View all language codes")
    async def languages(self, ctx):
        """
        Usage: `s!languages`
        """
        e = discord.Embed(
            title="All language codes",
            description="Please use the short versions when translating text.",
            color=0x4C9038,
        )

        e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        replacements = {
            "cs": "cz",
            "cnr": "me",
            "el": "gr",
            "fa": "ir",
            "fr-CA": "fr",
            "da": "dk",
            "en": "gb",
            "eo": "pl",
            "bn": "bd",
        }

        for code, lang in self.languages.items():
            if code in replacements.keys():
                countryCode = replacements[code]
            else:
                countryCode = code
            e.add_field(
                name=f":flag_{countryCode}: {lang}",
                value=f"Code: **{code}**",
                inline=True,
            )

        await ctx.send(embed=e)

    @commands.command(aliases=["t", "trans"], description="Text translation service")
    @commands.cooldown(2, 4)
    async def translate(self, ctx, toCode: str, *text):
        """
        Usage: `s!translate <to language> <text>`
        Example: `s!translate fr hello!`
        Example: `s!translate fr-de bonjour!`
        """
        async with ctx.typing():
            text = " ".join(text)
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

            if "-" in toCode:
                currentLang, targetLang = toCode.split("-")
            else:
                currentLang = translation.identifyLanguage(text)
                targetLang = toCode

            try:
                translated = translation.translate(text, currentLang, targetLang)
            except Exception:
                e = discord.Embed(
                    title="⛔ Failed to translate",
                    description=f"The model {toCode} may not be correct"
                    if "-" in toCode
                    else "The translation service may not be working.",
                    color=0xFF0000,
                )
                e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                return await ctx.send(embed=e)

            embed = discord.Embed(
                title=translated,
                color=0x2E9CE2,
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.avatar_url,
            )
            embed.set_footer(
                text=f"Translated {self.languages[currentLang]} to {self.languages[targetLang]}"
            )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
