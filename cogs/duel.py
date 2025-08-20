import discord
from discord.ext import commands
from discord import app_commands
import json, os, random

DATA_FILE = "duels.json"
PHRASES_FILE = "phrases.txt"

def load_json():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_phrases():
    if os.path.exists(PHRASES_FILE):
        with open(PHRASES_FILE, "r", encoding="utf-8") as f:
            phrases = [l.strip() for l in f if l.strip()]
            if phrases:
                return phrases
    return ["Another one for the scoreboard!"]

class DuelCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data = load_json()

    def _g(self, guild_id: int):
        gid = str(guild_id)
        if gid not in self.data:
            self.data[gid] = {}
        return self.data[gid]

    def _key(self, title: str):
        return title.strip().lower()

    duel = app_commands.Group(name="duel", description="Manage duels with scoreboards per game.")

    @duel.command(name="create", description="Create a new scoreboard for a game between two players.")
    @app_commands.describe(
        title="Game title",
        player1="First player",
        player2="Second player"
    )
    async def create(
        self,
        interaction: discord.Interaction,
        title: str,
        player1: discord.Member,
        player2: discord.Member
    ):
        await interaction.response.defer(thinking=False, ephemeral=False)
        games = self._g(interaction.guild_id)
        k = self._key(title)
        if k in games:
            await interaction.followup.send(f"❌ A scoreboard for **{title}** already exists.")
            return
        if player1.id == player2.id:
            await interaction.followup.send("❌ Please select **different players**.")
            return

        games[k] = {
            "title": title,
            "p1_id": player1.id,
            "p2_id": player2.id,
            "p1_pts": 0,
            "p2_pts": 0,
            "created_by": interaction.user.id
        }
        save_json(self.data)
        await interaction.followup.send(
            f"✅ Scoreboard created for **{title}**:\n"
            f"• {player1.mention} vs {player2.mention}\n"
            f"Use `/duel point` to add points."
        )

    @duel.command(name="point", description="Add 1 point to the winner in the selected game.")
    @app_commands.describe(
        title="Game title",
        winner="Player who won the point"
    )
    async def point(
        self,
        interaction: discord.Interaction,
        title: str,
        winner: discord.Member
    ):
        await interaction.response.defer(thinking=False)
        games = self._g(interaction.guild_id)
        k = self._key(title)
        if k not in games:
            await interaction.followup.send(f"❌ Could not find **{title}**. Create it with `/duel create`.")
            return

        g = games[k]
        if winner.id not in (g["p1_id"], g["p2_id"]):
            await interaction.followup.send("❌ This user is not part of the duel.")
            return

        if winner.id == g["p1_id"]:
            g["p1_pts"] += 1
        else:
            g["p2_pts"] += 1

        save_json(self.data)

        guild = interaction.guild
        p1 = guild.get_member(g["p1_id"]) or f"<@{g['p1_id']}>"
        p2 = guild.get_member(g["p2_id"]) or f"<@{g['p2_id']}>"
        phrases = get_phrases()
        phrase = random.choice(phrases)

        embed = discord.Embed(
            title=f"Scoreboard • {g['title']}",
            description=f"{p1} **{g['p1_pts']}** × **{g['p2_pts']}** {p2}",
            color=discord.Color.green()
        )
        embed.set_footer(text=phrase)
        await interaction.followup.send(embed=embed)

    @duel.command(name="score", description="Show the current score of a game.")
    @app_commands.describe(title="Game title")
    async def score(self, interaction: discord.Interaction, title: str):
        games = self._g(interaction.guild_id)
        k = self._key(title)
        if k not in games:
            await interaction.response.send_message(f"❌ Could not find **{title}**.", ephemeral=True)
            return
        g = games[k]
        p1 = interaction.guild.get_member(g["p1_id"]) or f"<@{g['p1_id']}>"
        p2 = interaction.guild.get_member(g["p2_id"]) or f"<@{g['p2_id']}>"
        await interaction.response.send_message(
            f"**{g['title']}**\n{p1} **{g['p1_pts']}** × **{g['p2_pts']}** {p2}"
        )

    @duel.command(name="end", description="Remove a game's scoreboard.")
    @app_commands.describe(title="Game title")
    async def end(self, interaction: discord.Interaction, title: str):
        games = self._g(interaction.guild_id)
        k = self._key(title)
        if k not in games:
            await interaction.response.send_message(f"❌ Could not find **{title}**.", ephemeral=True)
            return
        games.pop(k)
        save_json(self.data)
        await interaction.response.send_message(f"🗑️ Scoreboard for **{title}** has been removed.")

    @duel.command(name="list", description="List all active scoreboards in this server.")
    async def list_(self, interaction: discord.Interaction):
        games = self._g(interaction.guild_id)
        if not games:
            await interaction.response.send_message("No active scoreboards.", ephemeral=True)
            return
        titles = [games[k]["title"] for k in games]
        await interaction.response.send_message("**Active games:** " + ", ".join(f"`{t}`" for t in titles))

    @score.autocomplete("title")
    @point.autocomplete("title")
    @end.autocomplete("title")
    async def title_autocomplete(self, interaction: discord.Interaction, current: str):
        games = self._g(interaction.guild_id)
        choices = []
        for k, g in games.items():
            if current.lower() in g["title"].lower():
                choices.append(app_commands.Choice(name=g["title"], value=g["title"]))
        return choices[:25]

async def setup(bot: commands.Bot):
    await bot.add_cog(DuelCog(bot))
