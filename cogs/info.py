import os
import revolt
from revolt.ext import commands
from utils.embed import CustomEmbed

class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def upload_file(self, asset: revolt.Asset):
        temp_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(temp_dir, 'tempfile.png')
        with open(file_path, 'wb') as file:
            await asset.save(file)
        avatar_id = await self.client.upload_file(file=file_path, tag="attachments")
        os.remove(file_path)
        return avatar_id

    @commands.command()
    async def temporarycmd(self, ctx: commands.Context):
        tag = await Info.upload_file(self, ctx.author.avatar)
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

    @commands.command()
    async def userinfo(self, ctx: commands.Context, user: commands.UserConverter):
        if not user:
            user = ctx.author
        avatar_id = Info.upload_file(self, user.avatar)
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
            member = user.to_member(ctx.server)
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
