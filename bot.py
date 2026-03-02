import discord
from discord.ext import commands
import yt_dlp
import random
import os
import asyncio

# --- SETUP ---
# Ensure you have 'DISCORD_TOKEN' set in your hosting Variables!
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
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🚀 Bot is online as {bot.user}')

@bot.command()
async def play(ctx):
    """Searches Flaru for alekirser and plays a random result"""
    if not ctx.author.voice:
        return await ctx.send("🔊 You need to be in a Voice Channel first!")

    # Join Voice if not already connected
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        try:
            # Flaru search URL for alekirser
            search_url = "https://flaru.com/en/search/?q=alekirser"
            
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(search_url, download=False)
                tracks = info.get('entries', [])

            if not tracks:
                return await ctx.send("❌ No tracks found for alekirser on Flaru.")

            # Pick a random track
            track = random.choice(tracks)
            
            # Get the final audio URL
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
            await ctx.send(f"⚠️ Error: {str(e)}")

@bot.command()
async def stop(ctx):
    """Leaves the voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Bye!")

# THIS MUST BE THE VERY LAST LINE
bot.run(TOKEN)
