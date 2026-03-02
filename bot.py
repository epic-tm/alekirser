import discord
from discord.ext import commands
import yt_dlp
import requests
from bs4 import BeautifulSoup
import random
import os

# Your Secret Token from Railway/Host
TOKEN = os.getenv('DISCORD_TOKEN')

# Reconnection settings for smooth audio
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

# The fix for the 403 error in your screenshot
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    # This impersonates Chrome to get past Cloudflare
    'extractor_args': {'generic': {'impersonate': ['chrome']}}, 
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_alekirser_tracks():
    """Scrapes the specific alekirser profile on Flaru"""
    url = "https://www.flaru.com/en/soundgasm.net/alekirser"
    # We also use a browser header here for the scraper
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'soundgasm.net/u/alekirser/' in href:
                links.append(href)
        
        return list(set(links))
    except Exception as e:
        print(f"Scrape error: {e}")
        return []

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')

@bot.command()
async def play(ctx):
    """Picks a random track from the Alekirser Flaru page"""
    if not ctx.author.voice:
        return await ctx.send("🔊 You need to be in a Voice Channel first!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        tracks = get_alekirser_tracks()
        
        if not tracks:
            return await ctx.send("🔍 Still blocked by Cloudflare or no tracks found. Try again!")

        chosen_track = random.choice(tracks)

        # We apply the impersonation here too
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(chosen_track, download=False)
                audio_url = info['url']
                title = info.get('title', 'Alekirser Audio')

                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()

                source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source)
                await ctx.send(f"🎲 **Now Playing:** {title}")
            except Exception as e:
                await ctx.send(f"⚠️ Track failed to load: {str(e)}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
