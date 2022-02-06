# bot.py
from asyncio import tasks
import asyncio
import os
from re import search
import youtube_dl
from youtube_dl import YoutubeDL
import discord
from discord.ext import commands   
import random 
import validators

client = commands.Bot(command_prefix=",", case_insensitive=True)

global source
source = []

global looping
looping = False

global loop_index
loop_index = 0

FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
ydl_opts = {"format": "bestaudio/best"}

async def auto_skip(error):

    default_channel = client.get_channel("music_channel")

    voice = reusable_voice

    global loop_index

    global looping

    if not voice.is_playing():

        if not looping:
            
            if len(source) > 1:
            
                source.pop(0)
                voice.play(await discord.FFmpegOpusAudio.from_probe(source[0][0], **FFMPEG_OPTIONS), after=lambda x: client.loop.create_task(auto_skip(x)))
                return await default_channel.send(f"Nova medida do Chega: **{source[0][1]}**.")
            else:

                voice.stop()

        else:
            
            source.append(source[0])
            source.pop(0)
            voice.play(await discord.FFmpegOpusAudio.from_probe(source[0][0], **FFMPEG_OPTIONS), after=lambda x: client.loop.create_task(auto_skip(x)))
            return await default_channel.send(f"Nova medida do Chega: **{source[0][1]}**.")
            
    else:

        voice.stop()

async def search_yt(item):

    with YoutubeDL(ydl_opts) as ydl:
        
        if validators.url(item):
            playlist = ydl.extract_info(item, download=False)
            
        else:
            playlist = ydl.extract_info("ytsearch:{}".format(item), download=False)
        for i in playlist["entries"]:
            source.append((i['formats'][0]['url'], i["title"]))
            

@client.command(name="loop", aliases =["l"])
async def loop(ctx):

    default_channel = client.get_channel("music_channel")

    global looping

    looping = True

    return await default_channel.send(f"É o mesmo programa todo o ano!")

@client.command(name="unloop")
async def unloop(ctx):

    default_channel = client.get_channel("music_channel")

    global looping

    looping = False

    return await default_channel.send(f"O programa vai ser descontinuado este ano")


@client.command(name="shuffle")
async def shuffle(ctx):

    global source 
    temp_0 = source[0]
    source.pop(0)
    random.shuffle(source)
    source = [temp_0] + source

    await queue(ctx)

@client.command(name='play', aliases=['p'])
async def play(ctx, *url):

    default_channel = client.get_channel("music_channel")
    
    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    if ctx.author.voice is None:
        return await ctx.send("Entra num canal primeiro, puta!")

    if not validators.url(url[0]):
        search_info = ""
        for i in url:
            search_info += i + " " 
    else:
        search_info = url[0]
        await default_channel.send("Dá-me um segundo que desta vez, temos mais de 10 páginas.")

    voice_channel = ctx.author.voice.channel

    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice_client == None:
        await voice_channel.connect()

    voice = ctx.voice_client
    global reusable_voice
    reusable_voice = voice  

    await search_yt(search_info)
    if not voice.is_playing():
        await default_channel.send(f"Nova medida do Chega: **{source[0][1]}**.")
        return voice.play(await discord.FFmpegOpusAudio.from_probe(source[0][0], **FFMPEG_OPTIONS),after=lambda x: client.loop.create_task(auto_skip(x)))
    else:
        return await default_channel.send(f"**{source[-1][1]}** foi proposta em parlamento.")

@client.command(name='leave', aliases=["dc","stop"])
async def leave(ctx):

    default_channel = client.get_channel("music_channel")

    global source
    source = []

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    voice = ctx.voice_client
    try:
        return await voice.disconnect()
    except:
        return await default_channel.send("O Chega está em abstenção.")

@client.command(name='next', aliases=["n","skip","s"])
async def next(ctx):

    default_channel = client.get_channel("music_channel")

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    return await auto_skip("-")

@client.command(name='remove', aliases=['r'])
async def remove(ctx, *musictup):

    default_channel = client.get_channel("music_channel")
    voice = ctx.voice_client

    if source == []:
        return await default_channel.send("Ainda nem sequer temos medidas.")

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    if musictup[0].isdigit():
        try:
            music = musictup[0]
            i = int(music)
            temp_name = source[i - 1][1]
            if i == 1 and len(source) == 1:
                voice.stop()
                return await default_channel.send(f"**{temp_name}** já não faz parte do programa do Chega!")
            elif i == 1 and len(source) > 1:
                auto_skip("-")
                return await default_channel.send(f"**{temp_name}** já não faz parte do programa do Chega!")
            source.pop(i - 1)
            return await default_channel.send(f"**{temp_name}** já não faz parte do programa do Chega!")
        except:
            return await default_channel.send(f"Não temos uma medida número {i}, ok?")
    else:
        music = ""
        for i in musictup:
            music += i + " "
        for i in range(len(source)):
            if music.lower() in source[i][1].lower() and i == 0 and len(source) == 1:
                voice.stop()
                return await default_channel.send(f"**{source[0][1]}** já não faz parte do programa do Chega!")
            elif music.lower() in source[i][1].lower() and i == 0 and len(source) > 1:
                auto_skip("-")
                return await default_channel.send(f"**{source[0][1]}** já não faz parte do programa do Chega!")
            elif music.lower() in source[i][1].lower():
                temp_name = source[i][1]
                source.pop(i)
                return await default_channel.send(f"**{temp_name}** já não faz parte do programa do Chega!")
            

@client.command()
async def pause(ctx):

    default_channel = client.get_channel("music_channel")

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    voice = ctx.voice_client

    if voice.is_playing():
        await voice.pause()

    else:
        return await default_channel.send(f"Isso é mentira, o {ctx.author.name} sabe que eu não disse isso...")

@client.command()
async def resume(ctx):

    default_channel = client.get_channel("music_channel")

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    voice = ctx.voice_client

    if voice.is_paused():
        await voice.resume()

    else:
        return await default_channel.send("Eu gostava de poder falar sem ser interrompido.")

@client.command(name='queue', aliases=["q"])
async def queue(ctx):

    default_channel = client.get_channel("music_channel")

    if source == []:
        return await default_channel.send("Não temos mais medidas para apresentar.")

    i = 0
    count = 0

    while i < len(source):
        if i == 0:
            mes = "**O programa do Chega:** \n"
        else:
            mes = ""
        count = len(mes)
        while count < 1900 and i < len(source):
            mes += f"{i+1}. {source[i][1]} \n"
            i += 1
            count = len(mes)
            print(count)
            print(mes)
        await default_channel.send(mes)


client.run("token")