import discord
from discord.ext import commands
import os
import random

# Pulls your token from your hosting provider's environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is online! Ready to play local m4a files.')

@bot.command()
async def play(ctx):
    """Picks a random .m4a from the folder and plays it"""
    if not ctx.author.voice:
        return await ctx.send("🔊 Please join a voice channel first!")

    # 1. Get all files in the current directory ending with .m4a
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]

    if not songs:
        return await ctx.send("❌ I couldn't find any .m4a files in my folder! Did you upload them to GitHub?")

    # 2. Connect to the voice channel
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    # 3. Pick a random song
    random_song = random.choice(songs)

    # 4. Stop any current audio
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    try:
        # 5. Play the file using FFmpeg
        source = discord.FFmpegPCMAudio(random_song)
        ctx.voice_client.play(source)
        await ctx.send(f"🎲 **Now Playing:** {random_song}")
    except Exception as e:
        await ctx.send(f"⚠️ Technical Error: {e}")

@bot.command()
async def stop(ctx):
    """Stops the music and leaves the channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 See you later!")

bot.run(TOKEN)
