import discord
from discord.ext import commands
import os
import random
import asyncio
import shutil

TOKEN = os.getenv('DISCORD_TOKEN', '').strip()

intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True    

bot = commands.Bot(command_prefix='!', intents=intents)

def find_ffmpeg():
    """Hunts for the FFmpeg engine in the system."""
    # Check standard path
    path = shutil.which("ffmpeg")
    if path:
        return path
    # Check common Linux paths
    for loc in ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/app/ffmpeg"]:
        if os.path.exists(loc):
            return loc
    return None

@bot.event
async def on_ready():
    path = find_ffmpeg()
    print(f'✅ Bot Online: {bot.user}')
    print(f'🛠️ FFmpeg Status: {"FOUND at " + path if path else "STILL MISSING"}')

@bot.command()
async def play(ctx):
    if not ctx.author.voice:
        return await ctx.send("🔊 Join a voice channel first!")

    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ No .m4a files found in the folder!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    await asyncio.sleep(1)
    
    exe_path = find_ffmpeg()
    track = random.choice(songs)
    
    try:
        # We explicitly tell Discord where the engine is
        source = discord.FFmpegPCMAudio(track, executable=exe_path or "ffmpeg")
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        await ctx.send(f"⚠️ Audio Error: {e}")
        print(f"DEBUG: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
