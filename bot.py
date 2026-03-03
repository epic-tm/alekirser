import discord
from discord.ext import commands
import os
import random
import asyncio
import shutil

# 1. CLEAN TOKEN LOAD
TOKEN = os.getenv('DISCORD_TOKEN', '').strip()

# 2. INTENTS (Must be enabled in Discord Dev Portal)
intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True    

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    # This check runs immediately when the bot starts
    ffmpeg_check = shutil.which("ffmpeg")
    print(f'✅ Bot Online: {bot.user}')
    if ffmpeg_check:
        print(f'🔊 FFmpeg found at: {ffmpeg_check}')
    else:
        print('❌ FFmpeg NOT FOUND on this server!')

@bot.command()
async def play(ctx):
    """Simple local playback"""
    if not ctx.author.voice:
        return await ctx.send("🔊 Join a Voice Channel first!")

    # Find any m4a files in the folder
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ No .m4a files found in the project folder!")

    # Connect to Voice
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    await asyncio.sleep(1)
    track = random.choice(songs)
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    try:
        # We use the simplest call possible
        source = discord.FFmpegPCMAudio(track)
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        # This catches the "ffmpeg not found" error from your screenshots
        await ctx.send(f"⚠️ Error: {e}")

bot.run(TOKEN)
