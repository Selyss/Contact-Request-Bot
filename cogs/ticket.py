from nextcord import Interaction, slash_command
from nextcord.ext.commands import Bot, Cog


class Ticket(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="ping", description="A simple ping command.")
    async def ping(self, inter: Interaction) -> None:
        await inter.send(f"Pong! {self.bot.latency * 1000:.2f}ms")


def setup(bot: Bot) -> None:
    bot.add_cog(Ticket(bot))
