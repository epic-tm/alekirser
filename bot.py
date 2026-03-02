import discord
from discord.ext import commands
import yt_dlp
import asyncio
import random
import os

# --- SETUP ---
TOKEN = os.getenv('DISCORD_TOKEN')

# Options to make the audio stream smoothly in Discord
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

# This tells the bot to look at Flaru's search page specifically
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extract_flat': True, # Fast search
    'force_generic_extractor': True,
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🚀 Bot is running: {bot.user}')

@bot.command()
async def play(ctx):
    """Searches Flaru for alekirser and plays a random result"""
    if not ctx.author.voice:
        return await ctx.send("🔊 You need to be in a Voice Channel first!")

    # Join Voice
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        try:
            # We target the Flaru search URL directly
            flaru_url = "https://flaru.com/en/search/?q=alekirser"
            
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                # Scrape the Flaru page for links
                info = ydl.extract_info(flaru_url, download=False)
                
                # Flaru search results appear as 'entries'
                tracks = info.get('entries', [])

            if not tracks:
                return await ctx.send("❌ Flaru didn't return any alekirser tracks.")

            # Pick a random track from the results
            track = random.choice(tracks)
            
            # Since Flaru links to other sites, we need to extract the final audio URL
            with yt_dlp.YoutubeDL({'format': 'bestaudio'}) as ydl_final:
                final_info = ydl_final.extract_info(track['url'], download=False)
                audio_url = final_info['url']
                title = final_info.get('title', 'Alekirser Track')

            # Play the audio
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()

            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source)
            
            await ctx.send(f"🎲 **Flaru Random Pick:** {title}")

        except Exception as e:
            await ctx.send(f"⚠️ Technical Error: {e}")

@bot.command()
async def stop(ctx):
    """Leaves the voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)import discord
from discord.ext import commands
import yt_dlp
import asyncio
import random
import os

# --- CONFIGURATION ---
# We pull the token from the server environment instead of typing it here
TOKEN = os.getenv('DISCORD_TOKEN')

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
