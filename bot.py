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

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} is online!')

@bot.command()
async def play(ctx):
    if not ctx.author.voice:
        return await ctx.send("🔊 Join a Voice Channel first!")

    # Get local files
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ No .m4a files found in the folder!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    await asyncio.sleep(1)
    track = random.choice(songs)
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    # THE CRITICAL FIX: Manually find FFmpeg path
    ffmpeg_exe = shutil.which("ffmpeg")
    if not ffmpeg_exe:
        # Check common Linux server locations
        for loc in ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/nix/store/*/bin/ffmpeg"]:
            if os.path.exists(loc):
                ffmpeg_exe = loc
                break

    if not ffmpeg_exe:
        return await ctx.send("⚠️ Error: FFmpeg is still not installed on this server.")

    try:
        source = discord.FFmpegPCMAudio(track, executable=ffmpeg_exe)
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        await ctx.send(f"⚠️ Audio Error: {e}")

bot.run(TOKEN)
