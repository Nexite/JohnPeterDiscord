import random

import discord
from discord.ext import commands, tasks

from db.models import session_creator, ReadGuide, Raffles


class RaffleCog(commands.Cog, name="Raffle"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="raffle")
    async def raffle(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid raffle command passed...')

    @raffle.command()
    async def create(self, ctx, id, message, channel: discord.TextChannel, winners=1):
        raffle_message = await channel.send(f"{message} ({winners} winners)\nReact with <:codeday:689531563318312988> to enter!")
        if message:
            session = session_creator()
            session.add(
                Raffles(
                    raffle_id=id,
                    channel_id=str(channel.id),
                    message_id=str(raffle_message.id),
                    message=message,
                    winners=winners,
                )
            )
            session.commit()
        else:
            await ctx.send("an error occured while sending the message")

    @raffle.command()
    async def roll(self, ctx, message: discord.Message):
        session = session_creator()
        query = session.query(Raffles).filter_by(message_id=str(message.id))
        resp = query.all()
        if len(resp) > 0:
            raffle = resp[0]
            reactions = []
            for reaction in message.reactions:
                if reaction.custom_emoji and reaction.emoji.name == "codeday":
                    reaction_members = await reaction.users().flatten()
                    print(len(reaction_members))
                    raffle_winners = []
                    if len(reaction_members) >= raffle.winners:
                        for winner in random.sample(reaction_members, raffle.winners):
                            raffle_winners.append(winner.mention)
                        await ctx.send(" ".join(raffle_winners))
                    else:
                        for winner in reaction_members:
                            raffle_winners.append(winner.mention)
                        await ctx.send(" ".join(raffle_winners) + " (not enough people reacted to meet winners quota)")

            query = session.query(Raffles).filter_by(message_id=str(message.id))
            query.delete()
            session.commit()
        else:
            await ctx.send("raffle not found!")



def setup(bot):
    bot.add_cog(RaffleCog(bot))
