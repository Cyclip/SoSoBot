import discord
from discord.ext import commands
import traceback
import datetime
import os
from dotenv import load_dotenv
import asyncio

import config
import decorators


class SoSoBot:
    """
    Main class for SoSoBot
    Usage:
        SoSoBot(str token, str prefix, str description)
    """

    def __init__(self, token, prefix, description):
        self.token = token
        self.bot = commands.Bot(
            command_prefix=prefix, description=description, case_insensitive=True
        )
        self.loadedCogs = []  # For loading and unloading cogs

        self.loadCogs()
        self.addCommands()
        self.addEvents()

    def addCommands(self):
        """
        Internal commands in the main class
        """

        @commands.check(decorators.owner_required)
        @self.bot.command(pass_context=True)
        async def reload(ctx):
            self.unloadCogs()
            self.loadCogs()
            await ctx.send("Reloaded cogs!")

    def addEvents(self):
        """
        All events are handled here
        """

        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandOnCooldown):
                # Cooldown error
                embed = discord.Embed(
                    title=f"You need to wait {round(error.retry_after, 1)}s before using this command again",
                    description=f"Calm down <@{ctx.message.author.id}>",
                    color=0xFF0000,
                )
                await ctx.send(embed=embed, delete_after=10)
                asyncio.sleep(config.cooldownCooldown)
            raise error  # So errors show up in console

    def loadCogs(self, ignoreAdmin=False):
        """
        Load all cogs in ./cogs which start with "cog_"
        """
        for cog in os.listdir("cogs"):
            if cog.endswith(".py") and cog.startswith("cog_"):
                if (ignoreAdmin and cog != "cog_admin.py") or not ignoreAdmin:
                    try:
                        cog = f"cogs.{cog.replace('.py', '')}"
                        self.bot.load_extension(cog)
                        self.loadedCogs.append(cog)
                        print(f"Loaded {cog}")
                    except Exception:
                        print(f"{cog} failed to load")
                        print(traceback.format_exc())

    def unloadCogs(self, ignoreAdmin=False):
        """
        Unload all cogs in self.loadedCogs
        """
        for cogName in self.loadedCogs:
            if ignoreAdmin:
                if cogName == "cog_admin.py":
                    continue
            # cog = self.bot.get_cog(cogName)
            self.bot.unload_extension(cogName)
            print(f"Unloaded {cogName}")

        self.loadedCogs = []

    def start(self):
        self.bot.run(self.token)


if __name__ == "__main__":
    load_dotenv()

    try:
        ssb = SoSoBot(os.getenv("TOKEN"), config.prefix, config.description)
        ssb.start()
    except Exception:
        now = datetime.datetime.now()
        with open(
            f"crashes/{now.day}-{now.month}-{now.year} {now.hour}-{now.minute}-{now.second}.log",
            "w",
        ) as f:
            err = traceback.format_exc()
            f.write(err)
            print(err)
