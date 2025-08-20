import discord
import yt_dlp
import asyncio
from discord.ext import commands
from discord import app_commands
from collections import deque

SONG_QUEUES = {}

async def search_ytdlp_async(query, ydl_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_opts))

def _extract(query, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @app_commands.command(name="play", description="Play a song or add it to the queue.")
    @app_commands.describe(song_query="Search query or URL")
    async def play(self, interaction: discord.Interaction, song_query: str):
        await interaction.response.defer()

        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.followup.send("You must be in a voice channel.")

        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_channel != voice_client.channel:
            await voice_client.move_to(voice_channel)

        ydl_options = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "youtube_include_dash_manifest": False,
            "youtube_include_hls_manifest": False,
        }

        query = "ytsearch1: " + song_query
        results = await search_ytdlp_async(query, ydl_options)
        tracks = results.get("entries", [])

        if not tracks:
            return await interaction.followup.send("No results found.")

        first_track = tracks[0]
        audio_url = first_track["url"]
        title = first_track.get("title", "Untitled")

        guild_id = str(interaction.guild_id)
        if SONG_QUEUES.get(guild_id) is None:
            SONG_QUEUES[guild_id] = deque()

        SONG_QUEUES[guild_id].append((audio_url, title))

        if voice_client.is_playing() or voice_client.is_paused():
            await interaction.followup.send(f"Added to queue: **{title}**")
        else:
            await interaction.followup.send(f"Now playing: **{title}**")
            await self.play_next_song(voice_client, guild_id, interaction.channel)

    async def play_next_song(self, voice_client, guild_id, channel):
        if SONG_QUEUES[guild_id]:
            audio_url, title = SONG_QUEUES[guild_id].popleft()

            ffmpeg_options = {
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn -c:a libopus -b:a 96k",
            }

            source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options)

            def after_play(error):
                if error:
                    print(f"Error playing {title}: {error}")
                fut = self.play_next_song(voice_client, guild_id, channel)
                asyncio.run_coroutine_threadsafe(fut, self.bot.loop)

            voice_client.play(source, after=after_play)
            await channel.send(f"Now playing: **{title}**")
        else:
            await voice_client.disconnect()
            SONG_QUEUES[guild_id] = deque()

    
    @app_commands.command(name="skip", description="Skips the current playing song")
    async def skip(self, interaction: discord.Interaction):
        if interaction.guild.voice_client and (
            interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused()
        ):
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("Skipped the current song.")
        else:
            await interaction.response.send_message("Not playing anything to skip.")

    
    @app_commands.command(name="pause", description="Pause the currently playing song.")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            return await interaction.response.send_message("I'm not in a voice channel.")

        if not voice_client.is_playing():
            return await interaction.response.send_message("Nothing is currently playing to pause.")

        voice_client.pause()
        await interaction.response.send_message("Playback paused!")

    
    @app_commands.command(name="resume", description="Resume the currently paused song.")
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            return await interaction.response.send_message("I'm not in a voice channel.")

        if not voice_client.is_paused():
            return await interaction.response.send_message("I'm not paused right now.")

        voice_client.resume()
        await interaction.response.send_message("Playback resumed!")

    
    @app_commands.command(name="stop", description="Stop the song and clear the queue")
    async def stop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_id_str = str(interaction.guild_id)

        if interaction.guild.voice_client:
            if guild_id_str in SONG_QUEUES:
                SONG_QUEUES[guild_id_str].clear()

            interaction.guild.voice_client.stop()
            await interaction.followup.send("Playback stopped and queue cleared.")
        else:
            await interaction.followup.send("No song is currently playing.")

async def setup(bot):
    await bot.add_cog(Music(bot))
