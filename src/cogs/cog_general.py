import discord
from discord.ext import commands
import traceback
import time
import typing

import json
import os

from functions import retrieval
import config


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
                    {
                        "name": commandName,
                        "description": commandDescription,
                        "aliases": aliases
                    }
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
                    "help": command.help,
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
        """
        Usage: `s!help`
        """
        cogInfo = self.getCommandInfo()

        if module == "":
            # Show all cogs
            embed = discord.Embed(
                title="SoSoBot help menu",
                description="Type `s!help <module>` to list commands for that module.\nType `s!help <commands>` to show command usage.",
                color=config.uniColour,
            )

            for cog in cogInfo:
                embed.add_field(
                    name=f"{cog['name']} ({len(cog['commands'])} commands)",
                    value=f"`s!help {cog['name']}` for help",
                    inline=True,
                )

        else:
            moduleNames = [
                i["name"].lower() for i in cogInfo if i["name"].lower() != "admin"
            ]
            found = False
            for i, n in enumerate(moduleNames):
                if module.lower() == moduleNames[i]:
                    embed = discord.Embed(
                        title=f"{module} commands".capitalize(),
                        description="Type `s!help <command>` to show command usage",
                        color=config.uniColour,
                    )
                    cog = cogInfo[i]
                    if len(cog["commands"]) > 0:
                        for cmd in cog["commands"]:
                            description = f"{'No description' if (cmd['description'] is None or cmd['description'] == '') else cmd['description']}"
                            val = (
                                cmd["help"]
                                if not (cmd["help"] is None or cmd["help"] == "")
                                else "No usage description"
                            )
                            if len(cmd["aliases"]) > 0:
                                displayAliases = [f"`{i}`" for i in cmd["aliases"]]
                                try:
                                    val += f"\nAliases: {', '.join(displayAliases)}"
                                except Exception:
                                    pass
                            embed.add_field(
                                name=cmd["name"],
                                value=val,
                            )
                    else:
                        embed.add_field(
                            name=f"{module} has no commands".capitalize(),
                            value="Some commands may be hidden.",
                        )
                    found = True
                    break

            if not found:
                commands, names = self.getCommands(cogInfo)
                try:
                    index = names.index(module.lower())
                    selected = commands[index]

                    embed = discord.Embed(
                        title=f"Help for {selected['name']}",
                        color=config.uniColour,
                    )

                    value2 = (
                        f"Aliases: {', '.join(selected['aliases'])}"
                        if len(selected["aliases"]) > 0
                        else "\u200b"
                    )

                    embed.add_field(
                        name=selected["description"], value="\u200b", inline=False
                    )
                    embed.add_field(name=selected["help"], value=value2, inline=False)
                except IndexError:
                    embed.add_field(
                        name=f"{module} does not exist".capitalize(),
                        value="Some commands may be hidden.",
                    )

        # embed.add_field(name="\u200B", value="\u200B")
        embed.add_field(
            value=f"Developed by [Cyclip](https://github.com/Cyclip/)",
            name="\u200B",
            inline=False,
        )

        file = discord.File("resources/SSB.png", filename="SSB.png")
        embed.set_thumbnail(url="attachment://SSB.png")
        await ctx.send(embed=embed, file=file)

    def getCommands(self, cogInfo):
        """
        Get all command info.
        Output example:
        [
            {
                "name": "commandName",
                "description": "commandDescription",
                "aliases": "aliases",
                "help": "help"
            },
            {
                "name": "commandName2",
                "description": "commandDescription2",
                "aliases": "aliases2",
                "help": "help2"
            },
            {
                "name": "commandName3",
                "description": "commandDescription3",
                "aliases": "aliases3",
                "help": "help3"
            }
        ]
        """
        commands = []
        names = []

        for cog in cogInfo:
            listCmds = cog["commands"]
            for cmd in listCmds:
                commands += [cmd]
                names.append(cmd["name"].lower())

        return commands, names

    @commands.command(aliases=["subreddit", "red"], description="Search a subreddit")
    @commands.cooldown(4, 7, commands.BucketType.user)
    async def reddit(
        self,
        ctx,
        srName: str,
        sorting: typing.Optional[str] = "hot",
    ):
        """
        Usage: `s!reddit <subreddit> [sorting]`
        Example: `s!reddit all hot`
        """

        srName = srName.replace("r/", "")
        async with ctx.typing():
            try:
                nsfw = ctx.channel.is_nsfw()
                try:
                    subreddit = retrieval.getSubreddit(srName)
                except Exception:
                    e = discord.Embed(
                        title=f"⛔ Subreddit {srName} cannot be found",
                        color=0xFF0000,
                    )
                    e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                    return await ctx.send(embed=e)

                if not nsfw and subreddit.over18:
                    e = discord.Embed(
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

                try:
                    embed = self.getRedditdiscord.Embed(ctx.author)
                except IndexError:
                    e = discord.Embed(
                        title=f"⛔ r/{srName} does not contain any posts",
                        color=0xFF0000,
                    )
                    e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                    return await ctx.send(embed=e)
            except Exception as err:
                e = discord.Embed(
                    title=f"⛔ Unexpected error while handling r/{srName}",
                    description=str(err),
                    color=0xFF0000,
                )
                e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                return await ctx.send(embed=e)

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

        embed = discord.Embed(
            title=post["title"],
            color=config.uniColour,
        )

        if post["isText"]:
            embed.add_field(name=post["content"][:255], value="\u200b", inline=True)
        else:
            embed.set_image(url=post["content"])

        embed.set_footer(
            text=f"""👍 {post['score']}
💬 {post['comments']}
Sorting r/{post['subredditName']} by {s['sorting']}"""
        )

        embed.set_author(
            name=s["ctx"].author.name,
            icon_url=s["ctx"].author.avatar_url,
        )

        return embed

    @commands.command(
        aliases=["inv", "getinv", "invite"], description="Get the bot's invite link"
    )
    # @commands.cooldown(1, 10, commands.BucketType.user)
    async def getInvite(self, ctx):
        """
        Usage: `s!getInvite`
        """
        e = discord.Embed(
            title="Add SoSoBot to your own server:",
            description=f"[Click here to invite!]({self.inviteLink})",
            color=config.uniColour,
        )

        e.add_field(
            name="Note: you must have the 'Manage server' permission.",
            value="The invite link will not expire",
            inline=True,
        )

        file = discord.File("resources/SSB.png", filename="SSB.png")
        e.set_author(
            name="SoSoBot",
            icon_url="attachment://SSB.png",
        )
        await ctx.send(embed=e, file=file)

    @commands.command(description="Check the bot's status")
    @commands.cooldown(5, 10, commands.BucketType.user)
    async def ping(self, ctx):
        """
        Usage: `s!ping`
        """
        latency = round(self.bot.latency * 1000)
        if latency >= 200:
            color = 0xDF2F2F
        elif latency >= 100:
            color = 0xF17A18
        elif latency >= 50:
            color = 0xE2F41E
        else:
            color = 0x88EB1C
        embed = discord.Embed(
            title="Pong!",
            description=f"{latency}ms latency",
            color=color,
        )
        file = discord.File("resources/SSB.png", filename="SSB.png")
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
        e = discord.Embed(
            title=title,
            color=config.uniColour,
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
        Usage: `s!image <query>`
        """
        try:
            async with ctx.typing():
                query = " ".join(args[:])
                if len(query) > 100:
                    e = discord.Embed(
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
                embed = self.gendiscord.Embed(
                    links[imgIndex], imgIndex, len(links), query
                )
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            msg = await ctx.send(embed=embed)
        except Exception as err:
            e = discord.Embed(
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

                embed = self.gendiscord.Embed(
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

                embed = self.getRedditdiscord.Embed(s["ctx"].author)
                await s["msg"].edit(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
