from discord import Embed, File
from discord.ext import commands
import traceback
import time
import typing

from functions import retrieval


class General(commands.Cog):
    """General commands (including search commands)"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")
        self.activeImgs = dict()
        self.activeSubreddits = dict()
        self.reactions = ["⏪", "◀️", "❌", "▶️", "⏩"]
        self.inviteLink = "https://discord.com/api/oauth2/authorize?client_id=825450074116194345&permissions=2080500848&scope=bot"

    def getCommandInfo(self):
        """
        Format:
        [
            {
                "name": cogName,
                "commands": [
                    "name": commandName,
                    "description": commandDescription,
                    "aliases": aliases
                ],
                "description": description
            }
        ]
        """
        cogInfo = []
        for cog in self.bot.cogs:
            commands = [
                {
                    "name": command.name,
                    "description": command.description,
                    "aliases": command.aliases,
                }
                for command in self.bot.get_cog(cog).get_commands()
            ]
            cogInfo.append(
                {
                    "name": cog,
                    "commands": commands,
                    "description": cog.__doc__,
                }
            )
        return cogInfo

    @commands.command(name="help", description="View the help menu")
    async def _help(self, ctx, module: typing.Optional[str] = ""):
        cogInfo = self.getCommandInfo()

        if module is "":
            # Show all cogs
            embed = Embed(
                title="SoSoBot help menu",
                description="Developed by [Cyclip](http://github.com/cyclip)",
                color=0x490606,
            )

            for cog in cogInfo:
                embed.add_field(
                    name=f"{cog['name']} ({len(cog['commands'])} commands)",
                    value=f"`s!help {cog['name']}` for help",
                    inline=True,
                )

        else:
            if module.lower() in [i["name"].lower() for i in cogInfo]:
                pass

        file = File("resources/SSB.png", filename="SSB.png")
        embed.set_author(
            name="SoSoBot",
            icon_url="attachment://SSB.png",
        )
        await ctx.send(embed=embed, file=file)

    @commands.command(aliases=["subreddit", "red"], description="Search a subreddit")
    @commands.cooldown(4, 7, commands.BucketType.user)
    async def reddit(
        self,
        ctx,
        srName: str,
        sorting: typing.Optional[str] = "hot",
    ):
        """
        Search for reddit posts
        """
        async with ctx.typing():
            nsfw = ctx.channel.is_nsfw()
            subreddit = retrieval.getSubreddit(srName)

            if not nsfw and subreddit.over18:
                e = Embed(
                    title=f"⛔ Subreddit {srName} cannot be used in non-NSFW channels",
                    color=0xFF0000,
                )
                e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                return await ctx.send(embed=e)

            posts = retrieval.getPosts(subreddit, sorting, nsfw)

            self.activeSubreddits[ctx.author.id] = {
                "posts": posts,
                "ctx": ctx,
                "index": 0,
                "sorting": sorting,
            }

            embed = self.getRedditEmbed(ctx.author)

        msg = await ctx.send(embed=embed)
        self.activeSubreddits[ctx.author.id]["msg"] = msg

        for emoji in self.reactions:
            await msg.add_reaction(emoji)

    def getRedditEmbed(self, author):
        """
        Generate a Reddit embed
        """
        s = self.activeSubreddits[author.id]
        post = s["posts"][s["index"]]

        embed = Embed(
            title=post["title"],
            color=0x2689E4,
        )

        if post["isText"]:
            embed.add_field(name=post["content"][:255], value="\u200b", inline=True)
        else:
            embed.set_image(url=post["content"])

        embed.set_footer(
            text=f"""{post['score']} 👍   |   {post['comments']} 💬
