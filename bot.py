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
    print(f'✅ Bot is online: {bot.user}')

@bot.command()
async def play(ctx):
    if not ctx.author.voice:
        return await ctx.send("🔊 Join a voice channel first!")

    # Find .m4a files
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ No .m4a files found in the folder!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    await asyncio.sleep(1)
    
    # 🔍 AUTO-FIND FFMPEG ON THE SERVER
    ffmpeg_exe = shutil.which("ffmpeg")
    if not ffmpeg_exe:
        # Check specific paths where Railway/Nix often hides it
        possible_paths = ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/nix/var/nix/profiles/default/bin/ffmpeg"]
        for path in possible_paths:
            if os.path.exists(path):
                ffmpeg_exe = path
                break

    track = random.choice(songs)
    try:
        # If we found a path, use it; otherwise try the system default 'ffmpeg'
        source = discord.FFmpegPCMAudio(track, executable=ffmpeg_exe or "ffmpeg")
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        await ctx.send(f"⚠️ Audio Error: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left.")

bot.run(TOKEN)
