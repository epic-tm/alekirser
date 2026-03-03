import discord
from discord.ext import commands
import os
import random

# Your secret token from Railway/Render
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is online and ready to shuffle your files!')

@bot.command()
async def play(ctx):
    """Picks a random .m4a file from the folder and plays it"""
    if not ctx.author.voice:
        return await ctx.send("🔊 Please join a voice channel first!")

    # 1. Scan the folder for any file ending in .m4a
    m4a_files = [f for f in os.listdir('.') if f.endswith('.m4a')]

    if not m4a_files:
        return await ctx.send("❌ I couldn't find any .m4a files in my folder!")

    # 2. Join the voice channel
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    # 3. Select a random track
    chosen_file = random.choice(m4a_files)

    # 4. Stop current audio and play the new random track
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    try:
        # Playing the local file using FFmpeg
        source = discord.FFmpegPCMAudio(chosen_file)
        ctx.voice_client.play(source)
        await ctx.send(f"🎲 **Random Pick:** {chosen_file}")
    except Exception as e:
        await ctx.send(f"⚠️ Error playing file: {e}")

@bot.command()
async def stop(ctx):
    """Leaves the voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected.")

bot.run(TOKEN)
