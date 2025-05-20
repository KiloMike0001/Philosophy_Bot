import discord
import openai
import os
import json
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_KEY
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

with open("philosophers.json") as f:
    philosophers = json.load(f)

sessions = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

def get_session_key(ctx, philosopher):
    return f"{ctx.author.id}:{philosopher}"

@bot.command()
async def talk(ctx, philosopher_name: str, *, question: str):
    if philosopher_name not in philosophers:
        await ctx.send("Unknown philosopher.")
        return

    system_prompt = philosophers[philosopher_name]
    key = get_session_key(ctx, philosopher_name)

    if key not in sessions:
        sessions[key] = []

    session = sessions[key]
    session.append({"role": "user", "content": question})
    messages = [{"role": "system", "content": system_prompt}] + session[-10:]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    reply = response.choices[0].message["content"]
    session.append({"role": "assistant", "content": reply})
    await ctx.send(reply)

bot.run(DISCORD_TOKEN)
