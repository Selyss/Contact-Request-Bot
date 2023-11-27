from nextcord import SlashOption, TextChannel, slash_command
from nextcord.ext.commands import Bot, Cog
import nextcord
import json

# TODO: add to config
TICKET_CATEGORY: int = 1178415757378461727

with open("config.json", "r") as config_file:
    config = json.load(config_file)


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
        with open("config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)

        await inter.send(
            f"Request channel set to <#{request_channel.id}>. Advertisement channel set to <#{ad_channel.id}>.",
            ephemeral=True,
        )

    @slash_command(name="ticket")
    async def create_ticket(self, inter: nextcord.Interaction) -> None:
        category = nextcord.utils.get(inter.guild.categories, id=TICKET_CATEGORY)
        new_channel = await category.create_text_channel(
            name=f"ticket-{inter.user.name}",
            reason=f"Created ticket for {inter.user.id} - {inter.user.name}",
        )
        await inter.response.send_message(
            f"Ticket created: <#{new_channel.id}>", ephemeral=True
        )


def setup(bot: Bot) -> None:
    bot.add_cog(Ticket(bot))
