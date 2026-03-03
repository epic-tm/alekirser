import discord
from discord.ext import commands
import os
import random
import asyncio
import shutil # New import to find FFmpeg

TOKEN = os.getenv('DISCORD_TOKEN', '').strip()

intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True    

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def play(ctx):
    if not ctx.author.voice:
        return await ctx.send("🔊 Join a voice channel first!")

    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ No .m4a files found!")

    if ctx.voice_client is None:
        vc = await ctx.author.voice.channel.connect()
    else:
        vc = ctx.voice_client

    await asyncio.sleep(1)
    
    # 🛠️ FIND FFMPEG PATH
    ffmpeg_exe = shutil.which("ffmpeg")
    if not ffmpeg_exe:
        # Check common Linux locations if the system path fails
        for loc in ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
            if os.path.exists(loc):
                ffmpeg_exe = loc
                break

    if not ffmpeg_exe:
        return await ctx.send("⚠️ Error: FFmpeg is STILL not installed on this server.")

    track = random.choice(songs)
    try:
        # Use the specific path we found
        source = discord.FFmpegPCMAudio(track, executable=ffmpeg_exe)
        vc.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        await ctx.send(f"⚠️ Audio Error: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left.")

bot.run(TOKEN)
