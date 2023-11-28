import json
from nextcord import SlashOption, TextChannel, slash_command
from nextcord.ext.commands import Bot, Cog
import nextcord

with open("config.json", "r", encoding="utf-8") as config_file:
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
        with open("config.json", "w", encoding="utf-8") as config_file:
            json.dump(config, config_file, indent=4)

        await inter.send(
            f"""
            Request channel set to <#{request_channel.id}>
            Advertisement channel set to <#{ad_channel.id}>
            """,
            ephemeral=True,
        )


def setup(bot: Bot) -> None:
    bot.add_cog(Ticket(bot))
