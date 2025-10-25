import discord
from discord.ext import commands
import os


RESTAURANT_MENUS = {
    # map restaurant keys (lowercase) to image paths
    "mama": "image/menu.jpg",
    "pizza": "image/menu.jpg",
    "kfc": "image/menu.jpg",
    "starbucks": "image/menu.jpg",
    "mcd": "image/menu.jpg",
}


class Ticket(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore bot messages
        if message.author.bot:
            return

        # only respond inside ticket channels (name starts with 'ticket-')
        if isinstance(message.channel, discord.TextChannel) and message.channel.name.startswith("ticket-"):
            content = message.content.strip()
            lower = content.lower()

            if "open ticket" in lower:
                await message.channel.send(
                    "These are the restaurants in the canteen:\n1. Mama\n2. Pizza\n3. KFC\n4. Starbucks\n5. McD\nType `!menu <name>` to see the menu. eg `!menu mama`"
                )
                return
                # only handle non-command natural-language triggers like 'open ticket'

        await self.bot.process_commands(message)

    @commands.command(name="menu")
    async def menu_cmd(self, ctx: commands.Context, restaurant: str = None):
        """Prefix command: !menu <restaurant>"""
        if restaurant is None:
            await ctx.send("Please specify a restaurant. Example: `!menu mama`")
            return
        rest = restaurant.lower()
        path = RESTAURANT_MENUS.get(rest)
        if path and os.path.isfile(path):
            await ctx.send(file=discord.File(path))
        else:
            await ctx.send("Sorry, I don't have the menu for that restaurant.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Ticket(bot))

