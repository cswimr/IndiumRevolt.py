import asyncio
import os
import time
import aiohttp
import dotenv
import revolt
from dotenv import load_dotenv
from revolt.ext import commands
from cogs.moderation import Moderation
from cogs.info import Info
from utils.embed import CustomEmbed

# This code reads the variables set in the bot's '.env' file.
env = dotenv.find_dotenv()
load_dotenv(env)
token = os.getenv('TOKEN')
api_url = os.getenv('API_URL')
prefix = os.getenv('PREFIX')
message_logging_channel = os.getenv('MESSAGE_LOGGING_CHANNEL')

class Client(commands.CommandsClient):
    """This class contains all of the commands/methods required for core functionality. Everything else will be relegated to cogs (eventually)."""
    async def get_prefix(self, message: revolt.Message, input: str | None = None): # pylint: disable=W0622
        if input is None:
            return prefix
        return input

    async def on_message_delete(self, message: revolt.Message):
        if isinstance(message.author, revolt.Member):
            if message.author.bot == True:
                return
            embed = [CustomEmbed(description=f"## Message Deleted in {message.channel.mention}\n**Author:** {message.author.name}#{message.author.discriminator} ({message.author.id})\n**Content:** {message.content}", colour="#5d82d1")]
            embed[0].set_footer(f"Message ID: {message.id}")
            try:
                try:
                    await self.get_channel(message_logging_channel).send(embeds=embed)
                except LookupError:
                    print("Message logging channel not found for server ID: " + message.server.id)
            except(revolt.errors.HTTPError):
                truncated_content = message.content[:1500] + "..."
                embed = [CustomEmbed(description=f"## Message Deleted in {message.channel.mention}\n**Author:** {message.author.name}#{message.author.discriminator} ({message.author.id})\n**Content:** {truncated_content}\n\n*Message content is over the character limit.*", colour="#5d82d1")]
                embed[0].set_footer(f"Message ID: {message.id}")
                try:
                    await self.get_channel(message_logging_channel).send(embeds=embed)
                except LookupError:
                    print("Message logging channel not found for server ID: " + message.server.id)
        else:
            print(f"{message.author.name}#{message.author.discriminator} ({message.author.id}): {message.content}\n ⤷ Deleted from Direct Messages\n   Message ID: {message.id}")

    async def on_message_update(self, message: revolt.Message):
        if isinstance(message.author, revolt.Member):
            print(f"{message.author.name}#{message.author.discriminator} ({message.author.id}): {message.content}\n ⤷ Sent from {message.server.name} ({message.server.id})")
        else:
            print(f"{message.author.name}#{message.author.discriminator} ({message.author.id}): {message.content}\n ⤷ Sent in Direct Messages")

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """This command checks the bot's latency."""
        before = time.monotonic()
        await ctx.message.reply("🏓")
        mrm_list = await ctx.channel.history(limit=1)
        mrm = mrm_list[0]
        ping = (time.monotonic() - before) * 1000
        embeds = [CustomEmbed(title="🏓 Pong!", description=f"`\n{int(ping)} ms`", colour="#5d82d1")]
        await mrm.edit(content=" ", embeds=embeds)
        print(f'Ping {int(ping)}ms')

    @commands.command()
    async def avatar(self, ctx: commands.Context, target: commands.UserConverter):
        """This command retrieves a user's avatar. -  NOTE: Move to cog"""
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
        """This command sets the bot's prefix. CURRENTLY BROKEN"""
        if new_prefix is not None and ctx.author.id == ctx.client.user.owner_id:
            await Client.prefix_change(self=self, message=ctx.message, new_prefix=new_prefix)
        else:
            await ctx.message.reply(f"The prefix is currently set to `{prefix}`.")

async def main():
    """This function logs into the bot user."""
    async with aiohttp.ClientSession() as session:
        client = Client(session, token, api_url=api_url)
        client.add_cog(Moderation(client))
        client.add_cog(Info(client))
        await client.start()

asyncio.run(main())
