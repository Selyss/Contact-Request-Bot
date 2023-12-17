import nextcord


class CloseView(nextcord.ui.View):
    def __init__(self, closed_category=None) -> None:
        super().__init__(timeout=None)
        self.closed_category = closed_category

    @nextcord.ui.button(
        label="Acknowledge",
        style=nextcord.ButtonStyle.blurple,
        custom_id="closeview:close",
    )
    async def close(self, btn: nextcord.ui.Button, inter: nextcord.Interaction):
        if isinstance(inter.channel, nextcord.TextChannel):
            await inter.channel.send("Closing ticket...")
            category = inter.guild.get_channel(self.closed_category)
            await inter.channel.edit(category=category)
            # TODO: remove person from ticket