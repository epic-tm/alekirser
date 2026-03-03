
import discord
from discord.ext import commands
import random
import asyncio
import shutil
import os

# Enable necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Check for FFmpeg installation
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        print(f'FFmpeg found at: {ffmpeg_path}')
    else:
        print('FFmpeg not found. Please ensure it is installed and in your system PATH.')

@bot.command()
async def play(ctx):
    if not ctx.message.author.voice:
        await ctx.send('You are not connected to a voice channel.')
        return

    channel = ctx.message.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
        await asyncio.sleep(1)  # 1-second delay after joining
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)
        await asyncio.sleep(1) # 1-second delay after moving

    voice_client = ctx.voice_client

    # Stop current playback if any
    if voice_client.is_playing():
        voice_client.stop()

    # Scan for .m4a files in the root directory
    m4a_files = [f for f in os.listdir('.') if f.endswith('.m4a')]

    if not m4a_files:
        await ctx.send('No .m4a files found in the current directory.')
        return

    # Pick one at random
    selected_file = random.choice(m4a_files)
    await ctx.send(f'Now playing: {selected_file}')

    try:
        source = discord.FFmpegPCMAudio(selected_file)
        voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
    except Exception as e:
        await ctx.send(f'An error occurred during playback: {e}')

@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('Playback stopped.')
    else:
        await ctx.send('Bot is not playing anything.')

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected from voice channel.')
    else:
        await ctx.send('Bot is not in a voice channel.')

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
# It's recommended to use environment variables for tokens in production
# bot.run(os.getenv('DISCORD_BOT_TOKEN'))
# For local testing, you can uncomment the line below and replace with your token
# bot.run('YOUR_BOT_TOKEN')
