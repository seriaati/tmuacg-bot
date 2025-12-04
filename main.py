import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import random
from discord import app_commands


BLUE_HAOHAO = "<:HaoHaoBlue:1445996656284794891>"
GOLDEN_HAOHAO = "<:HaoHaoGolden:1445996673133314110>"
RAINBOW_HAOHAO = "<:HaoHaoRainbow:1445996670709141624>"

RATES = {BLUE_HAOHAO: 0.99, GOLDEN_HAOHAO: 0.01, RAINBOW_HAOHAO: 0.001}


class TMUACGBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            intents=discord.Intents.default(),
            command_prefix=commands.when_mentioned,
        )

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")


bot = TMUACGBot()


@bot.tree.command(name="抽豪", description="抽豪豪")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def draw_hao(i: discord.Interaction) -> None:
    pulls = []
    for _ in range(10):
        rand = random.random()
        cumulative = 0.0
        for hao, rate in RATES.items():
            cumulative += rate
            if rand < cumulative:
                pulls.append(hao)
                break

    formatted_pulls = "\n".join(["".join(pulls[i : i + 5]) for i in range(0, 10, 5)])
    await i.response.send_message(formatted_pulls)


if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
