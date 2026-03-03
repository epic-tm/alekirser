import discord
from discord.ext import commands
import os
import random
import asyncio
import shutil

# 1. Get Token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN', '').strip()

# 2. Setup Intents (Must be ON in Discord Developer Portal)
intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True    

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as: {bot.user.name}')
    # Verify files are present
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    print(f'📂 Found {len(songs)} tracks in folder.')

@bot.command()
async def play(ctx):
    """Joins voice and plays a random m4a file"""
    if not ctx.author.voice:
        return await ctx.send("🔊 Please join a Voice Channel first!")

    # Search for audio files
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ Error: No .m4a files found in the bot folder!")

    # Connect to Voice
    if ctx.voice_client is None:
        vc = await ctx.author.voice.channel.connect()
    else:
        vc = ctx.voice_client

    # Wait for connection to stabilize
    await asyncio.sleep(1)
    
    # Pick a random track
    track = random.choice(songs)
    
    if vc.is_playing():
        vc.stop()

    # 🛠️ THE FIX: Locate FFmpeg automatically on the server
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        # Check common Linux paths as a backup
        for path in ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
            if os.path.exists(path):
                ffmpeg_path = path
                break
    
    if not ffmpeg_path:
        return await ctx.send("⚠️ Error: FFmpeg is not installed on this server.")

    try:
        # Play using the specific FFmpeg path found
        source = discord.FFmpegPCMAudio(track, executable=ffmpeg_path)
        vc.play(source)
        await ctx.send(f"🎲 **Now playing:** {track}")
    except Exception as e:
        await ctx.send(f"⚠️ Audio Error: {str(e)}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected.")

# Safety check for the token
if not TOKEN:
    print("❌ FATAL: DISCORD_TOKEN variable is empty!")
else:
    bot.run(TOKEN)
