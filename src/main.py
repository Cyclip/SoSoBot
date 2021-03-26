import discord
from discord.ext import commands
import traceback
import datetime
import os
from dotenv import load_dotenv

import config


def main():
    global ssb
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


class SoSoBot:
    def __init__(self, token, prefix, description):
        self.token = token
        self.bot = commands.Bot(
            command_prefix=prefix, description=description, case_insensitive=True
        )
        self.loadedCogs = []

        self.loadCogs()

    @commands.command()
    async def test(ctx):
        ctx.send("ee")

    def loadCogs(self, ignoreAdmin=False):
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
        for cogName in self.loadedCogs:
            if ignoreAdmin:
                if cogName == "cog_admin.py":
                    continue
            cog = self.bot.get_cog(cogName)
            self.bot.unload_extension(cog)

        self.loadedCogs = []

    def start(self):
        self.bot.run(self.token)


if __name__ == "__main__":
    main()
