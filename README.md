# Ailema Bot for Discord  

#### Video Demo: <[URL HERE](https://www.youtube.com/watch?v=TjTTKV86w_0)>  

#### Description:  
The **Ailema Bot** is a multifunctional Discord bot that includes music features, creation of scoreboards between players with saved results, and a system to display Bible verses, as well as keyword search in the Bible.  

---

## Why did I build Ailema?  

Throughout my journey as a Discord user, I have used several different bots with various functions. However, there was never a bot that fully met my needs. Because of this, I always had to invite more than one bot to my server to achieve my goals.  

From this problem, **Ailema was born**. Ailema combines three things I needed for my server: music, scoreboards to keep track of 1v1 matches with my friends, and the Bible.  

---

## What does Ailema do?  

The **Ailema Bot** was developed to be a multifunctional assistant inside Discord servers.  
It brings together three main categories of features: **Music**, **Bible**, and **Duels**.  
Each set of commands was implemented in a separate *cog*, which ensures modularity, facilitates code maintenance, and allows future expansion without compromising current functionality.  

---

### Music Commands  

The music commands allow any voice channel to become a space for entertainment.  
The bot uses `yt-dlp` to fetch songs from YouTube and FFmpeg to stream audio in real time.  

- `/play <term or URL>` — plays a YouTube song or adds it to the queue if one is already playing.  
- `/pause` — pauses the current playback without losing its position.  
- `/resume` — resumes the paused song exactly where it stopped.  
- `/skip` — skips the current track and plays the next one in the queue.  
- `/stop` — completely stops playback and clears the music queue.  

---

### Bible Commands  

The Bible commands make Ailema Bot a useful tool for servers that want to share, study, or discuss biblical texts directly in Discord. Ailema uses the public [Bible API](https://bible-api.com).  

- `/verse <reference> [version]` — shows a specific Bible verse or passage.  
  Example: `/verse John 3:16 kjv` returns the verse in the King James Version.  
- `/search <keyword> [version] [limit]` — searches for verses containing a specific word.  
  Example: `/search love kjv 5` returns up to 5 verses that contain the word “love.”  

---

### Duel Commands  

The duel system allows the creation of custom scoreboards for any game — from chess matches to casual competitions among friends.  
The data is saved in `duels.json`, ensuring that results are not lost even after the bot is restarted.  

- `/duel create <title> <player1> <player2>` — creates a scoreboard between two players.  
- `/duel point <title> <winner>` — adds a point to the winning player.  
- `/duel score <title>` — shows the current score of the game.  
- `/duel end <title>` — ends and removes the scoreboard.  
- `/duel list` — lists all active scoreboards in the server.  

A unique feature of this system is the use of playful phrases stored in `phrases.txt`.  
Every time a point is scored, the bot sends a random fun phrase in the chat.  

---

## Complexity  

Ailema Bot is more than just a simple music bot. It demonstrates distinct complexity in several areas:  

1. **Multiple Features in One Bot** — Most Discord bots specialize in a single task. Ailema integrates three very different systems (music, Bible, and duels) into a single application.  
2. **Asynchronous Programming** — Music playback uses async functions and background callbacks to ensure that queues continue smoothly without blocking the bot.  
3. **External API Integration** — The Bible Cog connects to the Bible API and parses JSON responses dynamically.  
4. **Persistent Storage** — Duel results are saved to `duels.json`, ensuring data is not lost even when the bot restarts.  
5. **Modular Architecture** — Features are separated into independent *cogs*, which makes the code more maintainable and expandable.  

This combination makes Ailema Bot distinct from ordinary tutorial bots and highlights real-world programming skills.  

---

## Installation & Usage  

To run Ailema Bot on your own machine, follow these steps:  

1. **Install Python** (3.10 or higher recommended).  
2. **Install FFmpeg** and make sure it is available in your system’s PATH.  
3. **Clone this repository**:  
   ```bash
   git clone <repo_url>
   cd ailema-bot

4. Create a .env file in the project folder and add your Discord bot token:

`DISCORD_TOKEN=your_token_here`


5. Install dependencies listed in requirements.txt:

```pip install -r requirements.txt```


6. Run the bot:

```python ailema.py```

Once the bot is running, invite it to your Discord server using the OAuth2 link from the Discord Developer Portal. You can then use the commands described above directly in your server.

## References  

- [discord.py Documentation](https://discordpy.readthedocs.io/)  
- [yt-dlp GitHub Repository](https://github.com/yt-dlp/yt-dlp)  
- [FFmpeg Official Site](https://ffmpeg.org/)  
- [Bible API](https://bible-api.com)  
- [Python Asyncio Documentation](https://docs.python.org/3/library/asyncio.html) 