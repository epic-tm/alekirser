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

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_flaru_links(query):
    """Scrapes flaru.com for alekirser links"""
    search_url = f"https://flaru.com/en/search/?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'} 
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We look for links that Flaru usually indexes (Soundgasm, etc)
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'soundgasm.net' in href or 'soundcloud.com' in href:
                links.append(href)
        return links
    except Exception as e:
        print(f"Scrape error: {e}")
        return []

@bot.event
async def on_ready():
    print(f'✅ Bot is live: {bot.user}')

@bot.command()
async def play(ctx):
    """Plays a random alekirser track found on Flaru"""
    if not ctx.author.voice:
        return await ctx.send("🔊 Join a voice channel first!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        links = get_flaru_links("alekirser")
        
        if not links:
            return await ctx.send("🔍 No Alekirser tracks found on Flaru right now.")

        # Pick one at random
        target_url = random.choice(links)

        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
            info = ydl.extract_info(target_url, download=False)
            audio_url = info['url']
            title = info.get('title', 'Alekirser Track')

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        ctx.voice_client.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
        await ctx.send(f"🎲 **Random Pick from Flaru:** {title}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

# THIS MUST BE THE ABSOLUTE LAST LINE. 
# DO NOT ADD ANYTHING AFTER THIS.
bot.run(TOKEN)
