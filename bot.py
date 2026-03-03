import discord
from discord.ext import commands
import os
import random
import asyncio

# Clean the token for any accidental spaces
TOKEN = os.getenv('DISCORD_TOKEN', '').strip()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online and ready!')
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    print(f'📂 Local tracks found: {songs}')

@bot.command()
async def play(ctx):
    if not ctx.author.voice:
        return await ctx.send("🔊 Please join a voice channel first!")

    # Find all m4a files in the current folder
    songs = [f for f in os.listdir('.') if f.endswith('.m4a')]
    if not songs:
        return await ctx.send("❌ I couldn't find any .m4a files in my folder!")

    # Connect to Voice
    if ctx.voice_client is None:
        vc = await ctx.author.voice.channel.connect()
    else:
        vc = ctx.voice_client

    # IMPORTANT: Wait 1 second so Discord can initialize the audio stream
    await asyncio.sleep(1)

    track = random.choice(songs)
    
    if vc.is_playing():
        vc.stop()

    try:
        # FFMPEG options to handle stream stability
        ffmpeg_opts = {'options': '-vn', 'before_options': '-reconnect 1 -reconnect_delay_max 5'}
        
        # Load the file and boost volume to 80%
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track, **ffmpeg_opts), volume=0.8)
        
        vc.play(source)
        await ctx.send(f"🎲 **Now Playing:** {track}")
    except Exception as e:
        await ctx.send(f"⚠️ Audio Error: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected.")

bot.run(TOKEN)
