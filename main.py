import os
from typing import List
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT")

intents = nextcord.Intents.default()
intents.message_content = True

print("[System] Beginning load...")
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[System] Logged in as {bot.user.name}.")

@bot.command()
async def ping(ctx):
    await ctx.reply("pong!")

if not TOKEN:
    print("[System] Missing TOKEN environment variable.")

try:
    bot.run(TOKEN)
except nextcord.errors.LoginFailure:
    print("[System] Missing Discord bot token.")
