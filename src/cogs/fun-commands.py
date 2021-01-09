import asyncio
import io
import os
import random
import re
import urllib
from glob import glob
from os import getenv
from random import choice
from urllib import parse, request
import html

import aiohttp
import discord
from discord.ext import commands

from utils.cms import get_sponsor_intro, get_sponsor_audio
from utils.commands import only_random, require_vc


class FunCommands(commands.Cog, name="Fun"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.random_channel = int(getenv("CHANNEL_RANDOM", 689534362760642676))
        self.mod_log = int(getenv("CHANNEL_MOD_LOG", 689216590297694211))
        # Downloads mp3 files
        urls = get_sponsor_audio()
        if not os.path.isdir("./cache/sponsorships/"):
            os.makedirs("./cache/sponsorships/")
        for url in urls:
            file_name = re.sub("(h.*\/)+", "", url)
            urllib.request.urlretrieve(url, f"./cache/sponsorships/{file_name}")

        file_name = re.sub("(h.*\/)+", "", get_sponsor_intro())
        urllib.request.urlretrieve(get_sponsor_intro(), f"./cache/{file_name}")

        self.sponsorships = []
        for file in glob("./cache/sponsorships/*.mp3"):
            print(file)
            self.sponsorships.append(file)

    @commands.command(name="crab", aliases=["crabrave", "crab_rave", "crab-rave"])
    @only_random
    async def crab(self, ctx, *, text: str = None):
        """Turns the text into a crab rave."""
        await ctx.message.delete()
        async with ctx.channel.typing():
            print("Downloading...")
            url = f"https://adventurous-damselfly.glitch.me/video/{parse.quote(text)}.mp4?style=classic"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return False
                    resp = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(resp, f"{text}.mp4"))

    @commands.command(name="owo")
    @only_random
    async def owo(self, ctx):
        """owo"""
        await ctx.send(f"owo what's {ctx.author.mention}")

    @commands.command(
        name="up-down-up-down-left-right-left-right-b-a-start",
        hidden=True,
        aliases=["updownupdownleftrightleftrightbastart"],
    )
    @only_random
    async def updownupdownleftrightleftrightbastart(
            self, ctx,
    ):
        """A lot of typing for nothing."""
        await ctx.send("wow that's a long cheat code. You win 20 CodeCoin!!")

    @commands.command(pass_context=True, aliases=["disconnect"])
    async def disconnectvc(self, ctx):
        await ctx.message.delete()
        vc = ctx.message.guild.voice_client
        if vc is None:
            await ctx.send("You silly, I'm not in any VCs right now.")
        else:
            await vc.disconnect()

    @commands.command(
        name="sponsorship",
        aliases=[
            "sponsor",
            "sponsormessage",
            "sponsor-message",
            "sponsor_message",
            "sponsors",
        ],
    )
    @require_vc
    async def sponsorship(self, ctx):
        """Says a message from a sponsor."""
        await ctx.message.delete()
        retval = os.getcwd()
        vc = await ctx.message.author.voice.channel.connect()
        try:
            file = choice(self.sponsorships)
            intro = discord.FFmpegPCMAudio(f"./cache/sponsor-intro.mp3")
            sponsor = discord.FFmpegPCMAudio(f"{file}")
            player = vc.play(intro)
            while vc.is_playing():
                await asyncio.sleep(1)
            player = vc.play(sponsor)
            while vc.is_playing():
                await asyncio.sleep(1)
        finally:
            await vc.disconnect()

    # entire tag (<a [^>]*>.+?<\/a>)
    # inner text <a [^>]*>(.+?)<\/a>
    # extract href link <a[^>]+href=\"(.*?)\"[^>]*>
    # find tag with link (<a[^>]+href=\"{link}\"[^>]*>.+?<\/a>)
    @commands.command()
    async def embedtest(self, ctx):
        stringmsg = 'Learn from Erwin Chan, a former Microsoft &amp; Amazon software engineering recruiter on how to prepare yourself and stand out from the rest of the crowd as high schoolers and new college undergraduates.&nbsp;&nbsp;<br>Join from a PC, Mac, iPad, iPhone or Android device:<br>&nbsp;&nbsp;&nbsp;&nbsp;Please click this URL to join. <a href=\"https://zoom.us/j/96605864894\">https://zoom.us/j/96605864894</a><br><br>Or join by phone:<br>&nbsp;&nbsp;&nbsp;&nbsp;Dial(for higher quality, dial a number based on your current location):<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;US: +1 470 381 2552  or +1 646 558 8656  or +1 267 831 0333  or +1 312 626 6799  or +1 669 900 9128  or +1 971 247 1195  or +1 206 337 9723  or +1 213 338 8477  or +1 346 248 7799  or +1 602 753 0140 <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Canada: +1 647 558 0588  or +1 778 907 2071  or +1 204 272 7920  or +1 438 809 7799  or +1 587 328 1099  or +1 647 374 4685 <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;United Kingdom: +44 203 901 7895  or +44 208 080 6592 <br>&nbsp;&nbsp;&nbsp;&nbsp;Webinar ID: 966 0586 4894<br>&nbsp;&nbsp;&nbsp;&nbsp;International numbers available: <a href=\"https://zoom.us/u/acxKGQRUlj\">https://zoom.us/u/acxKGQRUlj</a>'

        stringmsg1 = "Learn from Erwin Chan, a former Microsoft &amp; Amazon software engineering recruiter on how to prepare yourself and stand out from the rest of the crowd as high schoolers and new college undergraduates.&nbsp;&nbsp;<br>Join from a PC, Mac, iPad, iPhone or Android device:<br>&nbsp;&nbsp;&nbsp;&nbsp;Please click this URL to join. <a href=\"https://zoom.us/j/96605864894\">https://zoom.us/j/96605864894</a><br><br>Or join by phone:<br>&nbsp;&nbsp;&nbsp;&nbsp;Dial(for higher quality, dial a number based on your current location):<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;US: +1 470 381 2552  or +1 646 558 8656  or +1 267 831 0333  or +1 312 626 6799  or +1 669 900 9128  or +1 971 247 1195  or +1 206 337 9723  or +1 213 338 8477  or +1 346 248 7799  or +1 602 753 0140 <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Canada: +1 647 558 0588  or +1 778 907 2071  or +1 204 272 7920  or +1 438 809 7799  or +1 587 328 1099  or +1 647 374 4685 <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;United Kingdom: +44 203 901 7895  or +44 208 080 6592 <br>&nbsp;&nbsp;&nbsp;&nbsp;Webinar ID: 966 0586 4894<br>&nbsp;&nbsp;&nbsp;&nbsp;International numbers available: <a href=\"https://zoom.us/u/acxKGQRUlj\">https://zoom.us/u/acxKGQRUlj</a>"
        stringmsg1 = stringmsg1.replace("<br />", "\n").replace("<br>", "\n").replace("<p>", "\n").replace("</p>", "\n").replace("<b>", "**").replace("</b>", "**")
        stringmsg1 = html.unescape(stringmsg1)
        a_tags = re.findall("(<a [^>]*>.+?</a>)", stringmsg1)
        for tag in a_tags:
            text = re.search("<a [^>]*>(.+?)</a>", tag).group(1)
            link = re.search("<a[^>]+href=\"(.*?)\"[^>]*>", tag).group(1)
            stringmsg1 = re.sub(f"(<a[^>]+href=\"{link}\"[^>]*>.+?</a>)", f"[{text}]({link})", stringmsg1)
        embedVar = discord.Embed(title=f"Starting Soon: {'Workshop: High School/Undergrads - Preparing Yourself to Land Your Internship/Job'}", description=f"Location: {'https://zoom.us/j/96605864894'} \n\n{stringmsg1}", color=0x00ff00)
        await ctx.send(content="<@&796840081080057856>", embed=embedVar)


def setup(bot):
    bot.add_cog(FunCommands(bot))
