from types import new_class
from nextcord import slash_command
from nextcord.ext.commands import Bot, Cog
import nextcord
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    REQUEST_CHANNEL: int = config["request_channel"]
    AD_CHANNEL: int = config["advertise_channel"]

# TODO: add as config fields
TICKET_CATEGORY: int = 1178415757378461727
EMBED_COLOR = 0xFF88FF
AD_EMBED_COLOR = 0x2ECC71
MARLOW_ID: int = 630872658027872273
ADVERTISING_ROLE: int = 1096584186304942111
# FIXME: make deploy command embed persistant


class AdForm(nextcord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(
            title="Advertisement Services",
            custom_id="persistant_modal:adform",
            timeout=None,
        )

        self.details = nextcord.ui.TextInput(
            label="Advertisement",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Contact Reason",
            required=True,
            max_length=1800,
            custom_id="persistant_modal:adform_details",
        )
        self.add_item(self.details)

    async def callback(self, inter: nextcord.Interaction) -> None:
        if isinstance(inter.channel, nextcord.TextChannel):
            category = nextcord.utils.get(inter.guild.categories, id=TICKET_CATEGORY)
            new_channel = await category.create_text_channel(
                name=f"ticket-{inter.user.name}",
                reason=f"Created ticket for {inter.user.id} - {inter.user.name}",
            )
            await inter.response.send_message(
                f"Ticket created: <#{new_channel.id}>", ephemeral=True
            )
            em = nextcord.Embed()
            em.color = AD_EMBED_COLOR
            em.set_author(icon_url=inter.user.avatar, name=inter.user.name)
            em.add_field(name="**CONTACT REQUEST ACCEPTED**", value="", inline=False)
            em.add_field(name="**reason**", value=self.details.value, inline=False)
            # TODO: add extra to footer
            em.set_footer(text=f"{inter.user.id}")

            async def mark_paid(interaction):
                await interaction.response.send_modal(QuestionForm())

            paid = nextcord.ui.Button(
                label="Mark Paid", style=nextcord.ButtonStyle.green
            )

            paid.callback = mark_paid

            view = nextcord.ui.View()
            view.add_item(paid)

            await new_channel.send(
                content=f"<@{inter.user.id}> <@{MARLOW_ID}> <@{ADVERTISING_ROLE}>",
                embed=em,
                view=view,
            )


class QuestionForm(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Contact Marlow",
            custom_id="persistant_modal:question",
            timeout=None,
        )

        self.details = nextcord.ui.TextInput(
            label="Inquiry details",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Contact Reason",
            required=True,
            max_length=1800,
            custom_id="persistent_modal:details",
        )
        self.add_item(self.details)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        if isinstance(interaction.channel, nextcord.TextChannel):
            target_channel = interaction.guild.get_channel(REQUEST_CHANNEL)
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
        self.persistent_modal_added = False

    @Cog.listener()
    async def on_ready(self):
        if not self.persistent_modal_added:
            self.bot.add_modal(AdForm())
            self.bot.add_modal(QuestionForm())
            self.persistent_modal_added = True

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