Sorting r/{post['subredditName']} by {s['sorting']}"""
        )

        embed.set_author(
            name=s["ctx"].author.name,
            icon_url=s["ctx"].author.avatar_url,
        )

        return embed

    @commands.command()
    async def test(self, ctx):
        pass

    @commands.command(
        aliases=["inv", "getinv", "invite"], description="Get the bot's invite link"
    )
    # @commands.cooldown(1, 10, commands.BucketType.user)
    async def getInvite(self, ctx):
        """
        Send the invite link for the bot
        """
        e = Embed(
            title="Add SoSoBot to your own server:",
            description=f"[Click here to invite!]({self.inviteLink})",
            color=0x2BE7A9,
        )

        e.add_field(
            name="Note: you must have the 'Manage server' permission.",
            value="The invite link will not expire",
            inline=True,
        )

        file = File("resources/SSB.png", filename="SSB.png")
        e.set_author(
            name="SoSoBot",
            icon_url="attachment://SSB.png",
        )
        await ctx.send(embed=e, file=file)

    @commands.command(description="Check the bot's status")
    @commands.cooldown(5, 10, commands.BucketType.user)
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
        file = File("resources/SSB.png", filename="SSB.png")
        embed.set_author(
            name="SoSoBot",
            icon_url="attachment://SSB.png",
        )

        await ctx.channel.send(embed=embed, file=file)

    def genEmbed(self, data, index, total, query):
        """
        Generate an image embed
        """
        title = f"Search results for '{query}'"
        e = Embed(
            title=title,
            color=0x2689E4,
        )
        e.set_image(url=data["url"])
        e.set_footer(
            text=f"[{data['title']}]({data['websiteUrl']})\nResult {index+1}/{total}"
        )
        return e

    @commands.command(aliases=["im", "img"], description="Search for an image")
    @commands.cooldown(2, 4, commands.BucketType.user)
    async def image(self, ctx, *args):
        """
        .im (inspired by NotSoBot)
        Search for an image via DuckDuckGo
        """
        try:
            async with ctx.typing():
                query = " ".join(args[:])
                if len(query) > 100:
                    e = Embed(
                        title=f"⛔ Query is too long ({len(query)}/100 chars)",
                        description=f"Shorten your query by {len(query)-100} characters",
                        color=0xFF0000,
                    )
                    e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                    return await ctx.send(embed=e)
                originalUser = ctx.message.author
                nsfwChannel = ctx.channel.is_nsfw()
                start = time.time()
                links = retrieval.getImageLinks(query, nsfw=nsfwChannel)
                tt = time.time() - start
                print(f"{query} took {round(tt, 3)}s")

                imgIndex = 0
                embed = self.genEmbed(links[imgIndex], imgIndex, len(links), query)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            msg = await ctx.send(embed=embed)
        except Exception as err:
            e = Embed(
                title="⛔ Failed to retrieve images",
                description="There was an unexpected error while using the API.",
                color=0xFF0000,
            )
            e.set_footer(text=str(err))
            print(traceback.format_exc())
            return await ctx.send(embed=e)

        self.activeImgs[originalUser] = {
            "links": links,
            "imgIndex": imgIndex,
            "msg": msg,
            "query": query,
            "ctx": ctx,
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

                embed = self.genEmbed(
                    img["links"][img["imgIndex"]],
                    img["imgIndex"],
                    len(img["links"]),
                    img["query"],
                )
                embed.set_author(
                    name=img["ctx"].author.name,
                    icon_url=img["ctx"].author.avatar_url,
                )
                await img["msg"].edit(embed=embed)

        elif user.id in self.activeSubreddits.keys():
            s = self.activeSubreddits[user.id]
            if reaction.message == s["msg"]:
                emoji = str(reaction.emoji)
                await reaction.remove(user)

                if emoji == self.reactions[0]:
                    s["index"] -= 5
                elif emoji == self.reactions[1]:
                    s["index"] -= 1
                elif emoji == self.reactions[2]:
                    del self.activeSubreddits[user.id]
                    return await s["msg"].delete()
                elif emoji == self.reactions[3]:
                    s["index"] += 1
                elif emoji == self.reactions[4]:
                    s["index"] += 5

                if s["index"] > len(s["posts"]):
                    s["index"] = len(s["posts"])
                elif s["index"] < 0:
                    s["index"] = 0

                embed = self.getRedditEmbed(s["ctx"].author)
                await s["msg"].edit(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
