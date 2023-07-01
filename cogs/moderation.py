import os
import dotenv
import mysql.connector
import revolt
from pytimeparse2 import disable_dateutil, parse
from revolt import utils
from revolt.ext import commands
from utils.embed import CustomEmbed

# This code reads the variables set in the bot's '.env' file.
env = dotenv.find_dotenv()
dotenv.load_dotenv(env)
prefix = os.getenv('PREFIX')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db = os.getenv('DB')
required_role_id = os.getenv('REQUIRED_ROLE_ID')

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        disable_dateutil()

    def mysql_connect(self):
        connection = mysql.connector.connect(host=db_host,user=db_user,password=db_password,database=db)
        return connection

    def mysql_log(self, ctx: commands.Context, moderation_type, target_id, duration, reason):
        database = Moderation.mysql_connect(self)
        cursor = database.cursor()
        cursor.execute(f"SELECT moderation_id FROM `{ctx.server.id.lower()}_moderation` ORDER BY moderation_id DESC LIMIT 1")
        moderation_id = cursor.fetchone()[0] + 1
        sql = f"INSERT INTO `{ctx.server.id.lower()}_moderation` (moderation_id, moderation_type, target_id, duration, reason, resolved) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (moderation_id, moderation_type, target_id, duration, f"{reason}", 0)
        cursor.execute(sql, val)
        database.commit()
        database.close()
        print(f"MySQL Row Inserted!\n{moderation_id}, {moderation_type}, {target_id}, {duration}, {reason}, 0")

    @commands.command(name="timeout", aliases=["mute"])
    async def timeout(self, ctx: commands.Context, target: commands.MemberConverter, duration: str, *, reason: str):
        required_role = utils.get(ctx.server.roles, id=required_role_id)
        if required_role not in ctx.author.roles:
            await ctx.message.reply("You do not have permission to use this command!")
            return
        try:
            parsed_time = parse(sval=duration, as_timedelta=True, raise_exception=True)
        except ValueError:
            await ctx.message.reply(f"Please provide a valid duration!\nSee `{prefix}tdc`")
            return
        if not reason:
            await ctx.message.reply("Please provide a reason!")
            return
        await target.timeout(parsed_time)
        response = await ctx.message.reply(f"{target.mention} has been timed out for {str(parsed_time)}!\n**Reason** - `{reason}`")
        try:
            embeds = [CustomEmbed(title="Timed Out", description=f"You have been timed out for `{str(parsed_time)}` in {ctx.server.name}.\n### Reason\n`{reason}`", color="#5d82d1")]
            await target.send(embeds=embeds)
        except revolt.errors.HTTPError:
            await response.edit(content=f"{response.content}\n*Failed to send DM, user likely has the bot blocked.*")
        Moderation.mysql_log(self, ctx, moderation_type='Timeout', target_id=target.id, duration=parsed_time, reason=reason)

    @commands.command(name="untimeout", aliases=["unmute"])
    async def untimeout(self, ctx: commands.Context, target: commands.MemberConverter, *, reason: str):
        required_role = utils.get(ctx.server.roles, id=required_role_id)
        if required_role not in ctx.author.roles:
            await ctx.message.reply("You do not have permission to use this command!")
            return
        if not reason:
            await ctx.message.reply("Please include a reason!")
            return
        parsed_time = parse(sval="0s", as_timedelta=True, raise_exception=True)
        await target.timeout(parsed_time)
        response = await ctx.message.reply(f"{target.mention} has had their timeout removed!\n**Reason** - `{reason}`")
        try:
            embeds = [CustomEmbed(title="Timeout Removed", description=f"Your timeout has been removed in {ctx.server.name}.\n### Reason\n`{reason}`", color="#5d82d1")]
            await target.send(embeds=embeds)
        except revolt.errors.HTTPError:
            await response.edit(content=f"{response.content}\n*Failed to send DM, user likely has the bot blocked.*")
        Moderation.mysql_log(self, ctx, moderation_type='Untimeout', target_id=target.id, duration=parsed_time, reason=reason)

    @commands.command()
    async def warn(self, ctx: commands.Context, target: commands.MemberConverter, *, reason: str):
        required_role = utils.get(ctx.server.roles, id=required_role_id)
        if required_role not in ctx.author.roles:
            await ctx.message.reply("You do not have permission to use this command!")
            return
        if not reason:
            await ctx.message.reply("Please include a reason!")
            return
        response = await ctx.message.reply(f"{target.mention} has been warned!\n**Reason** - `{reason}`")
        try:
            embeds = [CustomEmbed(title="Warned", description=f"You have been warned in {ctx.server.name}!\n### Reason\n`{reason}`", color="#5d82d1")]
            await target.send(embeds=embeds)
        except revolt.errors.HTTPError:
            await response.edit(content=f"{response.content}\n*Failed to send DM, user likely has the bot blocked.*")
        Moderation.mysql_log(self, ctx, moderation_type='Warning', target_id=target.id, duration='NULL', reason=reason)

    @commands.command()
    async def kick(self, ctx: commands.Context, target: commands.MemberConverter, *, reason: str):
        required_role = utils.get(ctx.server.roles, id=required_role_id)
        if required_role not in ctx.author.roles:
            await ctx.message.reply("You do not have permission to use this command!")
            return
        if not reason:
            await ctx.message.reply("Please include a reason!")
            return
        try:
            await target.kick()
        except revolt.errors.HTTPError:
            await ctx.message.reply("User is not in the server!")
            return
        response = await ctx.message.reply(f"{target.mention} has been kicked!\n**Reason** - `{reason}`")
        try:
            embeds = [CustomEmbed(title="Warned", description=f"You have been kicked from {ctx.server.name}!\n### Reason\n`{reason}`", color="#5d82d1")]
            await target.send(embeds=embeds)
        except revolt.errors.HTTPError:
            await response.edit(content=f"{response.content}\n*Failed to send DM, user likely has the bot blocked.*")
        Moderation.mysql_log(self, ctx, moderation_type='Kick', target_id=target.id, duration='NULL', reason=reason)

    @commands.command()
    async def ban(self, ctx: commands.Context, target: commands.MemberConverter, *, reason: str):
        required_role = utils.get(ctx.server.roles, id=required_role_id)
        if required_role not in ctx.author.roles:
            await ctx.message.reply("You do not have permission to use this command!")
            return
        if not reason:
            await ctx.message.reply("Please include a reason!")
            return
        try:
            await target.ban(reason=reason)
            response = await ctx.message.reply(f"{target.mention} has been banned!\n**Reason** - `{reason}`")
            try:
                embeds = [CustomEmbed(title="Banned", description=f"You have been banned from `{ctx.server.name}`.\n### Reason\n`{reason}`", color="#5d82d1")]
                await target.send(embeds=embeds)
            except revolt.errors.HTTPError:
                await response.edit(content=f"{response.content}\n*Failed to send DM, user likely has the bot blocked.*")
            Moderation.mysql_log(self, ctx, moderation_type='Ban', target_id=target.id, duration='NULL', reason=reason)
        except revolt.errors.HTTPError:
            await ctx.message.reply(f"{target.mention} is already banned!")

    @commands.command()
    async def unban(self, ctx: commands.Context, target: commands.UserConverter, *, reason: str):
        required_role = utils.get(ctx.server.roles, id=required_role_id)
        if required_role not in ctx.author.roles:
            await ctx.message.reply("You do not have permission to use this command!")
            return
        if ctx.channel.channel_type is not revolt.ChannelType.text_channel:
            await ctx.message.reply("You cannot use moderation commands in direct messages!")
            return
        if not reason:
            await ctx.message.reply("Please include a reason!")
            return
        bans = await ctx.server.fetch_bans()
        for ban in bans:
            if ban.user_id == target.id:
                await ban.unban()
                response = await ctx.message.reply(f"{target.mention} has been unbanned!\n**Reason** - `{reason}`")
                try:
                    embeds = [CustomEmbed(title="Unbanned", description=f"You have been unbanned from `{ctx.server.name}`.\n### Reason\n`{reason}`", color="#5d82d1")]
                    await target.send(embeds=embeds)
                except revolt.errors.HTTPError:
                    await response.edit(content=f"{response.content}\n*Failed to send DM, user likely has the bot blocked.*")
                Moderation.mysql_log(self, ctx, moderation_type='Unban', target_id=target.id, duration='NULL', reason=str(reason))
                return
        await ctx.message.reply(f"{target.mention} is not banned!")


    @commands.command(aliases=["tdc"])
    async def timedeltaconvert(self, ctx, *, duration):
        required_role = utils.get(ctx.server.roles, id=required_role_id)
        if required_role not in ctx.author.roles:
            await ctx.message.reply("You do not have permission to use this command!")
            return
        if not duration:
            embeds = [CustomEmbed(description=f"## timedeltaconvert\nThis command converts a duration to a `timedelta` Python object.\n### Example Usage\n`{prefix}timedeltaconvert 1 day 15hr 82 minutes 52 s`\n### Output\n`1 day, 16:22:52`", color="#5d82d1")]
            await ctx.message.reply(embeds=embeds)
        else:
            try:
                parsed_time = parse(duration, as_timedelta=True, raise_exception=True)
                await ctx.message.reply(f"`{str(parsed_time)}`")
            except ValueError:
                await ctx.message.reply("Please provide a convertible value!")
