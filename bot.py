import discord
from discord.ext import commands
import os
import random
import asyncio
import shutil
import subprocess

TOKEN = os.getenv('DISCORD_TOKEN', '').strip()

intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True    

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    # 🔍 This will print to your Railway logs so we can see if the build command worked
    path = shutil.which("ffmpeg")
    print(f'✅ Bot Online: {bot.user}')
    if path:
        print(f'⚡ FFmpeg FOUND at: {path}')
    else:
        print('❌ FFmpeg is STILL MISSING from the system path.')

@bot.command()
async def play(ctx):
    if not ctx.author.voice:
        return await ctx.send("🔊 Join a voice channel first!")

    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ No .m4a files found!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    await asyncio.sleep(1)
    
    # Try to find the executable
    exe = shutil.which("ffmpeg") or "ffmpeg"
    track = random.choice(songs)
    
    try:
        source = discord.FFmpegPCMAudio(track, executable=exe)
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        # This error message will be very specific
        await ctx.send(f"⚠️ Audio Error: {e}")
        print(f"Detailed Error: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
