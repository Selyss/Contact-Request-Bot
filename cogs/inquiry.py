from nextcord import slash_command
from nextcord.ext.commands import Bot, Cog
import nextcord
import json


with open("config.json", "r") as config_file:
    config = json.load(config_file)
    CHANNEL: int = config["request_channel"]

EMBED_COLOR = 0xFF88FF


class AdForm(nextcord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(
            "Advertisement Services",
            timeout=5 * 60,  # 5 minutes
        )

        self.details = nextcord.ui.TextInput(
            label="Advertisement",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Contact Reason",
            required=True,
            max_length=1800,
        )
        self.add_item(self.details)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        if isinstance(interaction.channel, nextcord.TextChannel):
            target_channel = interaction.guild.get_channel(CHANNEL)
            em = nextcord.Embed()
            em.set_author(icon_url=interaction.user.avatar, name=interaction.user.name)
            em.add_field(name="**reason**", value=self.details.value)
            # TODO: add extra to footer
            em.set_footer(text=f"{interaction.user.id}")

            async def btn_callback(interaction):
                await interaction.response.send_modal(QuestionForm())

            async def ad_btn_callback(interaction):
                await interaction.response.send_modal(AdForm())

            accept = nextcord.ui.Button(
                label="Accept", style=nextcord.ButtonStyle.green
            )
            reject = nextcord.ui.Button(label="Reject", style=nextcord.ButtonStyle.red)

            accept.callback = btn_callback
            reject.callback = ad_btn_callback

            view = nextcord.ui.View()
            view.add_item(accept)
            view.add_item(reject)

            await target_channel.send(embed=em, view=view)


class QuestionForm(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Contact Marlow",
            timeout=5 * 60,  # 5 minutes
        )

        self.details = nextcord.ui.TextInput(
            label="Inquiry details",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Contact Reason",
            required=True,
            max_length=1800,
        )
        self.add_item(self.details)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        if isinstance(interaction.channel, nextcord.TextChannel):
            target_channel = interaction.guild.get_channel(CHANNEL)
            em = nextcord.Embed()
            em.set_author(icon_url=interaction.user.avatar, name=interaction.user.name)
            em.add_field(name="**reason**", value=self.details.value)
            # TODO: add extra to footer
            em.set_footer(text=f"{interaction.user.id}")

            async def btn_callback(interaction):
                await interaction.response.send_modal(QuestionForm())

            async def ad_btn_callback(interaction):
                await interaction.response.send_modal(AdForm())

            accept = nextcord.ui.Button(
                label="Accept", style=nextcord.ButtonStyle.green
            )
            reject = nextcord.ui.Button(label="Reject", style=nextcord.ButtonStyle.red)

            accept.callback = btn_callback
            reject.callback = ad_btn_callback

            view = nextcord.ui.View()
            view.add_item(accept)
            view.add_item(reject)

            await target_channel.send(embed=em, view=view)


class Inquiry(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="deploy", description="Send inquiry embed")
    async def deploy(self, ctx) -> None:
        if isinstance(ctx.channel, nextcord.TextChannel):
            em = nextcord.Embed(
                title="📫 Contact Request",
                description="""
                Due to an influx of messages, I have decided to use requests to filter spam while still providing a means for important inquiries to be made.

                I cannot guarantee a response to each inquiry.
                Please reserve this system for important reasons.
                """,
                color=EMBED_COLOR,
            )

            async def btn_callback(interaction):
                await interaction.response.send_modal(QuestionForm())

            async def ad_btn_callback(interaction):
                await interaction.response.send_modal(AdForm())

            btn = nextcord.ui.Button(
                label="📝 Open Inquiry", style=nextcord.ButtonStyle.blurple
            )
            ad_btn = nextcord.ui.Button(
                label="📢 Advertisement", style=nextcord.ButtonStyle.blurple
            )

            btn.callback = btn_callback
            ad_btn.callback = ad_btn_callback

            view = nextcord.ui.View()
            view.add_item(btn)
            view.add_item(ad_btn)

            await ctx.channel.send(embed=em, view=view)


def setup(bot: Bot) -> None:
    bot.add_cog(Inquiry(bot))
