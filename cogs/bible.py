import aiohttp
import discord
import urllib.parse
from discord.ext import commands
from discord import app_commands
from typing import Optional

API = "https://bible-api.com"
DEFAULT_TRANSLATION = "kjv"   

class Bible(commands.Cog):
    

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    async def _get(self, passage: str, translation: str):
        assert self.session is not None
        q = urllib.parse.quote_plus(passage.strip())
        url = f"{API}/{q}?translation={translation}"
        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            return None

    
    @app_commands.command(name="verse", description="Shows a Bible verse or passage")
    @app_commands.describe(reference="Example: John 3:16, Romans 8:28-30, Psalm 23",version="Example: kjv, almeida, web (default kjv)")
    async def verse(self, interaction: discord.Interaction, reference: str, version: Optional[str] = None):
        await interaction.response.defer()
        translation = (version or DEFAULT_TRANSLATION).lower()

        data = await self._get(reference, translation)
        if not data or not data.get("text"):
            return await interaction.followup.send(f"Could not find `{reference}` ({translation}).")

        text = data["text"].strip()
        ref = data.get("reference", reference)

        if len(text) > 4000:
            text = text[:3999] + "…"

        embed = discord.Embed(title=ref, description=text, color=0x2b6cb0)
        embed.set_footer(text=f"Version: {translation}")
        await interaction.followup.send(embed=embed)

    
    @app_commands.command(name="search", description="Search verses by keyword (simple scan).")
    @app_commands.describe(term="Keyword to search (e.g., love, faith, grace)",version="Bible version (default kjv)",limit="Number of results (1-10, default 5)")
    async def search(self, interaction: discord.Interaction, term: str, version: Optional[str] = None, limit: int = 5):
        await interaction.response.defer()
        translation = (version or DEFAULT_TRANSLATION).lower()
        limit = max(1, min(limit, 10))

        
        sample_books = ["John 3", "Romans 8", "1 Corinthians 13", "Psalms 23", "Genesis 1, Ephesias 2", "Hebrews 11"]
        results = []

        for book in sample_books:
            data = await self._get(book, translation)
            if not data or "verses" not in data:
                continue
            for v in data["verses"]:
                text = v.get("text", "").strip()
                if term.lower() in text.lower():
                    ref = f"{v.get('book_name')} {v.get('chapter')}:{v.get('verse')}"
                    results.append((ref, text))
                    if len(results) >= limit:
                        break
            if len(results) >= limit:
                break

        if not results:
            return await interaction.followup.send(f"No results for **{term}** in {translation}.")

        lines = [f"**{ref}** — {text[:200]}{'…' if len(text) > 200 else ''}" for ref, text in results]

        embed = discord.Embed(title=f"Search: {term}", description="\n".join(lines), color=0x38a169)
        embed.set_footer(text=f"Version: {translation}")
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Bible(bot))
