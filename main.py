import os
import nextcord
from nextcord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT")
EMBED_COLOR = 0xFFFE88FF

intents = nextcord.Intents.default()
intents.message_content = True

print("[System] Beginning load...")
bot = Bot(command_prefix="!", intents=intents)
bot.load_extension("cogs.inquiry")
bot.load_extension("cogs.ticket")


@bot.event
async def on_ready():
    print(f"[System] Logged in as {bot.user.name}.")  # type: ignore


if not TOKEN:
    print("[System] Missing TOKEN environment variable.")

try:
    bot.run(TOKEN)
except nextcord.errors.LoginFailure:
    print("[System] Missing Discord bot token.")
