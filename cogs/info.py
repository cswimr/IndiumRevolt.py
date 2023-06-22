import revolt
from revolt.ext import commands
from utils.embed import CustomEmbed

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
