import time
import asyncio
import os
import aiohttp
import revolt
from revolt.ext import commands
import dotenv
from dotenv import load_dotenv

env = dotenv.find_dotenv()
load_dotenv(env)
token = os.getenv('TOKEN')
api_url = os.getenv('API_URL')
prefix = os.getenv('PREFIX')

class Client(commands.CommandsClient):
    # This class contains all of the commands the bot uses.
    async def get_prefix(self, message: revolt.Message, input: str = prefix):
        return input

    @commands.command()
    async def ping(self, ctx: commands.Context):
        # This command checks the bot's latency.
        before = time.monotonic()
        await ctx.message.reply("🏓")
        mrm_list = await ctx.channel.history(limit=1)
        mrm = mrm_list[0]
        ping = (time.monotonic() - before) * 1000
        embeds = [revolt.SendableEmbed(title="🏓 Pong!", description=f"`\n{int(ping)} ms`", colour="#5d82d1")]
        await mrm.edit(content=" ", embeds=embeds)
        print(f'Ping {int(ping)}ms')

    @commands.command()
    async def avatar(self, ctx: commands.Context, target: revolt.User):
        # This command retrieves a user's avatar. CURRENTLY BROKEN
        if not isinstance(target, revolt.User):
            await ctx.send("Please provide a user argument!")
            return
        avatar = target.avatar.url
        await ctx.send(f"{avatar}")

    @commands.command()
    @commands.is_bot_owner()
    async def prefix(self, ctx: commands.Context, new_prefix: str = None):
        # This command sets the bot's prefix. CURRENTLY BROKEN
        if 'PREFIX' not in os.environ:
            await ctx.send("Something is very wrong! You have managed to run a prefix command without having a prefix set in your `.env` file!")
            print("ERROR: prefix_env_var check failed!")
            return
        if new_prefix is not None:
            dotenv.set_key(env, 'PREFIX', new_prefix)
            await ctx.send(f"Prefix has been changed from `{prefix}` to `{new_prefix}`!")
            print(f"Prefix changed: {prefix} → {new_prefix}")
            await Client.get_prefix(ctx.message, new_prefix)
        else:
            await ctx.send(f"The prefix is currently set to `{prefix}`.")

async def main():
    # This function logs into the bot user.
    async with aiohttp.ClientSession() as session:
        client = Client(session, token, api_url=api_url)
        await client.start()

asyncio.run(main())
