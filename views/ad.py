import nextcord
from cogs.utils.colors import SUCCESS


class AdView(nextcord.ui.View):
    def __init__(self, paid_category=None) -> None:
        super().__init__(timeout=None)
        self.paid_category = paid_category

    @nextcord.ui.button(
        label="Mark Paid", style=nextcord.ButtonStyle.green, custom_id="ticket:paid"
    )
    async def paid(self, btn: nextcord.ui.Button, inter: nextcord.Interaction) -> None:
        if isinstance(inter.channel, nextcord.TextChannel):
            category = nextcord.utils.get(inter.guild.categories, id=self.paid_category)
            await inter.channel.edit(category=category)
            em = nextcord.Embed()
            em.color = SUCCESS
            em.title = ":checkmark: Payment Received"
            em.description = """Thank you for your purchase!\nIf you haven't already, please send your advertisement message and ensure if you are using any custom/nitro-accessed Emojis that they are present within the Discord you are advertising (emojis from our server are fine, too).\n\nIf another advertisement was recently posted, out of courtesy it will be given a reasonable amount of uptime before yours is posted."""
            await inter.response.send_message(embed=em)
