import nextcord
from cogs.utils.colors import SUCCESS
from os import getenv
from dotenv.main import load_dotenv

load_dotenv()

AD_PAID_DESC = getenv("AD_PAID_DESC")
AD_PAID_TITLE = getenv("AD_PAID_TITLE")


class AdView(nextcord.ui.View):
    def __init__(self, paid_category=None, advertising_role=None) -> None:
        super().__init__(timeout=None)
        self.paid_category = paid_category
        self.advertising_role = advertising_role

    @nextcord.ui.button(
        label="Mark Paid", style=nextcord.ButtonStyle.green, custom_id="ticket:paid"
    )
    async def paid(self, btn: nextcord.ui.Button, inter: nextcord.Interaction) -> None:
        if isinstance(inter.channel, nextcord.TextChannel):
            if inter.permissions.administrator or (
                nextcord.utils.get(inter.guild.roles, id=self.advertising_role)
                in inter.roles
            ):
                category = nextcord.utils.get(
                    inter.guild.categories, id=self.paid_category
                )
                await inter.channel.edit(category=category)
                em = nextcord.Embed()
                em.color = SUCCESS
                em.title = AD_PAID_TITLE
                em.description = AD_PAID_DESC
                await inter.response.send_message(embed=em)
