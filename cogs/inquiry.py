from datetime import datetime
import json
from nextcord import slash_command
from nextcord.ext.commands import Bot, Cog
from nextcord.ext import commands
import nextcord


with open("config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)
    REQUEST_CHANNEL: int = config["request_channel"]
    # PAID_CATEGORY: int = config["paid_category"]

# TODO: add as config fields
TICKET_CATEGORY: int = 1178415757378461727
PAID_CATEGORY: int = 1181391079698878555
EMBED_COLOR = 0xFF88FF
AD_EMBED_COLOR = 0x2ECC71
MARLOW_ID: int = 630872658027872273
ADVERTISING_ROLE: int = 1096584186304942111


def get_date() -> str:
    return datetime.now().strftime("%m/%d/%Y")


def get_time() -> str:
    return datetime.now().strftime("%-I:%M %p")


class TicketView(nextcord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(
            1, 60 * 1440, commands.BucketType.member  # 1 request per day
        )

    @nextcord.ui.button(
        label="📝 Open Inquiry",
        style=nextcord.ButtonStyle.blurple,
        custom_id="ticket:inquiry",
    )
    async def open_inquiry(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        inter.message.author = inter.user
        bucket = self.cooldown.get_bucket(inter.message)
        retry = bucket.update_rate_limit()
        if retry:
            return await inter.response.send_message(
                f"Slow down! Try again in {round(retry, 1)} seconds.", ephemeral=True
            )
        await inter.response.send_modal(QuestionForm())

    @nextcord.ui.button(
        label="📢 Advertisement",
        style=nextcord.ButtonStyle.blurple,
        custom_id="ticket:advertisement",
    )
    async def advertisement(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        inter.message.author = inter.user
        bucket = self.cooldown.get_bucket(inter.message)
        retry = bucket.update_rate_limit()
        if retry:
            return await inter.response.send_message(
                f"Slow down! Try again in {round(retry, 1)} seconds.", ephemeral=True
            )
        await inter.response.send_modal(AdForm())


class QuickResponse(nextcord.ui.Modal):
    def __init__(self, person) -> None:
        super().__init__(
            title="Quick Response",
            timeout=None,
        )
        self.person = person

        self.details = nextcord.ui.TextInput(
            label="Response",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Response here...",
            required=True,
            max_length=1800,
        )
        self.add_item(self.details)

    async def callback(self, inter: nextcord.Interaction) -> None:
        if isinstance(inter.channel, nextcord.TextChannel):
            # marlow = inter.guild.get_member(MARLOW_ID)

            category = nextcord.utils.get(inter.guild.categories, id=TICKET_CATEGORY)
            new_channel = await category.create_text_channel(
                name=f"ticket-{inter.user.name}",
                reason=f"Created ticket for {inter.user.id} - {inter.user.name}",
                topic=self.person.user.id,
            )
            await inter.response.send_message(
                f"Ticket created: <#{new_channel.id}>", ephemeral=True
            )
            em = nextcord.Embed()
            em.color = EMBED_COLOR
            # em.set_author(icon_url=marlow.user.avatar, name=marlow.user.name)
            em.add_field(name="**CONTACT REQUEST ACCEPTED**", value="", inline=False)
            em.add_field(name="**message**", value=self.details.value, inline=False)
            em.set_footer(text=f"{inter.user.id} • {get_date()} • {get_time()}")

            await new_channel.send(
                content=f"<@{inter.user.id}>",
                embed=em,
                view=CloseView(),
            )


class RequestView(nextcord.ui.View):
    def __init__(self, person, message) -> None:
        super().__init__(timeout=None)
        self.person = person
        self.message = message

    @nextcord.ui.button(
        label="Accept", style=nextcord.ButtonStyle.green, custom_id="ticket:accept"
    )
    async def accept(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        category = nextcord.utils.get(inter.guild.categories, id=TICKET_CATEGORY)
        new_channel = await category.create_text_channel(
            name=f"ticket-{inter.user.name}",
            reason=f"Created ticket for {inter.user.id} - {inter.user.name}",
            topic=self.person.user.id,
        )
        await inter.response.send_message(
            f"Ticket created: <#{new_channel.id}>", ephemeral=True
        )
        em = nextcord.Embed()
        em.color = EMBED_COLOR
        em.add_field(name="**CONTACT REQUEST ACCEPTED**", value="", inline=False)
        em.add_field(name="**message**", value=self.message, inline=False)
        em.set_footer(text=f"{inter.user.id} • {get_date()} • {get_time()}")

        await new_channel.send(
            content=f"<@{inter.user.id}>",
            embed=em,
            view=CloseView(),
        )

    @nextcord.ui.button(
        label="Quick Response",
        style=nextcord.ButtonStyle.blurple,
        custom_id="ticket:quickresponse",
    )
    async def quickresponse(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        await inter.response.send_modal(QuickResponse(self.person))


class CloseView(nextcord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Close", style=nextcord.ButtonStyle.red, custom_id="ticket:close"
    )
    async def close(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        await inter.channel.delete()


class AdView(nextcord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Mark Paid", style=nextcord.ButtonStyle.green, custom_id="ticket:paid"
    )
    async def paid(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        category = nextcord.utils.get(inter.guild.categories, id=PAID_CATEGORY)
        await inter.channel.edit(category=category)


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
                topic=inter.user.id,
            )
            await inter.response.send_message(
                f"Ticket created: <#{new_channel.id}>", ephemeral=True
            )
            em = nextcord.Embed()
            em.color = AD_EMBED_COLOR
            em.set_author(icon_url=inter.user.avatar, name=inter.user.name)
            em.add_field(name="**CONTACT REQUEST ACCEPTED**", value="", inline=False)
            em.add_field(name="**reason**", value=self.details.value, inline=False)
            em.set_footer(text=f"{inter.user.id} • {get_date()} • {get_time()}")

            await new_channel.send(
                content=f"<@{inter.user.id}> <@{MARLOW_ID}> <@{ADVERTISING_ROLE}>",
                embed=em,
                view=AdView(),
            )
            await new_channel.send(
                content="""--------------------------------------------\n__**ADVERTISEMENT SERVICES**__\n\n🔔 $40 = Ping @ everyone with ad message/links\n\n🎁  $45 = Hosted Nitro Giveaway Ad with @ everyone ping (Nitro must be supplied by the customer)\n\n*These prices apply to the Vanilla PvP Community/Tier List*\n--------------------------------------------"""
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

    async def callback(self, inter: nextcord.Interaction) -> None:
        if isinstance(inter.channel, nextcord.TextChannel):
            target_channel = inter.guild.get_channel(REQUEST_CHANNEL)
            em = nextcord.Embed()
            em.set_author(icon_url=inter.user.avatar, name=inter.user.name)
            em.add_field(name="**reason**", value=self.details.value)
            em.set_footer(text=f"{inter.user.id} • {get_date()} • {get_time()}")

            await target_channel.send(
                embed=em, view=RequestView(person=inter, message=self.details.value)
            )
            await inter.response.send_message(
                """📫 **Your request has been sent!**""", ephemeral=True
            )


class Inquiry(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.persistent_modal_added = False

    @Cog.listener()
    async def on_ready(self) -> None:
        if not self.persistent_modal_added:
            self.bot.add_view(RequestView(None, None))
            self.bot.add_view(TicketView())
            self.bot.add_view(AdView())
            self.persistent_modal_added = True

    @slash_command(name="deploy", description="Send inquiry embed")
    async def deploy(self, inter: nextcord.Interaction) -> None:
        if isinstance(inter.channel, nextcord.TextChannel):
            em = nextcord.Embed(
                title="📫 Contact Request",
                description="""
                Due to an influx of messages, I have decided to use requests to filter spam while still providing a means for important inquiries to be made.

                I cannot guarantee a response to each inquiry.
                Please reserve this system for important reasons.
                """,
                color=EMBED_COLOR,
            )

            await inter.channel.send(embed=em, view=TicketView())


def setup(bot: Bot) -> None:
    bot.add_cog(Inquiry(bot))
