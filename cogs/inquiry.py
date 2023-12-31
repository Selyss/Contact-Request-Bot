from dotenv.main import load_dotenv
from nextcord import slash_command
from nextcord.ext.commands import Bot, Cog
from nextcord.ext import commands
import nextcord
from os import getenv
from .utils.colors import EMBED_COLOR, SUCCESS, INQUIRY, REPLY, AD_EM_COLOR
from .utils.formatting import format_footer, get_id_from_em
from views.ad import AdView
from views.close import CloseView

load_dotenv()

AD_CATEGORY = int(getenv("AD_CATEGORY"))
PAID_CATEGORY = int(getenv("PAID_CATEGORY"))
CLOSED_CATEGORY = int(getenv("CLOSED_CATEGORY"))
TICKET_CATEGORY = int(getenv("TICKET_CATEGORY"))
REQUEST_CHANNEL = int(getenv("REQUEST_CHANNEL"))
ADVERTISING_ROLE = int(getenv("ADVERTISING_ROLE"))
AD_CHANNEL = int(getenv("AD_CHANNEL"))
DEPLOY_DESC = getenv("DEPLOY_DESC")
FORM_TITLE = getenv("FORM_TITLE")
PAYMENT_DESC = getenv("PAYMENT_DESC")


class TicketView(nextcord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(
            1,
            60 * 1440,
            commands.BucketType.member,  # 1 request per day
        )

    @nextcord.ui.button(
        label="📝 Open Inquiry",
        style=nextcord.ButtonStyle.blurple,
        custom_id="ticket:inquiry",
    )
    async def open_inquiry(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        if isinstance(inter.message, nextcord.Message):
            inter.message.author = inter.user
            bucket = self.cooldown.get_bucket(inter.message)
            retry = bucket.update_rate_limit()
            if retry:
                return await inter.response.send_message(
                    f"Slow down! Try again in {int(retry // 3600)}h.", ephemeral=True
                )
            await inter.response.send_modal(QuestionForm())

    @nextcord.ui.button(
        label="📢 Advertisement",
        style=nextcord.ButtonStyle.blurple,
        custom_id="ticket:advertisement",
    )
    async def advertisement(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        if isinstance(inter.message, nextcord.Message):
            inter.message.author = inter.user
            bucket = self.cooldown.get_bucket(inter.message)
            retry = bucket.update_rate_limit()
            if retry:
                return await inter.response.send_message(
                    f"Slow down! Try again in {int(retry // 3600)}h.", ephemeral=True
                )
            await inter.response.send_modal(AdForm())


class QuickResponse(nextcord.ui.Modal):
    def __init__(self, person, message, full) -> None:
        super().__init__(
            title="Quick Response",
            custom_id="ticket:quickresponse",
            timeout=None,
        )
        self.person = person
        self.message = message
        self.full = full

        self.details = nextcord.ui.TextInput(
            label="Response",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Response here...",
            required=True,
            max_length=1800,
            custom_id="ticket:quickresponse_details",
        )
        self.add_item(self.details)

    async def callback(self, inter: nextcord.Interaction) -> None:
        if isinstance(inter.channel, nextcord.TextChannel):
            person = await inter.guild.fetch_member(self.person)
            id = person.id
            name = person.name
            nick = person.global_name
            category = nextcord.utils.get(inter.guild.categories, id=CLOSED_CATEGORY)
            ac = nextcord.Embed()
            ac.title = "Accepted"
            ac.color = SUCCESS
            ac.set_author(icon_url=inter.user.avatar, name=inter.user.name)
            ac.description = self.message
            ac.set_footer(text=format_footer(inter.user.id))
            await inter.message.edit(embed=ac, view=None)
            new_channel = await category.create_text_channel(
                name=f"ticket-{name}",
                reason=f"Created ticket for {id} - {name}",
                topic=id,
            )
            await inter.response.send_message(
                f"Ticket created: <#{new_channel.id}>", ephemeral=True
            )
            # inquiry again
            emb = nextcord.Embed()
            emb.color = INQUIRY
            emb.set_author(name=f"{nick} inquired:", icon_url=person.avatar)
            emb.description = self.message
            emb.set_footer(text=format_footer(id))
            await new_channel.send(
                embed=emb,
            )

            # response msg
            em = nextcord.Embed()
            em.color = REPLY
            em.set_author(name=f"{inter.user} replied:", icon_url=inter.user.avatar)
            em.description = self.details.value
            em.set_footer(text='Press "Acknowledge" to close.')

            await new_channel.send(
                content=f"<@{id}>",
                embed=em,
                view=CloseView(CLOSED_CATEGORY),
            )
            await new_channel.set_permissions(
                person, send_messages=False, read_messages=True
            )


class RequestView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Accept", style=nextcord.ButtonStyle.green, custom_id="requestview:accept"
    )
    async def accept(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        msg = await get_id_from_em(inter)
        content = inter.message.embeds[0].description
        person = await inter.guild.fetch_member(msg)
        id = person.id
        name = person.name
        nick = person.global_name
        ac = nextcord.Embed()
        ac.title = "Accepted"
        ac.color = SUCCESS
        ac.set_author(icon_url=person.avatar, name=person.name)
        ac.description = content
        ac.set_footer(text=format_footer(inter.user.id))
        await inter.message.edit(embed=ac, view=None)
        em = nextcord.Embed()
        if inter.channel.id == AD_CHANNEL:
            # IS AD
            category = nextcord.utils.get(inter.guild.categories, id=AD_CATEGORY)
            new_channel = await category.create_text_channel(
                name=f"ticket-{name}",
                reason=f"Created ticket for {id} - {name}",
                topic=id,
            )
            await inter.response.send_message(
                f"Ticket created: <#{new_channel.id}>", ephemeral=True
            )
            em.color = SUCCESS
            em.set_author(
                name=f"{nick} requested an advertisement:", icon_url=person.avatar
            )
            em.description = content
            em.set_footer(text=format_footer(id))

            await new_channel.set_permissions(
                person, send_messages=True, read_messages=True
            )
            await new_channel.send(
                content=f"<@{inter.user.id}> <@{ADVERTISING_ROLE}>",
                embed=em,
                view=AdView(PAID_CATEGORY, ADVERTISING_ROLE),
            )
            emb = nextcord.Embed()
            emb.color = AD_EM_COLOR
            emb.title = "__**Advertisement Services**__"
            emb.description = PAYMENT_DESC
            await new_channel.send(embed=emb)

        else:
            # IS NOT AD
            category = nextcord.utils.get(inter.guild.categories, id=TICKET_CATEGORY)
            new_channel = await category.create_text_channel(
                name=f"ticket-{name}",
                reason=f"Created ticket for {id} - {name}",
                topic=id,
            )
            await inter.response.send_message(
                f"Ticket created: <#{new_channel.id}>", ephemeral=True
            )
            em.color = INQUIRY
            em.set_author(name=f"{nick} inquired:", icon_url=person.avatar)
            em.description = content
            em.set_footer(text=format_footer(id))

            await new_channel.set_permissions(
                person, send_messages=True, read_messages=True
            )
            await new_channel.send(
                content=f"<@{id}>",
                embed=em,
            )

    @nextcord.ui.button(
        label="Quick Response",
        style=nextcord.ButtonStyle.blurple,
        custom_id="ticket:quickresponse",
    )
    async def quickresponse(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        msg = await get_id_from_em(inter)
        content = inter.message.embeds[0].description
        full = inter.message.embeds[0]
        await inter.response.send_modal(QuickResponse(msg, content, full))


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
            target_channel = inter.guild.get_channel(AD_CHANNEL)
            em = nextcord.Embed()
            em.title = "Advertisement"
            em.set_author(icon_url=inter.user.avatar, name=inter.user.name)
            em.description = self.details.value
            em.set_footer(text=format_footer(inter.user.id))
            await target_channel.send(embed=em, view=RequestView())
            await inter.response.send_message(
                """📫 **Your request has been sent!**""", ephemeral=True
            )


class QuestionForm(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title=FORM_TITLE,
            custom_id="questionform:question",
            timeout=None,
        )

        self.details = nextcord.ui.TextInput(
            label="Inquiry details",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Contact Reason",
            required=True,
            max_length=1800,
            custom_id="questionform:details",
        )
        self.add_item(self.details)

    async def callback(self, inter: nextcord.Interaction) -> None:
        if isinstance(inter.channel, nextcord.TextChannel):
            target_channel = inter.guild.get_channel(REQUEST_CHANNEL)
            em = nextcord.Embed()
            em.title = "Contact Request"
            em.set_author(icon_url=inter.user.avatar, name=inter.user.name)
            em.description = self.details.value
            em.set_footer(text=format_footer(inter.user.id))
            await target_channel.send(embed=em, view=RequestView())
            await inter.response.send_message(
                """📫 **Your request has been sent!**""", ephemeral=True
            )


class Inquiry(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.persistent_modals_added = False
        self.persistent_views_added = False

    @Cog.listener()
    async def on_ready(self) -> None:
        if not self.persistent_modals_added:
            self.bot.add_modal(QuestionForm())
            self.bot.add_modal(AdForm())
            self.persistent_modals_added = True

        if not self.persistent_views_added:
            self.bot.add_view(RequestView())
            self.bot.add_view(TicketView())
            self.bot.add_view(AdView())
            self.bot.add_view(CloseView())
            self.persistent_views_added = True

    @slash_command(name="deploy", description="Send inquiry embed")
    async def deploy(self, inter: nextcord.Interaction) -> None:
        if isinstance(inter.channel, nextcord.TextChannel):
            em = nextcord.Embed(
                title="📫 Contact Request",
                description=DEPLOY_DESC,
                color=EMBED_COLOR,
            )

            await inter.channel.send(embed=em, view=TicketView())


def setup(bot: Bot) -> None:
    bot.add_cog(Inquiry(bot))
