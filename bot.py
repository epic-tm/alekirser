import discord
from discord.ext import commands
import os
import random
import asyncio
import shutil

# 1. Load Token
TOKEN = os.getenv('DISCORD_TOKEN', '').strip()

# 2. Setup Intents
intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True    

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is online: {bot.user}')
    # Check if Railway's builder actually installed FFmpeg
    path = shutil.which("ffmpeg")
    print(f'🛠️ FFmpeg Check: {"READY" if path else "MISSING"}')

@bot.command()
async def play(ctx):
    if not ctx.author.voice:
        return await ctx.send("🔊 Join a voice channel first!")

    # Find local files
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ No .m4a files found in the folder!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    await asyncio.sleep(1)
    track = random.choice(songs)
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    try:
        # Standard FFmpeg call (Railway builder makes this work)
        source = discord.FFmpegPCMAudio(track)
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        await ctx.send(f"⚠️ Audio Error: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the channel.")

bot.run(TOKEN)
