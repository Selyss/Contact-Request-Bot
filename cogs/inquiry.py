from nextcord import slash_command
from nextcord.ext.commands import Bot, Cog
import nextcord

EMBED_COLOR = 0xff88ff


class QuestionForm(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Contact Marlow",
            timeout=5 * 60,  # 5 minutes
        )

        self.details = nextcord.ui.TextInput(
            label="Inquiry details",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Contact Reason",
            required=True,
            max_length=1800,
        )
        self.add_item(self.details)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        response = "Placeholder."
        if self.details.value != "":
            response += (
                "response"
            )
        await interaction.send(response)



class Inquiry(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="deploy", description="Send inquiry embed")
    async def deploy(self, ctx) -> None:
        if isinstance(ctx.channel, nextcord.TextChannel):
            em = nextcord.Embed(
                title="📫 Contact Request",
                description="""
                Due to an influx of messages, I have decided to use requests to filter spam while still providing a means for important inquiries to be made.

                I cannot guarantee a response to each inquiry.
                Please reserve this system for important reasons.
                """,
                color=EMBED_COLOR,
            )

            async def btn_callback(interaction):
                await interaction.response.send_modal(QuestionForm())

            btn = nextcord.ui.Button(label="📝 Open Inquiry", style=nextcord.ButtonStyle.blurple)
            btn.callback = btn_callback
            view = nextcord.ui.View()
            view.add_item(btn)

            await ctx.channel.send(embed=em, view=view)

def setup(bot: Bot) -> None:
    bot.add_cog(Inquiry(bot))
