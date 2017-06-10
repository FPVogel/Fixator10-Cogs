import discord
from discord.ext import commands
import aiohttp
from datetime import datetime
from .utils import chat_formatting as chat
import tabulate


class MinecraftData:
    """Minecraft-Related data"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.group(name="minecraft", aliases=["mc"], pass_context=True)
    async def minecraft(self, ctx):
        """Get Minecraft-Related data"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @minecraft.command(pass_context=True)
    async def skin(self, ctx, nickname: str, helm_layer: bool = True):
        """Get minecraft skin by nickname"""
        helm_layer = str(helm_layer).lower()
        em = discord.Embed(timestamp=ctx.message.timestamp, url="https://mcapi.ca/rawskin/"+nickname)
        em.set_footer(text="Provided by MCAPI", icon_url="https://mcapi.ca/img/icon.png")
        em.set_author(name=nickname, icon_url="https://mcapi.ca/avatar/"+nickname+"/"+helm_layer)
        em.set_thumbnail(url="https://mcapi.ca/rawskin/"+nickname)
        em.set_image(url="https://mcapi.ca/skin/"+nickname+"/"+helm_layer)
        await self.bot.say(embed=em)

    @minecraft.command(pass_context=True)
    async def isup(self, ctx, IP_or_domain: str):
        """Is minecraft server up or down?"""
        try:
            async with self.session.get('https://mcapi.ca/isup/'+IP_or_domain) as data:
                data = await data.json()
            await self.bot.say(data["message"])
        except Exception as e:
            await self.bot.say(chat.error("Unable to check. An error has been occurred: "+chat.inline(e)))

    @minecraft.command(pass_context=True)
    async def server(self, ctx, IP_or_domain: str):
        """Get info about server"""
        try:
            async with self.session.get('https://mcapi.ca/query/{}/info'.format(IP_or_domain)) as data:
                data = await data.json()
            em = discord.Embed(title="Server data: "+IP_or_domain, description="Provided by MCAPI",
                               timestamp=ctx.message.timestamp)
            em.set_footer(text="Provided by MCAPI", icon_url="https://mcapi.ca/img/icon.png")
            em.add_field(name="Status", value=str(data["status"]).replace("True", "OK").replace("False", "Not OK"))
            em.set_thumbnail(url="https://mcapi.ca/query/{}/icon".format(IP_or_domain))
            if data["status"]:
                em.add_field(name="Ping", value=data["ping"] or chat.inline("N/A"))
                em.add_field(name="Version", value="{} (Protocol: {})".format(data["version"], data["protocol"]))
                em.add_field(name="Players", value="{}/{}".format(data["players"]["online"], data["players"]["max"]))
            else:
                em.add_field(name="Error", value="Unable to fetch server: {}".format(chat.inline(data["error"])))
            await self.bot.say(embed=em)
        except Exception as e:
            await self.bot.say(chat.error("Unable to check. An error has been occurred: "+chat.inline(e)))

    @minecraft.command(pass_context=True)
    async def status(self, ctx):
        """Get status of minecraft services"""
        try:
            async with self.session.get('https://mcapi.ca/mcstatus') as data:
                data = await data.json()
            em = discord.Embed(title="Status of minecraft services", description="Provided by MCAPI",
                               timestamp=ctx.message.timestamp)
            em.set_footer(text="Provided by MCAPI", icon_url="https://mcapi.ca/img/icon.png")
            for entry, status in data.items():
                status = status["status"]
                em.add_field(name=entry, value=status)
            await self.bot.say(embed=em)
        except Exception as e:
            await self.bot.say(chat.error("Unable to check. An error has been occurred: "+chat.inline(e)))

    @minecraft.command(pass_context=True, aliases=["nicknames", "nickhistory"])
    async def nicks(self, ctx, current_nick: str):
        """Check history of user's nicks history"""
        try:
            async with self.session.get('https://api.mojang.com/users/profiles/minecraft/'+current_nick) as data:
                data_current = await data.json()
            if data_current is None:
                raise Exception("Server return empty response. (Non-existing player?)")
            try:
                async with self.session.get('https://api.mojang.com/user/'
                                            'profiles/'+data_current["id"]+'/names') as data:
                    data_history = await data.json()
                for nick in data_history:
                    try:
                        nick["changedToAt"] = \
                            datetime.fromtimestamp(nick["changedToAt"]/1000).strftime('%d.%m.%Y %H:%M:%S')
                    except:
                        pass
                await self.bot.say(chat.box(tabulate.tabulate(data_history,
                                                              headers={"name": "Nickname",
                                                                       "changedToAt": "Changed to at..."},
                                                              tablefmt="fancy_grid")))
            except Exception as e:
                await self.bot.say(chat.error("Unable to check name history.\nAn error has been occurred: " +
                                              chat.inline(e)))
        except Exception as e:
            await self.bot.say(chat.error("Unable to find this user.\nAn error has been occurred: "+chat.inline(e)))


def setup(bot):
    bot.add_cog(MinecraftData(bot))
