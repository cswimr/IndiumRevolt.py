import os
import re
import revolt
from revolt.ext import commands
from colorthief import ColorThief
from utils.embed import CustomEmbed

class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    def rgb_to_hex(r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'

    async def upload_to_revolt(self, ctx: commands.Context, asset: revolt.Asset, color: bool = False):
        """Uploads an asset to Revolt and returns the asset ID."""
        temp_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(temp_dir, 'tempfile.png')
        with open(file_path, 'wb') as file:
            await asset.save(file)
            if color is True:
                color_thief = ColorThief(file_path)
                dominant_color = list(color_thief.get_color(quality=1))
                hex_color = self.rgb_to_hex(dominant_color[0], dominant_color[1], dominant_color[2])
            else:
                hex_color = None
        with open(file_path, 'rb') as file:
            upload_file = revolt.File(file=file_path, filename="indium.png")
            avatar_id = await ctx.client.upload_file(file=upload_file, tag="attachments")
        return avatar_id.id, hex_color

    class CustomError(Exception):
        pass

    @commands.command()
    async def avatar(self, ctx: commands.Context, target: commands.UserConverter):
        """This command retrieves a user's avatar. -  NOTE: Move to cog"""
        if not isinstance(target, revolt.User):
            await ctx.message.reply("Please provide a user argument!")
            return
        avatar = target.avatar.url
        await ctx.message.reply(f"{avatar}")

    @commands.command()
    async def channelinfo(self, ctx: commands.Context, channel: commands.ChannelConverter):
        """Displays information about a channel."""
        if str(channel.channel_type) != "ChannelType.text_channel" and str(channel.channel_type) != "ChannelType.voice_channel":
            raise self.CustomError
        # I have no idea how this works, thanks ChatGPT! :)
        formatted_channel_type = re.sub(r"(?<=\w)([A-Z])", r" \1", ' '.join(word.capitalize() for word in str(channel.channel_type).split('.')[1:])).replace("_", " ").title()
        embed = [CustomEmbed(description=f"## {channel.mention}\n### Channel Type\n{formatted_channel_type}\n### Channel ID\n{channel.id}")]
        if channel.description:
            embed[0].add_field(name="Description", value=channel.description)
        if channel.icon:
            icon_id = await self.upload_to_revolt(ctx, channel.icon, True)
            embed[0].add_field(name="Icon")
            embed[0].media = icon_id[0]
            embed[0].colour = icon_id[1]
        else:
            embed[0].colour = "#5d82d1"
        await ctx.message.reply(embeds=embed)

    @channelinfo.error
    async def channelinfo_error_handling(self, ctx: commands.Context, error: revolt.errors):
        """Handles errors from the channelinfo command."""
        if isinstance(error, self.CustomError):
            await ctx.message.reply("Please provide a valid text channel.\nDirect Messages are not currently supported.")
        elif isinstance(error, LookupError):
            await ctx.message.reply("Please provide a text channel I can access.")
        else:
            raise error

    @commands.command()
    async def serverinfo(self, ctx: commands.Context):
        """Displays information about a server."""
        embed = [CustomEmbed(description=f"## {ctx.server.name}\n### Server ID\n{ctx.server.id}")]
        embed[0].add_field(name="Owner", value=f"{ctx.server.owner.mention} ({ctx.server.owner.id})")
        if ctx.server.description:
            embed[0].add_field(name="Description", value=ctx.server.description)
        embed[0].add_field(name="Members", value=len(ctx.server.members))
        if ctx.server.roles:
            embed[0].add_field(name="Roles", value=len(ctx.server.roles))
        if ctx.server.categories:
            embed[0].add_field(name="Categories", value=len(ctx.server.categories))
        embed[0].add_field(name="Channels", value=len(ctx.server.channels))
        if ctx.server.emojis:
            embed[0].add_field(name="Emojis", value=len(ctx.server.emojis))
        if ctx.server.icon:
            icon_id = await self.upload_to_revolt(ctx, ctx.server.icon, True)
            embed[0].add_field(name="Icon")
            embed[0].media = icon_id[0]
            embed[0].colour = icon_id[1]
        else:
            embed[0].colour = "#5d82d1"
        await ctx.message.reply(embeds=embed)

    # This is commented out due to an issue with the Revolt.py library.
    # @commands.command()
    # async def roleinfo(self, ctx: commands.Context, role: revolt.Role):
    #     """Displays information about a role."""
    #     embed = [CustomEmbed(description=f"## {role.name}\n### Role ID\n{role.id}")]
    #     if role.color:
    #         embed[0].colour = role.colour
    #     else:
    #         embed[0].colour = "#5d82d1"
    #     embed[0].add_field(name="Hoisted", value=role.hoist)
    #     embed[0].add_field(name="Rank", value=role.rank)
    #     embed[0].add_field(name="Permissions", value=role.server_permissions)
    #     await ctx.message.reply(embeds=embed)

    @commands.command()
    async def userinfo(self, ctx: commands.Context, user: commands.UserConverter = None):
        """Displays information about a user."""
        if user is None:
            user = ctx.author
        avatar_id = await self.upload_to_revolt(ctx, user.avatar, True)
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
        embeds = [CustomEmbed(title=f"{user.original_name}#{user.discriminator}", description=f"### Status\n{presencedict[str(status_presence)]} - {status_text}", media=avatar_id[0])]
        if user_profile[0] is not None:
            embeds[0].add_field(name="Profile", value=user_profile[0])
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
            elif avatar_id[1] is not None:
                embeds[0].colour = avatar_id[1]
            embeds[0].set_footer(f"User ID: {user.id}")
        except LookupError:
            if user.display_name is not None:
                embeds[0].title += f" - {user.display_name}"
            embeds[0].set_footer(f"User ID: {user.id} - User is not in this server!")
        if embeds[0].colour is None:
            embeds[0].colour = "#5d82d1"
        await ctx.message.reply(embeds=embeds)
