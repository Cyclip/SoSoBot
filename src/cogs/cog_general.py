from discord import Embed
from discord.ext import commands

from functions import imageHandler


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activeImgs = dict()
        self.reactions = ["⏪", "◀️", "❌", "▶️", "⏩"]

    @commands.command(description="Check the bot's status")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        if latency >= 200:
            color = 0xDF2F2F
        elif latency >= 100:
            color = 0xF17A18
        elif latency >= 50:
            color = 0xE2F41E
        else:
            color = 0x88EB1C
        embed = Embed(
            title="Pong!",
            description=f"{latency}ms latency",
            color=color,
        )
        await ctx.channel.send(embed=embed)

    def genEmbed(self, data, index, total, query):
        """
        Generate an image embed
        """
        title = f"Search results for '{query}'"
        e = Embed(
            title=title,
            description=f"[{data['title']}]({data['websiteUrl']})",
            color=0x2689E4,
        )
        e.set_image(url=data["url"])
        e.set_footer(text=f"Result {index+1}/{total}")
        return e

    @commands.command(aliases=["im"], description="Search for an image")
    @commands.cooldown(2, 4, commands.BucketType.user)
    async def image(self, ctx, *args):
        """
        .im (inspired by NotSoBot)
        Search for an image via DuckDuckGo
        """
        async with ctx.typing():
            query = " ".join(args[:])
            originalUser = ctx.message.author
            nsfwChannel = ctx.channel.is_nsfw()
            links, next = imageHandler.getImageLinks(query, nsfw=nsfwChannel)

            imgIndex = 0
            embed = self.genEmbed(links[imgIndex], imgIndex, len(links), query)
        msg = await ctx.send(embed=embed)

        self.activeImgs[originalUser] = {
            "links": links,
            "imgIndex": imgIndex,
            "msg": msg,
            "query": query,
        }

        for emoji in self.reactions:
            await msg.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        When someone reacts to a message, check if they
        are reacting to an active image and that the
        appropriate user is adding a reaction. From
        that, modify the message accordingly.
        """
        if user in self.activeImgs.keys():
            img = self.activeImgs[user]
            if reaction.message == img["msg"]:
                emoji = str(reaction.emoji)
                await reaction.remove(user)

                if emoji == self.reactions[0]:
                    img["imgIndex"] -= 5
                elif emoji == self.reactions[1]:
                    img["imgIndex"] -= 1
                elif emoji == self.reactions[2]:
                    del self.activeImgs[user]
                    return await img["msg"].delete()
                elif emoji == self.reactions[3]:
                    img["imgIndex"] += 1
                elif emoji == self.reactions[4]:
                    img["imgIndex"] += 5

                if img["imgIndex"] > len(img["links"]):
                    img["imgIndex"] = len(img["links"])
                elif img["imgIndex"] < 0:
                    img["imgIndex"] = 0

                print(img["imgIndex"], len(img["links"]))

                embed = self.genEmbed(
                    img["links"][img["imgIndex"]],
                    img["imgIndex"],
                    len(img["links"]),
                    img["query"],
                )
                await img["msg"].edit(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
