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

moddb = mysql.connector.connect(
host=db_host,
user=db_user,
password=db_password,
database=db
)
cursor = moddb.cursor()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        disable_dateutil()

    @commands.command(name="mute", aliases=["timeout"])
    async def mute(self, ctx: commands.Context, target: commands.MemberConverter, *, duration: str = "1 hour"):
        try:
            parsed_time = parse(duration, as_timedelta=True, raise_exception=True)
        except ValueError:
            await ctx.message.reply(f"Please provide a valid duration!\nSee `{prefix}tdc`")
            return
        await target.timeout(parsed_time)
        await ctx.message.reply(f"{target.mention} has been timed out for {str(parsed_time)}!")
        embeds = [revolt.SendableEmbed(title="Timed Out", description=f"You have been timed out for {str(parsed_time)}.", colour="#5d82d1")]
        await target.send(embeds=embeds)
        # latest_id = cursor.execute("SELECT * FROM mod ORDER BY moderation_id DESC LIMIT 1;")
        # sql = "INSERT INTO mod (moderation_id, moderation_type, target_id, duration, reason) VALUES (%s, %s, %s, %s, %s)"
        # val = (latest_id, "Timeout", target.id, parsed_time, "Testing")
        # cursor.execute(sql, val)

        # moddb.commit()

        # print(moddb.rowcount, "record inserted.")

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
