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
    # 🔍 This will tell us EXACTLY where FFmpeg is in your logs
    path = shutil.which("ffmpeg")
    print(f'✅ Bot Online: {bot.user}')
    print(f'🛠️ FFmpeg Detection: {"FOUND at " + path if path else "STILL MISSING"}')

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
    
    # 🕵️‍♂️ Manual Search for the FFmpeg "Engine"
    executable = shutil.which("ffmpeg")
    if not executable:
        # Check specific paths where Railway/Nix builds store software
        for loc in ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/nix/var/nix/profiles/default/bin/ffmpeg"]:
            if os.path.exists(loc):
                executable = loc
                break

    track = random.choice(songs)
    try:
        # We tell Discord exactly where the engine is
        source = discord.FFmpegPCMAudio(track, executable=executable or "ffmpeg")
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        await ctx.send(f"⚠️ Audio Error: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
