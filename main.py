import asyncio
import os
from dotenv import load_dotenv
import aiohttp
import revolt
from revolt.ext import commands
import time

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
        # This command checks the bot's latency.
        before = time.monotonic()
        await ctx.send("🏓")
        mrm_list = await ctx.channel.history(limit=1)
        mrm = mrm_list[0]
        ping = (time.monotonic() - before) * 1000
        embeds = [revolt.SendableEmbed(title="🏓 Pong!", description=f"`\n{int(ping)} ms`", colour="#5d82d1")]
        await mrm.edit(content=None, embeds=embeds)
        print(f'Ping {int(ping)}ms')

    @commands.command()
    async def avatar(self, ctx: commands.Context, member: revolt.Member):
        # This command retrieves a user's avatar.
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
