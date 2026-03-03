import discord
from discord.ext import commands
import os
import random
import asyncio

# 1. Get Token
TOKEN = os.getenv('DISCORD_TOKEN', '').strip()

# 2. Setup Intents
intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True    

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.command()
async def play(ctx):
    # Check if user is in voice
    if not ctx.author.voice:
        return await ctx.send("🔊 Please join a voice channel first!")

    # Find .m4a files in the same folder as this script
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ No .m4a files found in the bot folder!")

    # Join Voice
    if ctx.voice_client is None:
        vc = await ctx.author.voice.channel.connect()
    else:
        vc = ctx.voice_client

    # Pick a random song
    track = random.choice(songs)
    
    if vc.is_playing():
        vc.stop()

    try:
        # Standard playback
        source = discord.FFmpegPCMAudio(track)
        vc.play(source)
        await ctx.send(f"🎶 **Now playing:** {track}")
    except Exception as e:
        # This will tell us if FFmpeg is still missing
        await ctx.send(f"⚠️ Error: {e}")

bot.run(TOKEN)
