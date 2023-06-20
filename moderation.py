from datetime import timedelta
import revolt
from revolt.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_timedelta(self, input_str):
        # Split the string into its components (e.g., "1 day 3 hours" becomes ["1", "day", "3", "hours"])
        components = input_str.split()

        # Define a dictionary to map time units to their corresponding `timedelta` attribute
        units = {"days": "days", "hours": "hours", "minutes": "minutes", "seconds": "seconds"}

        # Iterate over the components, taking pairs of values and units
        values_units = zip(components[::2], components[1::2])

        # Initialize a dictionary to store the values for each unit
        values = {}

        # Parse the values and units into the dictionary
        for value, unit in values_units:
            # Convert the value to an integer
            value = int(value)
            # Map the unit to the corresponding `timedelta` attribute and store the value
            values[units[unit]] = value

        # Create and return the `timedelta` object
        return timedelta(**values)


    @commands.command(name="mute", aliases="timeout")
    async def mute(self, ctx, target: revolt.Member, duration: str = "1 hour"):
        parsed_time = Moderation.parse_timedelta(self, duration)
        await target.timeout(parsed_time)
        await ctx.message.reply(f"{target.mention} has been timed out for {str(parsed_time)}!")

    @commands.command()
    async def timedeltaconvert(self, ctx, *, duration: str = "1 hour"):
        parsed_time = Moderation.parse_timedelta(self, duration)
        await ctx.send(str(parsed_time))
