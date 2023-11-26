from nextcord import SlashOption, TextChannel, slash_command
from nextcord.ext.commands import Bot, Cog
import nextcord
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)


class Ticket(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="config", description="set bot config")
    async def set_log_channel(
        self,
        inter: nextcord.Interaction,
        channel: TextChannel = SlashOption(
            description="channel to recieve requests",
            required=True,
        ),
    ):
        config["request_channel"] = channel.id
        with open("config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)

        await inter.send(f"Request channel set to <#{channel.id}>.", ephemeral=True)


def setup(bot: Bot) -> None:
    bot.add_cog(Ticket(bot))
