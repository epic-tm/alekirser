import discord
from discord.ext import commands
import os
import random
import asyncio

# --- CONFIG ---
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
    """Simple play command for local m4a files"""
    if not ctx.author.voice:
        return await ctx.send("🔊 Join a Voice Channel first!")

    # Find local tracks
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ No .m4a files found in the folder!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    await asyncio.sleep(1) # Let the connection settle
    track = random.choice(songs)
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    try:
        # We don't specify the path here; we let the system find 'ffmpeg'
        source = discord.FFmpegPCMAudio(track)
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        # This is the error you keep seeing in your screenshots
        await ctx.send(f"⚠️ Audio Error: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
