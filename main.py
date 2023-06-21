import time
import asyncio
import os
import aiohttp
import revolt
from revolt.ext import commands
import dotenv
from dotenv import load_dotenv
from moderation import Moderation

# This code reads the variables set in the bot's '.env' file.
env = dotenv.find_dotenv()
load_dotenv(env)
token = os.getenv('TOKEN')
api_url = os.getenv('API_URL')
prefix = os.getenv('PREFIX')

class Client(commands.CommandsClient):
    # This class contains all of the commands/methods required for core functionality. Everything else will be relegated to cogs (eventually).
    async def get_prefix(self, message: revolt.Message, input: str | None = None): # pylint: disable=W0622
        if input is None:
            return prefix
        return input

    # async def on_message(self, message: revolt.Message):
    #     if 'PREFIX' not in os.environ or prefix is None:
    #         if message.author == self.user.owner:
    #             await message.channel.send("You have started the bot without setting the `prefix` environment variable!\nIt has been set to `temp!` automatically, please change it using `temp!prefix <new prefix>`.")
    #             print("ERROR: prefix_env_var check failed! Prefix set to 'temp!'.")
    #             new_prefix = "temp!"
    #             await Client.prefix_change(self=self, message=message, new_prefix=new_prefix, silent=True)
    #         else:
    #             print("ERROR: prefix_env_var check failed!")
    #     else:
    #         if isinstance(message.author, revolt.Member):
    #             print(f"{message.author.name}#{message.author.discriminator} ({message.author.id}): {message.content}\n ⤷ Sent from {message.server.name} ({message.server.id})")
    #         else:
    #             print(f"{message.author.name}#{message.author.discriminator} ({message.author.id}): {message.content}\n ⤷ Sent in Direct Messages")
    #     await Client.process_commands(self, message)

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
        # This command retrieves a user's avatar. CURRENTLY BROKEN - NOTE: Move to cog
        if not isinstance(target, revolt.User):
            await ctx.message.reply("Please provide a user argument!")
            return
        avatar = target.avatar.url
        await ctx.message.reply(f"{avatar}")

    async def prefix_change(self, message: revolt.Message, new_prefix: str, silent: bool | None = False):
        dotenv.set_key(env, 'PREFIX', new_prefix)
        if silent is not True:
            await message.reply(f"Prefix has been changed from `{prefix}` to `{new_prefix}`!")
        print(f"Prefix changed: {prefix} → {new_prefix}")
        await Client.get_prefix(message, new_prefix)

    @commands.command()
    async def prefix(self, ctx: commands.Context, new_prefix: str = None):
        # This command sets the bot's prefix. CURRENTLY BROKEN
        if new_prefix is not None and ctx.author.id == ctx.client.user.owner_id:
            await Client.prefix_change(self=self, message=ctx.message, new_prefix=new_prefix)
        else:
            await ctx.message.reply(f"The prefix is currently set to `{prefix}`.")

    @commands.command()
    async def temptimeout(self, ctx: commands.Context):
        target = Client.get_server(self, "01G9FHH3F20QHBERQ6FT3RT5Y2").get_member("01H37XQF4WMV6HRGYTA03YMSDZ")
        duration = Moderation.parse_timedelta(self, "1 minute")
        await target.timeout(duration)

async def main():
    # This function logs into the bot user.
    async with aiohttp.ClientSession() as session:
        client = Client(session, token, api_url=api_url)
        client.add_cog(Moderation(client))
        await client.start()

asyncio.run(main())
