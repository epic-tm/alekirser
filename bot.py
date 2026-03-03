import discord
from discord.ext import commands
import os
import random
import asyncio

# 1. Clean Token Load
TOKEN = os.getenv('DISCORD_TOKEN', '').strip()

# 2. Setup Intents
intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True    

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is online: {bot.user}')

@bot.command()
async def play(ctx):
    """Joins voice and plays a random m4a file"""
    if not ctx.author.voice:
        return await ctx.send("🔊 Please join a voice channel first!")

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
    
    track = random.choice(songs)
    
    if vc.is_playing():
        vc.stop()

    try:
        # Standard playback - Railway will find ffmpeg because of the build command
        source = discord.FFmpegPCMAudio(track)
        vc.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        await ctx.send(f"⚠️ Audio Error: {str(e)}")

@bot.command()
async def stop(ctx):
    """Stops and leaves"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel.")

bot.run(TOKEN)
