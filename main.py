import asyncio
import os
from dotenv import load_dotenv
import aiohttp
import revolt
from revolt.ext import commands

load_dotenv()
token = os.getenv('TOKEN')
api_url = os.getenv('API_URL')

class Client(commands.CommandsClient):
    async def get_prefix(self, message: revolt.Message):
        return "."
    
    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("Pong!")

    @commands.command()
    async def avatar(self, ctx: commands.Context, member: revolt.Member):
        if not isinstance(member, revolt.Member):
            await ctx.send("Please provide a member argument!")
            return
        avatar = member.avatar.url
        await ctx.send(f"{avatar}")

async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, token, api_url=api_url)
        await client.start()

asyncio.run(main())