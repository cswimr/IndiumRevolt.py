import os
import revolt
from revolt.ext import commands
from utils.embed import CustomEmbed

class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def upload_to_revolt(self, asset: revolt.Asset):
        """Uploads an asset to Revolt and returns the asset ID."""
        temp_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(temp_dir, 'latest_avatar.png')
        with open(file_path, 'wb') as file:
            await asset.save(file)
        with open(file_path, 'rb') as file:
            upload_file = revolt.File(file=file_path)
            avatar_id = await self.client.upload_file(file=upload_file, tag="attachments")
        return avatar_id

    @commands.command()
    async def temporarycmd(self, ctx: commands.Context):
        tag = str(await Info.upload_to_revolt(self, ctx.author.avatar))
        await ctx.message.reply(tag)

    @commands.command()
    async def color(self, ctx: commands.Context):
        user = ctx.author
        roles=list(reversed(user.roles))
        highest_role_color = None
        for role in roles:
            if role.colour is not None:
                highest_role_color = role.colour
                break
        if highest_role_color:
            await ctx.message.reply(highest_role_color)

    class CustomError(Exception):
        pass

    @commands.command()
    async def channelinfo(self, ctx: commands.Context, channel: commands.ChannelConverter, permissions: commands.BoolConverter = False):
        if str(channel.channel_type) != "ChannelType.text_channel" and str(channel.channel_type) != "ChannelType.voice_channel":
            raise Info.CustomError
        await ctx.message.reply(f"Command executed!\n{permissions}")

    @channelinfo.error
    async def channelinfo_error_handling(self, ctx: commands.Context, error: revolt.errors):
        """Handles errors from the channelinfo command."""
        if isinstance(error, Info.CustomError):
            await ctx.message.reply("Please provide a valid text channel.\nDirect Messages are not currently supported.")
        elif isinstance(error, LookupError):
            await ctx.message.reply("Please provide a text channel I can access.")
        else:
            raise error

    @commands.command()
    async def userinfo(self, ctx: commands.Context, user: commands.UserConverter = None):
        """Displays information about a user."""
        if user is None:
            user = ctx.author
        avatar_id = await Info.upload_to_revolt(self, user.avatar)
        user_profile = await user.fetch_profile()
        presencedict = {
            "PresenceType.online": "🟢",
            "PresenceType.idle": "🟡",
            "PresenceType.busy": "🔴",
            "PresenceType.focus": "🔵",
            "PresenceType.invisible": "⚫"
        }
        if user.status is None:
            status_presence = "PresenceType.invisible"
            status_text = "Offline"
        elif user.status.text is not None:
            status_text = user.status.text
            status_presence = user.status.presence
        else:
            if str(user.status.presence) != "PresenceType.invisible":
                status_text = str(user.status.presence).split(".", 1)[-1].capitalize()
            else:
                status_text = "Offline"
            status_presence = user.status.presence
        embeds = [CustomEmbed(title=f"{user.original_name}#{user.discriminator}", description=f"### Status\n{presencedict[str(status_presence)]} - {status_text}\n### Profile\n{user_profile[0]}", media=avatar_id)]
        try:
            if not isinstance(user, revolt.Member):
                member = user.to_member(ctx.server)
            else:
                member = user
            if member.nickname is not None:
                embeds[0].title += f" - {member.nickname}"
            elif member.display_name is not None:
                embeds[0].title += f" - {member.display_name}"
            member_roles = list(reversed(member.roles))
            member_role_names = [f"$\\textsf{{\\textcolor{{{role.colour}}}{{{role.name}}}}}$" for role in member_roles]
            humanized_member_roles = ', '.join(member_role_names)
            embeds[0].add_field(name="Roles", value=humanized_member_roles)
            highest_role_color = None
            for role in member_roles:
                if role.colour is not None:
                    highest_role_color = role.colour
                    break
            if highest_role_color:
                embeds[0].colour = highest_role_color
            embeds[0].set_footer(f"User ID: {user.id}")
        except LookupError:
            if user.display_name is not None:
                embeds[0].title += f" - {user.display_name}"
            embeds[0].set_footer(f"User ID: {user.id} - User is not in this server!")
        if embeds[0].colour is None:
            embeds[0].colour = "#5d82d1"
        await ctx.message.reply(embeds=embeds)
