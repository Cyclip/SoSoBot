import config
from discord.ext import commands


def owner_required(ctx):
    if ctx.message.author.id in config.owners:
        return True
    else:
        return False
