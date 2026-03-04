import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import aiohttp
import os
import tempfile
import random
import logging
from dataclasses import dataclass, field
from collections import deque
from typing import Optional

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

GITHUB_REPO = "epic-tm/alekirser"
GITHUB_BRANCH = "main"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/contents"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


@dataclass
class Track:
    title: str
    filename: str
    requester: str


@dataclass
class GuildPlayer:
    queue: deque = field(default_factory=deque)
    current: Optional[Track] = None
    temp_dir: str = field(default_factory=lambda: tempfile.mkdtemp(prefix="m4a_"))


class M4ABot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.guild_players: dict[int, GuildPlayer] = {}

    async def setup_hook(self):
        await self.tree.sync()
        log.info("Slash commands synced globally.")

    def get_player(self, guild_id: int) -> GuildPlayer:
        if guild_id not in self.guild_players:
            self.guild_players[guild_id] = GuildPlayer()
        return self.guild_players[guild_id]

    async def fetch_m4a_files(self) -> list[dict]:
        """Fetch all .m4a files from root and music/ folder."""
        paths = ["", "music"]
        results = []
        async with aiohttp.ClientSession() as session:
            for path in paths:
                url = f"{GITHUB_API}/{path}?ref={GITHUB_BRANCH}" if path else f"{GITHUB_API}?ref={GITHUB_BRANCH}"
                async with session.get(url) as resp:
                    if resp.status == 404:
                        continue
                    resp.raise_for_status()
                    contents = await resp.json()
                for f in contents:
                    if f["name"].lower().endswith(".m4a"):
                        results.append({
                            "name": f["name"],
                            "raw_url": f"{GITHUB_RAW}/{path + '/' if path else ''}{f['name']}",
                        })
        return results

    async def download_file(self, url: str, dest: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                with open(dest, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024 * 64):
                        f.write(chunk)

    def play_next(self, guild: discord.Guild, error=None):
        if error:
            log.error(f"Playback error: {error}")
        asyncio.run_coroutine_threadsafe(self._advance_queue(guild), self.loop)

    async def _advance_queue(self, guild: discord.Guild):
        player = self.get_player(guild.id)

        if player.current and os.path.exists(player.current.filename):
            try:
                os.remove(player.current.filename)
            except OSError:
                pass

        player.current = None

        if not player.queue:
            return

        vc: discord.VoiceClient = guild.voice_client
        if not vc or not vc.is_connected():
            return

        track = player.queue.popleft()
        player.current = track

        try:
            source = discord.FFmpegPCMAudio(track.filename, **FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(source, volume=1.0)
            vc.play(source, after=lambda e: self.play_next(guild, e))
            log.info(f"Now playing: {track.title}")
        except Exception as e:
            log.error(f"Failed to play {track.title}: {e}")
            await self._advance_queue(guild)


bot = M4ABot()


async def ensure_voice(interaction: discord.Interaction) -> Optional[discord.VoiceClient]:
    member = interaction.user
    if not isinstance(member, discord.Member) or not member.voice or not member.voice.channel:
        await interaction.followup.send("❌ You must be in a voice channel.", ephemeral=True)
        return None
    vc = interaction.guild.voice_client
    if vc and vc.channel != member.voice.channel:
        await vc.move_to(member.voice.channel)
    elif not vc:
        vc = await member.voice.channel.connect()
    return vc


@bot.tree.command(name="alekirser", description="Play a random m4a from the repo")
async def alekirser(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        files = await bot.fetch_m4a_files()
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to fetch files: {e}")
        return

    if not files:
        await interaction.followup.send("❌ No `.m4a` files found.")
        return

    chosen = random.choice(files)
    vc = await ensure_voice(interaction)
    if not vc:
        return

    player = bot.get_player(interaction.guild_id)
    dest = os.path.join(player.temp_dir, chosen["name"])

    await interaction.followup.send(f"⬇️ Loading **{chosen['name']}**…")

    try:
        await bot.download_file(chosen["raw_url"], dest)
    except Exception as e:
        await interaction.followup.send(f"❌ Download failed: {e}")
        return

    track = Track(title=chosen["name"], filename=dest, requester=interaction.user.display_name)

    if vc.is_playing() or vc.is_paused():
        player.queue.append(track)
        await interaction.followup.send(f"📋 Queued: **{track.title}**")
    else:
        player.queue.appendleft(track)
        await bot._advance_queue(interaction.guild)
        await interaction.followup.send(f"🎲 Now playing: **{track.title}**")


@bot.tree.command(name="skip", description="Skip the current track")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_playing():
        await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)
        return
    vc.stop()
    await interaction.response.send_message("⏭️ Skipped.")


@bot.tree.command(name="stop", description="Stop playback and clear the queue")
async def stop(interaction: discord.Interaction):
    bot.get_player(interaction.guild_id).queue.clear()
    vc = interaction.guild.voice_client
    if vc:
        vc.stop()
    await interaction.response.send_message("⏹️ Stopped and queue cleared.")


@bot.tree.command(name="pause", description="Pause playback")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸️ Paused.")
    else:
        await interaction.response.send_message("❌ Nothing to pause.", ephemeral=True)


@bot.tree.command(name="resume", description="Resume paused playback")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶️ Resumed.")
    else:
        await interaction.response.send_message("❌ Not paused.", ephemeral=True)


@bot.tree.command(name="queue", description="Show the current queue")
async def queue_cmd(interaction: discord.Interaction):
    player = bot.get_player(interaction.guild_id)
    lines = []
    if player.current:
        lines.append(f"▶️ **Now playing:** {player.current.title}")
    if player.queue:
        lines.append("**Up next:**")
        for i, t in enumerate(player.queue, 1):
            lines.append(f"  {i}. {t.title} — {t.requester}")
    if not lines:
        await interaction.response.send_message("📭 Queue is empty.")
    else:
        await interaction.response.send_message("\n".join(lines))


@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    bot.get_player(interaction.guild_id).queue.clear()
    vc = interaction.guild.voice_client
    if vc:
        await vc.disconnect()
        await interaction.response.send_message("👋 Left.")
    else:
        await interaction.response.send_message("❌ Not in a voice channel.", ephemeral=True)


@bot.command(name="sync", hidden=True)
@commands.is_owner()
async def sync(ctx: commands.Context):
    synced = await bot.tree.sync()
    await ctx.send(f"✅ Synced {len(synced)} commands.")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
