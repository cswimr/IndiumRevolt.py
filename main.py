# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring
import asyncio
import os
from dotenv import load_dotenv
import aiohttp
import revolt
from revolt.ext import commands

load_dotenv()
token = os.getenv('TOKEN')
api_url = os.getenv('API_URL')
prefix = os.getenv('PREFIX')

class Client(commands.CommandsClient):
    # This class contains all of the commands the bot uses.
    async def get_prefix(self, message: revolt.Message):
        return prefix

    @commands.command()
    async def ping(self, ctx: commands.Context):
        # Checks if the bot is running.
        await ctx.send("Pong!")

    @commands.command()
    async def avatar(self, ctx: commands.Context, member: revolt.Member):
        # Checks a user's avatar.
        if not isinstance(member, revolt.Member):
            await ctx.send("Please provide a member argument!")
            return
        avatar = member.avatar.url
        await ctx.send(f"{avatar}")

async def main():
    # This function logs into the bot user.
    async with aiohttp.ClientSession() as session:
        client = Client(session, token, api_url=api_url)
        await client.start()

asyncio.run(main())
