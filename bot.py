import discord
from discord.ext import commands
import os
import random

# 1. Grab the token and clean it (removes invisible spaces/newlines)
RAW_TOKEN = os.getenv('DISCORD_TOKEN')
TOKEN = RAW_TOKEN.strip() if RAW_TOKEN else None

# 2. Setup Intents (Crucial for 2026 bots)
intents = discord.Intents.default()
intents.message_content = True  # Allows bot to see "!play"
intents.voice_states = True     # Allows bot to join Voice Channels

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Success! {bot.user.name} is online.')
    # List files to verify they are in the right spot
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    print(f'📂 Found {len(songs)} .m4a files: {songs}')

@bot.command()
async def play(ctx):
    """Plays a random m4a file from the local folder"""
    if not ctx.author.voice:
        return await ctx.send("🔊 You need to be in a voice channel first!")

    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ Error: No .m4a files found in the bot's folder!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()
    
    track = random.choice(songs)
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    # Play local file
    ctx.voice_client.play(discord.FFmpegPCMAudio(track))
    await ctx.send(f"🎶 **Now playing:** {track}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel.")

# --- SAFE START ---
if not TOKEN:
    print("❌ FATAL ERROR: DISCORD_TOKEN is missing from your environment variables!")
else:
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ FATAL ERROR: The token is invalid. Reset it in the Developer Portal.")
