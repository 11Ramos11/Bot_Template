# bot.py
from asyncio import tasks
import asyncio
import os
import youtube_dl
from youtube_dl import YoutubeDL
import discord
from discord.ext import commands    

client = commands.Bot(command_prefix=",")

source = []
info_playlist = []

FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
ydl_opts = {"format": "bestaudio/best"}

def auto_skip(error):

    default_channel = client.get_channel("channel id")
    
    voice = reusable_voice

    if len(source) > 1:
        voice.stop()
        source.pop(0)
        info_playlist.pop(0)
        voice.play(source[0],after=auto_skip)
        default_channel.send(f"Nova medida do Chega: **{info_playlist[0]}**.")
    else:
        default_channel.send("Huh... em abstenção mais uma vez!")

async def search_yt(item):

    with YoutubeDL(ydl_opts) as ydl:
        
        playlist = ydl.extract_info("ytsearch:{}".format(item), download=False)['entries']
        for i in playlist:
            source.append(await discord.FFmpegOpusAudio.from_probe(i['formats'][0]['url'], **FFMPEG_OPTIONS))
            info_playlist.append(i["title"])
  

@client.command(name='play', aliases=['p'])
async def play(ctx, *url):

    default_channel = client.get_channel("channel id")

    search_info = ""
    for i in url:
        search_info += i + " " 

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    if ctx.author.voice is None:
        return await ctx.send("Entra num canal primeiro, puta!")

    voice_channel = ctx.author.voice.channel

    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice_client == None:
        await voice_channel.connect()

    voice = ctx.voice_client
    global reusable_voice
    reusable_voice = voice  

    await search_yt(search_info)
    print(source, info_playlist)
    if not voice.is_playing():
        await default_channel.send(f"Nova medida do Chega: **{info_playlist[0]}**.")
        return voice.play(source[0],after=auto_skip)
    else:
        return await default_channel.send(f"**{info_playlist[-1]}** foi proposta em parlamento.")

@client.command(name='leave', aliases=["dc","stop"])
async def leave(ctx):

    default_channel = client.get_channel("channel id")

    global source
    source = []
    global info_playlist
    info_playlist = []

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    voice = ctx.voice_client
    try:
        return await voice.disconnect()
    except:
        return await default_channel.send("O Chega está em abstenção.")

@client.command(name='next', aliases=["n","skip","s"])
async def next(ctx):

    default_channel = client.get_channel("channel id")

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    voice = ctx.voice_client
    if len(source) > 1:
        await voice.stop()
        source.pop(0)
        info_playlist.pop(0)
        voice.play(source[0],after=auto_skip)
        return await default_channel.send(f"Nova medida do Chega: **{info_playlist[0]}**.")
    else:
        return await default_channel.send("Não temos mais medidas no programa.")

@client.command(name='remove', aliases=['r'])
async def remove(ctx, *musictup):

    default_channel = client.get_channel("channel id")
    voice = ctx.voice_client

    if info_playlist == []:
        return await default_channel.send("Ainda nem sequer temos medidas.")

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    if musictup[0].isdigit():
        try:
            music = musictup[0]
            i = int(music)
            temp_name = info_playlist[i - 1]
            if i == 1 and len(info_playlist) == 1:
                voice.stop()
                return await default_channel.send(f"**{temp_name}** já não faz parte do programa do Chega!")
            elif i == 1 and len(info_playlist) > 1:
                auto_skip("-")
                return await default_channel.send(f"**{temp_name}** já não faz parte do programa do Chega!")
            source.pop(i - 1)
            info_playlist.pop(i - 1)
            return await default_channel.send(f"**{temp_name}** já não faz parte do programa do Chega!")
        except:
            return await default_channel.send(f"Não temos uma medida número {i}, ok?")
    else:
        music = ""
        for i in musictup:
            music += i + " "
        for i in range(len(info_playlist)):
            if music.lower() in info_playlist[i].lower() and i == 0 and len(info_playlist) == 1:
                voice.stop()
                return await default_channel.send(f"**{info_playlist[0]}** já não faz parte do programa do Chega!")
            elif music.lower() in info_playlist[i].lower() and i == 0 and len(info_playlist) > 1:
                auto_skip("-")
                return await default_channel.send(f"**{info_playlist[0]}** já não faz parte do programa do Chega!")
            elif music.lower() in info_playlist[i].lower():
                temp_name = info_playlist[i]
                source.pop(i)
                info_playlist.pop(i)
                return await default_channel.send(f"**{temp_name}** já não faz parte do programa do Chega!")
            

@client.command()
async def pause(ctx):

    default_channel = client.get_channel("channel id")

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    voice = ctx.voice_client

    if voice.is_playing():
        await voice.pause()

    else:
        return await default_channel.send(f"Isso é mentira, o {ctx.author.name} sabe que eu não disse isso...")

@client.command()
async def resume(ctx):

    default_channel = client.get_channel("channel id")

    if ctx.message.channel != default_channel:
        return await default_channel.send(f"{ctx.author.mention}, não é aí seu burro do caralho!")

    voice = ctx.voice_client

    if voice.is_paused():
        await voice.resume()

    else:
        return await default_channel.send("Eu gostava de poder falar sem ser interrompido.")

@client.command(name='queue', aliases=["q"])
async def queue(ctx):

    default_channel = client.get_channel("channel id")

    if info_playlist == []:
        return await default_channel.send("Não temos mais medidas para apresentar.")

    mes = "**O programa do Chega:** \n"

    for i, tit in enumerate(info_playlist):
        mes += f"{i+1}. {tit} \n"
    return await default_channel.send(mes)

client.run("Server Token")