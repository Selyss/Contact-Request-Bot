import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

from cogs.inquiry import AdForm, QuestionForm

load_dotenv()

TOKEN = os.getenv("BOT")
EMBED_COLOR = 0xFFFE88FF

intents = nextcord.Intents.default()
intents.message_content = True

print("[System] Beginning load...")


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.persistent_modals_added = False

    async def on_ready(self):
        if not self.persistent_modals_added:
            self.add_modal(AdForm())
            self.add_modal(QuestionForm())
            self.persistent_modals_added = True

        print(f"[System] Logged in as {bot.user.name}.")


bot = Bot(command_prefix="!", intents=intents)
bot.load_extension("cogs.inquiry")
bot.load_extension("cogs.ticket")


if not TOKEN:
    print("[System] Missing TOKEN environment variable.")

try:
    bot.run(TOKEN)
except nextcord.errors.LoginFailure:
    print("[System] Missing Discord bot token.")
