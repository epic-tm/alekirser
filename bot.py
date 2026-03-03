import discord
from discord.ext import commands
import os
import random

# Your Discord Token
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is online and looking for m4a files!')

@bot.command()
async def play(ctx):
    """Plays a random m4a file from the bot's folder"""
    if not ctx.author.voice:
        return await ctx.send("🔊 Please join a voice channel first!")

    # 1. Get a list of all files ending in .m4a in the current folder
    all_files = os.listdir('.')
    m4a_files = [f for f in all_files if f.endswith('.m4a')]

    # 2. Check if we actually found any files
    if not m4a_files:
        return await ctx.send("❌ I couldn't find any .m4a files in my folder!")

    # 3. Connect to voice
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    # 4. Pick a random file from our list
    random_file = random.choice(m4a_files)

    # 5. Stop current audio and play the new one
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    try:
        source = discord.FFmpegPCMAudio(random_file)
        ctx.voice_client.play(source)
        await ctx.send(f"🎲 **Random Pick:** {random_file}")
    except Exception as e:
        await ctx.send(f"⚠️ Error playing file: {e}")

@bot.command()
async def stop(ctx):
    """Stops audio and leaves"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected.")

bot.run(TOKEN)
