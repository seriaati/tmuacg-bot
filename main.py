import os
import aiosqlite
import discord
from dotenv import load_dotenv
from discord.ext import commands
import random
from discord import app_commands


BLUE_HAOHAO = "<:HaoHaoBlue:1445996656284794891>"
GOLDEN_HAOHAO = "<:HaoHaoGolden:1445996673133314110>"
RAINBOW_HAOHAO = "<:HaoHaoRainbow:1445996670709141624>"

RATES = {BLUE_HAOHAO: 0.99, GOLDEN_HAOHAO: 0.005, RAINBOW_HAOHAO: 0.001}


class TMUACGBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            intents=discord.Intents.default(),
            command_prefix=commands.when_mentioned,
        )

    async def create_tables(self) -> None:
        async with self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS draw_hao_pity (
                user_id TEXT PRIMARY KEY,
                pity_count INTEGER NOT NULL
            )
            """
        ):
            await self.db.commit()

    async def setup_hook(self) -> None:
        self.db = await aiosqlite.connect("db.sqlite3")
        await self.create_tables()
        await self.load_extension("jishaku")

    async def close(self) -> None:
        await self.db.close()
        await super().close()


bot = TMUACGBot()


@bot.tree.command(name="抽豪", description="抽豪豪")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def draw_hao(i: discord.Interaction) -> None:
    user_id = str(i.user.id)

    # Get current pity count
    async with bot.db.execute(
        "SELECT pity_count FROM draw_hao_pity WHERE user_id = ?", (user_id,)
    ) as cursor:
        result = await cursor.fetchone()
        pity_count = result[0] if result else 0

    pulls = []

    for _ in range(10):
        pity_count += 1

        # Guarantee golden at 100 pity
        if pity_count >= 100:
            pulls.append(GOLDEN_HAOHAO)
            pity_count = 0
        else:
            rand = random.random()
            cumulative = 0.0
            for hao, rate in RATES.items():
                cumulative += rate
                if rand < cumulative:
                    pulls.append(hao)
                    if hao == GOLDEN_HAOHAO:
                        pity_count = 0
                    break

    # Update pity count in database
    await bot.db.execute(
        """
        INSERT INTO draw_hao_pity (user_id, pity_count)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET pity_count = ?
        """,
        (user_id, pity_count, pity_count),
    )
    await bot.db.commit()

    formatted_pulls = "\n".join(["".join(pulls[i : i + 5]) for i in range(0, 10, 5)])
    await i.response.send_message(formatted_pulls)


if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
