import json
from nextcord import SlashOption, TextChannel, slash_command
from nextcord.ext.commands import Bot, Cog
import nextcord

CLOSED_CATEGORY = 1182473403303723128

with open("config.json", "r", encoding="utf-8") as conf:
    config = json.load(conf)


class CloseRequest(nextcord.ui.View):
    def __init__(self, inter: nextcord.Interaction):
        super().__init__(timeout=60)
        self.inter = inter

    @nextcord.ui.button(label="☑️ Accept & Close", style=nextcord.ButtonStyle.green)
    async def accept(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.inter.channel.send("Closing ticket...")
        await self.inter.channel.edit(category=CLOSED_CATEGORY)
        await self.inter.channel.set_permissions(
            self.inter.author, read_messages=False, send_messages=False
        )
        await self.inter.channel.send("Ticket closed!")

    @nextcord.ui.button(label="❌ Deny & Keep Open", style=nextcord.ButtonStyle.gray)
    async def deny(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await inter.channel.send("Request denied!")


class CloseView(nextcord.ui.View):
    def __init__(self, inter: nextcord.Interaction):
        super().__init__(timeout=60)
        self.inter = inter

    @nextcord.ui.button(label="Acknowledge", style=nextcord.ButtonStyle.blurple)
    async def accept(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.inter.channel.send("Closing ticket...")
        await self.inter.channel.edit(category=CLOSED_CATEGORY)
        await self.inter.channel.set_permissions(
            self.inter.author, read_messages=False, send_messages=False
        )


class Ticket(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="config", description="set bot config")
    async def set_log_channel(
        self,
        inter: nextcord.Interaction,
        request_channel: TextChannel = SlashOption(
            description="channel to recieve requests",
            required=False,
        ),
        ad_channel: TextChannel = SlashOption(
            description="channel to recieve advertisements",
            required=False,
        ),
    ):
        config["request_channel"] = request_channel.id
        config["advertise_channel"] = ad_channel.id
        with open("config.json", "w", encoding="utf-8") as config_file:
            json.dump(config, config_file, indent=4)

        await inter.send(
            f"""
            Request channel set to <#{request_channel.id}>
            Advertisement channel set to <#{ad_channel.id}>
            """,
            ephemeral=True,
        )

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
        em.color = 0x3498DB
        em.title = "Ticket Close Request"
        em.description = f"<@{inter.user.id}> has requested to close this ticket.\n\nPlease accept or deny this request using the buttons below."

        await inter.channel.send(embed=em, view=CloseRequest(inter=inter))


def setup(bot: Bot) -> None:
    bot.add_cog(Ticket(bot))
