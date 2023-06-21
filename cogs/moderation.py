import os
import dotenv
import mysql.connector
import revolt
from dotenv import load_dotenv
from pytimeparse2 import disable_dateutil, parse
from revolt.ext import commands

# This code reads the variables set in the bot's '.env' file.
env = dotenv.find_dotenv()
load_dotenv(env)
prefix = os.getenv('PREFIX')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db = os.getenv('DB')

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        disable_dateutil()

    def mysql_log(self, type, target_id, duration, reason):
        moddb = mysql.connector.connect(host=db_host,user=db_user,password=db_password,database=db)
        cursor = moddb.cursor()
        cursor.execute("SELECT moderation_id FROM `mod` ORDER BY moderation_id DESC LIMIT 1")
        moderation_id = cursor.fetchone()[0] + 1
        sql = "INSERT INTO `mod` (moderation_id, moderation_type, target_id, duration, reason, resolved) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (moderation_id, type, target_id, duration, reason, 0)
        cursor.execute(sql, val)
        moddb.commit()
        moddb.close()
        print(f"MySQL Row Inserted!\n{moderation_id}, {type}, {target_id}, {duration}, {reason}, 0")

    @commands.command(name="timeout", aliases=["mute"])
    async def timeout(self, ctx: commands.Context, target: commands.MemberConverter, duration: str, *, reason: str):
        try:
            parsed_time = parse(sval=duration, as_timedelta=True, raise_exception=True)
        except ValueError:
            await ctx.message.reply(f"Please provide a valid duration!\nSee `{prefix}tdc`")
            return
        # await target.timeout(parsed_time)
        await ctx.message.reply(f"{target.mention} has been timed out for {str(parsed_time)}!\n**Reason** - `{reason}`")
        embeds = [revolt.SendableEmbed(title="Timed Out", description=f"You have been timed out for {str(parsed_time)}.\n### Reason\n`{reason}", colour="#5d82d1")]
        # await target.send(embeds=embeds)
        Moderation.mysql_log(self, type='Timeout', target_id=target.id, duration=parsed_time, reason=reason)

    @commands.command()
    async def warn(self, ctx: commands.Context, target: commands.MemberConverter, *, reason: str):
        if not reason:
            await ctx.message.reply("Please include a reason!")
            return
        await ctx.message.reply(f"{target.mention} has been warned!\n**Reason** - `{reason}`")
        embeds = [revolt.SendableEmbed(title="Warned", description=f"You have been warned.\n### Reason\n`{reason}", colour="#5d82d1")]
        # await target.send(embeds=embeds)
        Moderation.mysql_log(self, type='Warning', target_id=target.id, duration='NULL', reason=reason)

    @commands.command()
    async def ban(self, ctx: commands.Context, target: commands.MemberConverter, *, reason: str):
        if not reason:
            await ctx.message.reply("Please include a reason!")
            return
        try:
            embeds = [revolt.SendableEmbed(title="Banned", description=f"You have been banned.\n### Reason\n`{reason}", colour="#5d82d1")]
            # await target.send(embeds=embeds)
            await target.ban(reason=reason)
            await ctx.message.reply(f"{target.mention} has been banned!\n**Reason** - `{reason}`")
            Moderation.mysql_log(self, type='Ban', target_id=target.id, duration='NULL', reason=reason)
        except revolt.errors.HTTPError:
            await ctx.message.reply(f"{target.mention} is already banned!")

    @commands.command()
    async def unban(self, ctx: commands.Context, target: commands.MemberConverter):
        try:
            await target.unban()
            embeds = [revolt.SendableEmbed(title="Unbanned", description=f"You have been unbanned.", colour="#5d82d1")]
            # await target.send(embeds=embeds)
            await ctx.message.reply(f"{target.mention} has been unbanned!")
            Moderation.mysql_log(self, type='Unban', target_id=target.id, duration='NULL', reason=f'Unbanned through {prefix}unban')
        except revolt.errors.HTTPError:
            await ctx.message.reply(f"{target.mention} is not banned!")
            return


    @commands.command(aliases=["tdc"])
    async def timedeltaconvert(self, ctx, *, duration):
        if not duration:
            embeds = [revolt.SendableEmbed(description=f"## timedeltaconvert\nThis command converts a duration to a `timedelta` Python object.\n### Example Usage\n`{prefix}timedeltaconvert 1 day 15hr 82 minutes 52 s`\n### Output\n`1 day, 16:22:52`", colour="#5d82d1")]
            await ctx.message.reply(embeds=embeds)
        else:
            try:
                parsed_time = parse(duration, as_timedelta=True, raise_exception=True)
                await ctx.message.reply(f"`{str(parsed_time)}`")
            except ValueError:
                await ctx.message.reply("Please provide a convertible value!")
