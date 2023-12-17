from os import getenv
from nextcord import slash_command
from nextcord.ext.commands import Bot, Cog
import nextcord
from .utils.colors import CLOSE_REQUEST

CLOSED_CATEGORY = int(getenv("CLOSED_CATEGORY"))


class CloseRequest(nextcord.ui.View):
    def __init__(self, inter: nextcord.Interaction):
        super().__init__(timeout=60)
        self.inter = inter

    @nextcord.ui.button(label="☑️ Accept & Close", style=nextcord.ButtonStyle.green)
    async def accept(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        if isinstance(inter.channel, nextcord.TextChannel):
            category = nextcord.utils.get(inter.guild.categories, id=CLOSED_CATEGORY)
            await self.inter.channel.send("Closing ticket...")
            await self.inter.channel.edit(category=category)
            await self.inter.channel.set_permissions(
                self.inter.user, send_messages=False, read_messages=False
            )
            await self.inter.channel.send("Ticket closed!")

    @nextcord.ui.button(label="❌ Deny & Keep Open", style=nextcord.ButtonStyle.gray)
    async def deny(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        if isinstance(inter.channel, nextcord.TextChannel):
            await inter.channel.send("Request denied!")


class CloseView(nextcord.ui.View):
    def __init__(self, inter=None):
        super().__init__(timeout=60)
        self.inter = inter

    @nextcord.ui.button(label="Acknowledge", style=nextcord.ButtonStyle.blurple)
    async def accept(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        category = nextcord.utils.get(inter.guild.categories, id=CLOSED_CATEGORY)
        await self.inter.channel.send("Closing ticket...")
        await self.inter.channel.edit(category=category)
        await self.inter.channel.set_permissions(
            self.inter.user, read_messages=False, send_messages=False
        )
        # FIXME: duplicate?


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
            self.persistent_views_added = True

    @slash_command(name="close", description="close a ticket")
    async def close_ticket(self, inter: nextcord.Interaction):
        if inter.channel.category_id == CLOSED_CATEGORY:
            await inter.send("This channel is already closed!", ephemeral=True)
            return
        em = nextcord.Embed()
        em.title = "Ticket Closed"
        em.description = f"<@{inter.user.id}> has closed this ticket.\n\nPlease acknowledge this closure using the button below."

        await inter.channel.send(embed=em, view=CloseView(inter=inter))

    @slash_command(name="closereq", description="request to close ticket")
    async def close_request(self, inter: nextcord.Interaction):
        if inter.channel.category_id == CLOSED_CATEGORY:
            await inter.send("This channel is already closed!", ephemeral=True)
            return

        em = nextcord.Embed()
        em.color = CLOSE_REQUEST
        em.title = "Ticket Close Request"
        em.description = f"<@{inter.user.id}> has requested to close this ticket.\n\nPlease accept or deny this request using the buttons below."

        await inter.channel.send(embed=em, view=CloseRequest(inter=inter))


def setup(bot: Bot) -> None:
    bot.add_cog(Ticket(bot))
