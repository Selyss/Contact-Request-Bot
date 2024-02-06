from os import getenv
from nextcord import slash_command
from nextcord.ext.commands import Bot, Cog
import nextcord
from .utils.colors import CLOSE_REQUEST, REPLY
from views.close import CloseView

CLOSED_CATEGORY = int(getenv("CLOSED_CATEGORY"))


class CloseRequest(nextcord.ui.View):
    def __init__(self, inter=None, old_channel=None):
        super().__init__(timeout=None)
        self.inter = inter
        self.old_channel = old_channel

    @nextcord.ui.button(label="☑️ Accept & Close", style=nextcord.ButtonStyle.green)
    async def accept(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        if isinstance(inter.channel, nextcord.TextChannel):
            category = nextcord.utils.get(inter.guild.categories, id=CLOSED_CATEGORY)
            await self.inter.channel.send("Closing ticket...")
            await self.inter.channel.delete()

    @nextcord.ui.button(label="❌ Deny & Keep Open", style=nextcord.ButtonStyle.gray)
    async def deny(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        if isinstance(inter.channel, nextcord.TextChannel):
            category = nextcord.utils.get(
                inter.guild.categories, id=self.old_channel.category_id
            )
            await self.inter.channel.edit(category=category)
            await inter.channel.send("Request denied!")


class Ticket(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.persistent_modals_added = False
        self.persistent_views_added = False

    @Cog.listener()
    async def on_ready(self) -> None:
        if not self.persistent_modals_added:
            self.persistent_modals_added = True

        if not self.persistent_views_added:
            self.bot.add_view(CloseView())
            self.bot.add_view(CloseRequest())
            self.persistent_views_added = True

    @slash_command(name="close", description="close a ticket")
    async def close_ticket(self, inter: nextcord.Interaction):
        if inter.channel.category_id == CLOSED_CATEGORY:
            await inter.channel.delete()
            return
        em = nextcord.Embed()
        em.title = "Ticket Closed"
        em.description = f"<@{inter.user.id}> has closed this ticket.\n\nPlease acknowledge this closure using the button below."

        await inter.channel.send(embed=em, view=CloseView())

    @slash_command(name="closereq", description="request to close ticket")
    async def close_request(self, inter: nextcord.Interaction):
        em = nextcord.Embed()
        em.color = CLOSE_REQUEST
        em.title = "Ticket Close Request"
        em.description = f"<@{inter.user.id}> has requested to close this ticket.\n\nPlease accept or deny this request using the buttons below."

        category = nextcord.utils.get(inter.guild.categories, id=CLOSED_CATEGORY)
        await inter.channel.edit(category=category)
        await inter.channel.send(
            embed=em, view=CloseRequest(inter=inter, old_channel=inter.channel)
        )

    @slash_command(name="add", description="add a person to the ticket")
    async def add(
        self,
        inter: nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption(required=True),
    ):
        em = nextcord.Embed()
        em.color = REPLY
        em.title = f"User Added"
        em.description = f"<@{user.id}> has been added to this ticket."
        await inter.channel.set_permissions(
            user, read_messages=True, send_messages=True
        )
        await inter.channel.send(embed=em)


def setup(bot: Bot) -> None:
    bot.add_cog(Ticket(bot))
