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
app_url = os.getenv('APP_URL')

class Client(commands.CommandsClient):
    """This class contains all of the commands/methods required for core functionality. Everything else will be relegated to cogs (eventually)."""
    async def get_prefix(self, message: revolt.Message, input: str | None = None): # pylint: disable=W0622
        if input is None:
            return prefix
        return input

    async def on_server_join(self, server: revolt.Server):
        print(f"Joined server: {server.name} ({server.id})")
        Moderation.create_server_table(self, server.id)

    async def on_message_delete(self, message: revolt.Message):
        if isinstance(message.author, revolt.Member):
            if message.author.bot is True:
                return
            truncated_content = message.content[:1500] + "..."
            embed = [CustomEmbed(description=f"## Message Deleted in {message.channel.mention}\n**Author:** {message.author.name}#{message.author.discriminator} ({message.author.id})\n**Content:** {message.content}", colour="#5d82d1"), CustomEmbed(description=f"## Message Deleted in {message.channel.mention}\n**Author:** {message.author.name}#{message.author.discriminator} ({message.author.id})\n**Content:** {truncated_content}\n\n*Message content is over the character limit.*", colour="#5d82d1")]
            embed[0].set_footer(f"Message ID: {message.id}")
            embed[1].set_footer(f"Message ID: {message.id}")
            channel = self.get_channel(message_logging_channel)
            try:
                try:
                    await channel.send(embed=embed[0])
                except LookupError:
                    print("Message logging channel not found for server ID: " + message.server.id)
            except(revolt.errors.HTTPError):
                try:
                    await channel.send(embed=embed[1])
                except LookupError:
                    print("Message logging channel not found for server ID: " + message.server.id)
        else:
            print(f"{message.author.name}#{message.author.discriminator} ({message.author.id}): {message.content}\n ⤷ Deleted from Direct Messages\n   Message ID: {message.id}")

    async def on_message_update(self, before: revolt.Message, message: revolt.Message):
        if isinstance(message.author, revolt.Member):
            if message.author.bot is True:
                return
            message_link = f"{app_url}/server/{message.server.id}/channel/{message.channel.id}/message/{message.id}"
            embeds = [CustomEmbed(description=f"## Message Edited in {message.channel.mention}\n**Author:** {message.author.name}#{message.author.discriminator} ({message.author.id})\n**Message ID:** [{message.id}]({message_link})", colour="#5d82d1"), CustomEmbed(title="Old Content", description=before.content, colour="#5d82d1"), CustomEmbed(title="New Content", description=message.content, colour="#5d82d1")]
            channel = self.get_channel(message_logging_channel)
            try:
                await channel.send(embed=embeds[0])
                await channel.send(embed=embeds[1])
                await channel.send(embed=embeds[2])
            except LookupError:
                print("Message logging channel not found for server ID: " + message.server.id)
        else:
            print(f"{message.author.name}#{message.author.discriminator} ({message.author.id}): {before.content}\n ⤷ Edited in Direct Messages\n   New Content: {message.content}")

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """This command checks the bot's latency."""
        before = time.monotonic()
        msg = await ctx.message.reply("🏓")
        ping = (time.monotonic() - before) * 1000
        embeds = [CustomEmbed(title="🏓 Pong!", description=f"`\n{int(ping)} ms`", colour="#5d82d1")]
        await msg.edit(content=" ", embeds=embeds)
        print(f'Ping {int(ping)}ms')

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
