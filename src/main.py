import discord
from discord.ext import commands
import traceback
import datetime
import os
from dotenv import load_dotenv

import config


def main():
    load_dotenv()

    try:
        ssb = SoSoBot(os.getenv("TOKEN"), config.prefix, config.description)
        ssb.start()
    except Exception:
        now = datetime.datetime.now()
        with open(
            f"crashes/{now.day}-{now.month}-{now.year} {now-hour}-{now.minute}-{now.second}.log",
            "w",
        ) as f:
            f.write(traceback.format_exc())


class SoSoBot:
    def __init__(self, token, prefix, description):
        self.token = token
        self.bot = commands.Bot(command_prefix=prefix, description=description)

    def start(self):
        self.bot.run(self.token)


if __name__ == "__main__":
    main()
