import discord
import os
from dotenv import load_dotenv, find_dotenv
from discord import FFmpegPCMAudio
from discord.client import _ClientEventTask
from discord.utils import get
from discord.ext import commands
import asyncio
from youtube_dl import YoutubeDL
import requests
from pymongo import MongoClient

load_dotenv(find_dotenv())

Secret = os.environ["SECRET"]
MonogUri = os.environ["MONGO_URI"]

client = MongoClient(MonogUri)
db = client.vvVegaCountRecord

client = commands.Bot(command_prefix='.')
client.remove_command("help")


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.group(invoke_without_command=True)
# custom help command
async def help(ctx):
    em = discord.Embed(
        title="This won't be much help")

    em.add_field(name="Plays any Youtube URL.", value="`.play <url>`")
    em.add_field(name="Pauses the current song.", value="`.pause`")
    em.add_field(name="Resumes the paused song.", value="`.resume`")
    em.add_field(
        name="Joins the voice channel you're currently in.", value="`.join`")
    em.add_field(
        name="Leaves the voice channel you're currently in.", value="`.leave`")
    em.add_field(name="Posts a fella.", value="`.fella`")

    await ctx.send(embed=em)


@client.command()
# joins the voice channel the author is in
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()


@client.command()
# leaves the voice channel the author is in
async def leave(ctx):
    await ctx.voice_client.disconnect()


@client.command()
# plays a youtube link
async def play(ctx, url):
    YDL_OPTIONS = {'verbose': True, 'format': 'bestaudio',
                   'noplaylist': False, 'nocheckcertificate': True, }
    # FFMPEG_OPTIONS = {
    #     'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        voice.play(FFmpegPCMAudio(URL))
        voice.is_playing()
        await ctx.send('Playing your trash song')
    else:
        await ctx.send("I'm already playing a song <a:snifffff:895368996713545768>")


@client.command()
# pauses the current song playing
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()


@client.command()
# pauses the current song playing
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Paused')


@client.command()
# resumes the paused song
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.resume()
    await ctx.send('Resuming')


@client.command()
# prints a 4x4 fella
async def fella(ctx):
    await ctx.channel.send(f'<:vv1:857653948152676352> <:vv2:857653948340240404>')
    await ctx.channel.send(f'<:vv3:857653947903901757> <:vv4:857653948324511744>')


@client.command()
# resets the vvvVegaCount to 0. Only usable by me
async def whyareyougoingtokillthevvegas(ctx):
    if ctx.author.id == 98144379490803712:
        global vvVegaCount
        vvVegaCount = 0
        return


@client.command()
# checks to see if the twitch streamer the user enters is live, not live, or doesn't exist.
async def twitch(ctx, str):
    channelName = str
    contents = requests.get('https://www.twitch.tv/' +
                            channelName).content.decode('utf-8')

    if channelName in contents and 'isLiveBroadcast' in contents:
        results = (
            channelName + ' is live! Check them out here: https://www.twitch.tv/'+channelName)
        await ctx.send(results)
    elif channelName not in contents:
        results = (channelName + ' Is not a valid channel!')
        await ctx.send(results)
    else:
        results = (channelName + ' is not live')
        await ctx.send(results)


@client.command()
async def record(ctx):
    # MongoDB
    queryCount = db.vvega.find_one({}, {"_id": 0, "count": 1})
    vvVegaCount = (queryCount["count"])
    await ctx.send(f'<a:woowowoo:893529115347521616> {vvVegaCount} and counting!<a:woowowoo:893529115347521616>')


@client.event
# vvVega emote counter
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message}: ({channel})')

    # MongoDB
    queryCount = db.vvega.find_one({}, {"_id": 0, "count": 1})
    vvVegaCount = (queryCount["count"])
    stable = db.vvega.find_one({})

    if message.author == client.user:
        return

    # checks to see if a message has the ID for the vvVega emote
    if '<:vvVega:850090008953880576>' in user_message:
        # prints the normal vvVega emote and adds 1 to vvVegaCount
        totalCount = user_message.count('<:vvVega:850090008953880576>')
        vvVegaCount += totalCount
        await message.channel.send(f'<:vvVega:850090008953880576> {vvVegaCount}')
        result = db.vvega.update_one(
            {'_id': stable.get('_id')}, {'$inc': {'count': +1}})
        print(result)
        return
    await client.process_commands(message)

client.run(Secret)
