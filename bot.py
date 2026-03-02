import discord
from discord.ext import commands
import yt_dlp
import requests
from bs4 import BeautifulSoup
import random
import os
import asyncio

# --- CONFIG ---
TOKEN = os.getenv('DISCORD_TOKEN')

# Standard audio options
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_flaru_links(query):
    """Scrapes flaru.com for a list of playable links"""
    search_url = f"https://flaru.com/en/search/?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'} # Pretend to be a browser
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Flaru search results usually contain links to soundgasm or soundcloud
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'soundgasm.net' in href or 'soundcloud.com' in href:
            links.append(href)
    return links

@bot.event
async def on_ready():
    print(f'✅ Flaru Scraper Bot is online as {bot.user}')

@bot.command()
async def play(ctx):
    """Force searches Flaru for Alekirser and picks a random result"""
    if not ctx.author.voice:
        return await ctx.send("🔊 Join a voice channel first!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        try:
            # Step 1: Get links specifically from Flaru search
            links = get_flaru_links("alekirser")
            
            if not links:
                return await ctx.send("🔍 Flaru didn't show any results for Alekirser right now.")

            # Step 2: Pick a random one
            target_url = random.choice(links)

            # Step 3: Extract the actual audio stream using yt-dlp
            with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
                info = ydl.extract_info(target_url, download=False)
                audio_url = info['url']
                title = info.get('title', 'Alekirser Track')

            # Step 4: Play
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()

            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source)
            await ctx.send(f"🎲 **Random Alekirser from Flaru:** {title}")

        except Exception as e:
            await ctx.send(f"⚠️ Error: {str(e)}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)import discord
from discord.ext import commands
import yt_dlp
import random
import os
import asyncio

# Pulls your token from the 'Variables' tab on your host
TOKEN = os.getenv('DISCORD_TOKEN')

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extract_flat': True,
    # This part helps bypass Cloudflare protection
    'extractor_args': {'generic': {'impersonate': ['chrome']}}, 
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🚀 {bot.user} is now LIVE and searching Flaru!')

@bot.command()
async def play(ctx):
    """Searches Flaru for alekirser and plays a random result"""
    if not ctx.author.voice:
        return await ctx.send("🔊 You need to be in a Voice Channel first!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        try:
            # Direct search on Flaru for alekirser
            search_url = "https://flaru.com/en/search/?q=alekirser"
            
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(search_url, download=False)
                tracks = info.get('entries', [])

            if not tracks:
                return await ctx.send("❌ No tracks found for alekirser on Flaru.")

            # Choose a random track from the search results
            track = random.choice(tracks)
            
            # Deep-extract the actual audio stream
            with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl_final:
                final_info = ydl_final.extract_info(track['url'], download=False)
                audio_url = final_info['url']
                title = final_info.get('title', 'Alekirser Track')

            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()

            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source)
            
            await ctx.send(f"🎲 **Random Alekirser (via Flaru):** {title}")

        except Exception as e:
            await ctx.send(f"⚠️ Technical Error: {str(e)}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
