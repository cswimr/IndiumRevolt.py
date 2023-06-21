import revolt

class CustomEmbed(revolt.SendableEmbed):
    def __init__(self, *args, **kwargs):
        """
        Represents an embed that can be sent in a message, you will never receive this, you will receive :class:`Embed`.

        Attributes
        -----------
        title: Optional[:class:`str`]
            The title of the embed

        description: Optional[:class:`str`]
            The description of the embed

        media: Optional[:class:`str`]
            The file inside the embed, this is the ID of the file, you can use :meth:`Client.upload_file` to get an ID.

        icon_url: Optional[:class:`str`]
            The url of the icon url

        colour: Optional[:class:`str`]
            The embed's accent colour, this is any valid `CSS color <https://developer.mozilla.org/en-US/docs/Web/CSS/color_value>`_

        url: Optional[:class:`str`]
            URL for hyperlinking the embed's title
        """
        if "color" in kwargs:
            kwargs["colour"] = kwargs["color"]
            del kwargs["color"]
        super().__init__(*args, **kwargs)
        self.footer: str | None = None

    def add_field(self, name = None, value = None):
        if name is None and value is None:
            raise ValueError("A 'name' or 'value' must be given")

        if self.description is None:
            self.description = ""
        else:
            self.description += "\n"

        if value is None:
            self.description += f"### {name}"
        elif name is None:
            self.description += f"{value}"
        else:
            self.description += f"### {name}\n{value}"

    def set_footer(self, text):
        self.footer = text

    def to_dict(self):
        if self.footer is not None:
            if self.description is None:
                self.description = ""
            else:
                self.description += "\n\n"
            self.description += f"##### {self.footer}"
        return super().to_dict()

    def copy(self):
        deepcopy = CustomEmbed(title=self.title, description=self.description, colour=self.colour)
        deepcopy.set_footer(self.footer)
        return deepcopy
