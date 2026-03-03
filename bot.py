import discord
from discord.ext import commands
import os
import random
import asyncio

# --- Configuration ---
TOKEN = 'DISCORD_TOKEN'
MUSIC_FOLDER = './music'  # The folder containing your .m4a files
COMMAND_PREFIX = '!'

# Define intents (required for modern Discord bots)
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def play(ctx):
    """Joins voice and plays a random .m4a file from the local folder."""
    
    # 1. Check if the user is in a voice channel
    if not ctx.author.voice:
        return await ctx.send("You need to be in a voice channel to use this command!")

    channel = ctx.author.voice.channel

    # 2. Get a list of all .m4a files in the folder
    files = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith('.m4a')]
    
    if not files:
        return await ctx.send(f"No .m4a files found in `{MUSIC_FOLDER}`.")

    # 3. Pick a random file
    random_file = random.choice(files)
    file_path = os.path.join(MUSIC_FOLDER, random_file)

    # 4. Connect to voice and play
    try:
        vc = await channel.connect()
        await ctx.send(f"Now playing: **{random_file}**")

        # Play the audio using FFmpeg
        vc.play(discord.FFmpegPCMAudio(file_path), after=lambda e: print(f'Finished playing: {e}' if e else 'Finished playing.'))

        # 5. Wait for the audio to finish before disconnecting
        while vc.is_playing():
            await asyncio.sleep(1)
        
        await vc.disconnect()

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

@bot.command()
async def stop(ctx):
    """Stops the bot and makes it leave the channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected.")
    else:
        await ctx.send("I'm not in a voice channel.")

bot.run(TOKEN)
