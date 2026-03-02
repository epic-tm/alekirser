import discord
from discord.ext import commands
import yt_dlp
import requests
from bs4 import BeautifulSoup
import random
import os

TOKEN = os.getenv('DISCORD_TOKEN')

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_alekirser_tracks():
    """Scrapes the specific alekirser profile on Flaru"""
    # Using your suggested URL
    url = "https://www.flaru.com/en/soundgasm.net/alekirser"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # On this specific page, we look for all links that go to soundgasm
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'soundgasm.net/u/alekirser/' in href:
                links.append(href)
        
        # Remove duplicates
        return list(set(links))
    except Exception as e:
        print(f"Scrape error: {e}")
        return []

@bot.command()
async def play(ctx):
    """Picks a random track from the alekirser soundgasm list on Flaru"""
    if not ctx.author.voice:
        return await ctx.send("🔊 You need to be in a Voice Channel first!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        # Get the list from the specific page
        tracks = get_alekirser_tracks()
        
        if not tracks:
            return await ctx.send("🔍 Couldn't find any tracks on that page. Try again in a moment!")

        # Pick a random one
        chosen_track = random.choice(tracks)

        # Extract the audio using yt-dlp
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
            try:
                info = ydl.extract_info(chosen_track, download=False)
                audio_url = info['url']
                title = info.get('title', 'Alekirser Audio')

                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()

                source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source)
                await ctx.send(f"🎲 **Playing Random Alekirser:** {title}")
            except:
                await ctx.send("⚠️ This specific track failed to load. Try `!play` again for a new one!")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
