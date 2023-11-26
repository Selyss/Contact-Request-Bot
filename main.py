import os
from nextcord import PermissionOverwrite, TextChannel
from typing import List
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Bot
from nextcord import SlashOption
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT")
EMBED_COLOR = 0xfffe88ff

intents = nextcord.Intents.default()
intents.message_content = True

print("[System] Beginning load...")
bot = Bot(command_prefix="!", intents=intents)
bot.load_extension("cogs.inquiry")

@bot.event
async def on_ready():
    print(f"[System] Logged in as {bot.user.name}.")


if not TOKEN:
    print("[System] Missing TOKEN environment variable.")

try:
    bot.run(TOKEN)
except nextcord.errors.LoginFailure:
    print("[System] Missing Discord bot token.")
