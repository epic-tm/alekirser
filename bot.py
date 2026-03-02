import discord
from discord.ext import commands
import yt_dlp
import asyncio
import random
import os

# --- CONFIGURATION ---
# We pull the token from the server environment instead of typing it here
TOKEN = os.getenv('ODA5MDUyNjc0NjMyODQzMjgz.G7n9G0.7uk9jt5Jdi01BiCja80IwyMDh9XIe4QB7JjMMk')

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch10', # Searches for top 10 results
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')

@bot.command()
async def play(ctx):
    """Plays a random alekirser track"""
    if not ctx.author.voice:
        return await ctx.send("❌ You need to be in a voice channel first!")

    # Connect to voice
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()
    elif ctx.voice_client.channel != ctx.author.voice.channel:
        await ctx.voice_client.move_to(ctx.author.voice.channel)

    async with ctx.typing():
        try:
            # Force search for alekirser
            search_query = "alekirser"
            
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                # Get 10 results to pick a random one
                info = ydl.extract_info(f"ytsearch10:{search_query}", download=False)
                tracks = info.get('entries', [])

            if not tracks:
                return await ctx.send("🔍 Couldn't find any alekirser tracks.")

            # Pick a random one
            track = random.choice(tracks)
            url = track['url']
            title = track.get('title', 'Unknown Track')

            # Stop current music if playing
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()

            # Play the audio
            source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source)
            
            await ctx.send(f"🎲 **Random alekirser Pick:** {title}")

        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {str(e)}")

@bot.command()
async def stop(ctx):
    """Stops the music and leaves"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected.")

bot.run(TOKEN)
