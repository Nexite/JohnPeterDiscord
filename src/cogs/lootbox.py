import asyncio
import random
from datetime import datetime
from os import getenv

import discord
from discord.ext import commands

from db.models import session_creator, Lootbox
from utils import checks

lootbox_notify_channel = int(getenv("LOOTBOX_NOTIFY_CHANNEL", 693223559387938817))
lootbox_open_channel = int(getenv("LOOTBOX_OPEN_CHANNEL", 689534362760642676))

lootbox_weights = [10, 100, 10, 10]
lootbox_rewards = ["shirt", "badge", "stickers", "pin", ]
badges = [{"id": "party"}, {"id": "dice"}]


async def remove_lootbox(member, amount=1):
    session = session_creator()
    query = session.query(Lootbox).filter_by(user_id=str(member.id)).first()
    if query:
        query.lootboxes -= amount
    else:
        session.add(
            Lootbox(
                user_id=str(member.id),
                lootboxes=1,
            )
        )
    session.commit()


async def add_lootbox(member, amount=1, force=False):
    session = session_creator()
    query = session.query(Lootbox).filter_by(user_id=str(member.id)).first()
    if force:
        if query:
            query.lootboxes += amount
        else:
            session.add(
                Lootbox(
                    user_id=str(member.id),
                    lootboxes=1,
                )
            )
    else:
        if query:
            query.lootboxes += amount
            query.last_earned = datetime.now()
        else:
            session.add(
                Lootbox(
                    user_id=str(member.id),
                    lootboxes=1,
                    last_earned=datetime.now(),
                )
            )
    session.commit()


async def get_lootbox_count(member):
    session = session_creator()
    query = session.query(Lootbox).filter_by(user_id=str(member.id))
    resp = query.first()
    if resp:
        return resp.lootboxes
    else:
        return 0


async def get_last_lootbox_time(member):
    session = session_creator()
    query = session.query(Lootbox).filter_by(user_id=str(member.id))
    resp = query.first()
    if resp:
        return resp.last_earned
    else:
        return None


class LootboxCog(commands.Cog, name="Lootbox"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if discord.utils.get(message.author.roles, name="Community Member") is not None and message.author != self.bot.user and not message.content.startswith("~") and not message.content.startswith("~~") and not message.content.startswith("j!"):
            duration = (datetime.now() - await get_last_lootbox_time(message.author))
            days, seconds = duration.days, duration.seconds
            hours = days * 24 + seconds // 3600
            print(hours)
            if hours >= 1:
                if random.random() < .5:
                    await add_lootbox(message.author)
                    msg = await message.channel.send(
                        f"Congrats <@{message.author.id}> you found 1 CodeDay Lootbox! :game_die:\n("
                        f"this message will self destruct in 10 seconds)")
                    await asyncio.sleep(10)
                    await msg.delete()

    @commands.group(name="lootbox")
    async def lootbox(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid lootbox command passed...')

    @lootbox.command()
    @checks.requires_staff_role()
    async def give(self, ctx, member: discord.Member = None):
        if member:
            await add_lootbox(member, force=True)
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        else:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
            await ctx.message.reply("Please specify someone to give a lootbox to!")

    @lootbox.command()
    async def list(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send(f"{ctx.author.display_name} has {await get_lootbox_count(ctx.author)} lootboxes")
        else:
            await ctx.send(f"{member.display_name} has {await get_lootbox_count(member)} lootboxes")

    @lootbox.command()
    async def open(self, ctx):
        if ctx.channel.id == lootbox_open_channel:
            count = await get_lootbox_count(ctx.author)
            if count > 0:
                message = await ctx.send("Rolling your prize...")
                await asyncio.sleep(2)
                await remove_lootbox(ctx.author)
                prize = random.choices(lootbox_rewards, weights=lootbox_weights, k=1)[0]
                if prize == "shirt":
                    await message.edit(content=f"Congrats! You won a shirt, I am contacting a staff member.")
                    await self.contact_staff(ctx.author, prize)
                elif prize == "badge":
                    await message.edit(content=f"Congrats! You won a badge with id of {random.choice(badges)['id']}.")
                elif prize == "stickers":
                    await message.edit(content=f"Congrats! You won stickers, I am contacting a staff member.")
                    await self.contact_staff(ctx.author, prize)
                elif prize == "pin":
                    await message.edit(content=f"Congrats! You won a pin, I am contacting a staff member.")
                    await self.contact_staff(ctx.author, prize)
                else:
                    await ctx.send("An error occured, please contact a staff member.")
            else:
                await ctx.send(f"{ctx.author.mention} You don't have any lootboxes!")
        else:
            await ctx.message.delete()

    async def contact_staff(self, member, item):
        message = await self.bot.get_channel(lootbox_notify_channel).send(f"<@{member.id}> won {item}. React with :thumbsup: to when done.")

def setup(bot):
    bot.add_cog(LootboxCog(bot))
