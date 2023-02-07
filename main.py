import discord
from discord.ext import commands
import json
import asyncio
import requests
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

ffmpeg_options = {
    "options": "-vn"
}



import asyncio, datetime

class RainwaveApi:
    def __init__(self, conf):
        self.apikey = conf["rainwave_api"]
        self.user_id = conf["rainwaive_user_id"]
        self.station_id = None
        self.urls = {1: "https://relay.rainwave.cc/game.mp3",
                     2: "https://relay.rainwave.cc/ocremix.mp3",
                     3: "https://relay.rainwave.cc/covers.mp3",
                     4: "https://relay.rainwave.cc/chiptune.mp3",
                     5: "https://relay.rainwave.cc/all.mp3"}

        self.base_url = "https://rainwave.cc/api4/"
        self.current_info = None

    def setStation(self, station_id):
        self.station_id = station_id
        self.current_url = self.urls[self.station_id]


    def getEndTime(self):
        return self.current_info["sched_current"]["end"]

    def getStreamUrl(self):
        return self.current_url

    def updateInfo(self):
        if self.station_id is not None:
            self.current_info = requests.get(self.base_url + "info", params={"sid":self.station_id, "user_id": self.user_id, "key": self.apikey}).json()

    def getCurrentPlayingInfo(self):
        self.updateInfo()

        infos = None
        if self.station_id is not None:
            infos = {}
            
            infos["title"] =  self.current_info["sched_current"]["songs"][0]["title"]
            infos["cover"] = "https://rainwave.cc" + self.current_info["sched_current"]["songs"][0]["albums"][0]["art"] + "_240.jpg"
            infos["author"] = self.current_info["sched_current"]["songs"][0]["artists"][0]["name"]
            infos["album"] = self.current_info["sched_current"]["songs"][0]["albums"][0]["name"]

        return infos


class RainWave(commands.Cog):
    def __init__(self, bot, api, conf):
        self.bot = bot
        self.api = api
        self.conf = conf
        self.inVoice = False

        self.list_radio = discord.Embed(title="Radios")
        self.list_radio.add_field(name="Game", value="1")
        self.list_radio.add_field(name="OcRemix", value="2")
        self.list_radio.add_field(name="Covers", value="3")
        self.list_radio.add_field(name="Chiptune", value="4")
        self.list_radio.add_field(name="All", value="5")


    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged in as")
        print(bot.user.name)
        print(bot.user.id)
        print("-------------")

        self.autoInfoTask = asyncio.get_event_loop().create_task(self.autoInfo())


    async def autoInfo(self):
        while not self.bot.is_closed():
            await asyncio.sleep(1)
            if self.inVoice:
                infos = self.api.getCurrentPlayingInfo()

                if infos is not None:
                    embed = discord.Embed(title=infos["title"])
                    embed.set_image(url=infos["cover"])
                    embed.add_field(name="Album", value=infos["album"])
                    embed.add_field(name="Author", value=infos["author"])

                    channel = self.bot.get_channel(self.conf["channel_id"])

                    await channel.send(embed=embed)
                    dt = datetime.datetime.fromtimestamp(self.api.getEndTime())
                    endTime = dt + datetime.timedelta(seconds=5)
                    now = datetime.datetime.now()
                    await asyncio.sleep((endTime - now).total_seconds())


    @commands.command()
    async def play(self, ctx, *, station_id: int):
        if station_id not in [1, 2, 3, 4, 5]:
            await ctx.send("Unknown station : " + str(station_id))
            await ctx.send(embed=self.list_radio)
            return

        self.api.setStation(station_id)

        async with ctx.typing():
            player = discord.FFmpegPCMAudio(self.api.getStreamUrl(), **ffmpeg_options)
            ctx.voice_client.play(player)

    @commands.command()
    async def stop(self, ctx):
        self.inVoice = False
        await ctx.voice_client.disconnect()

    @commands.command()
    @commands.cooldown(1, 3.0, type=commands.BucketType.channel)
    async def info(self, ctx):
        infos = self.api.getCurrentPlayingInfo()
        embed = discord.Embed(title=infos["title"], color=0xE39F29)
        
        embed.set_image(url=infos["cover"])
        embed.add_field(name="Album", value=infos["album"])
        embed.add_field(name="Author", value=infos["author"])
        
        await ctx.send(embed=embed)


    @play.error
    async def playError(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=self.list_radio)


    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                self.inVoice = True
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


def main():
    with open("config.json", "r") as configfile:
        conf = json.load(configfile)

        api = RainwaveApi(conf)


        asyncio.run(bot.add_cog(RainWave(bot, api, conf)))

        bot.run(conf["token"])

if __name__ == "__main__":
    main()
