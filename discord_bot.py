import discord
import asyncio
import random
from discord import Member
from discord.ext import commands
import youtube_dl
from urllib.request import urlopen, Request
import urllib
import urllib.request
import os
import sys
import json
import time
import datetime
import re
import ffmpeg
from urllib import parse

client = discord.Client()

que = {}
playerlist = {}
playlist = list()


def queue(id): #음악 재생용 큐
	if que[id] != []:
		player = que[id].pop(0)
		playerlist[id] = player
		del playlist[0]
		player.start()


youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
    'executable':"C:/ffmpeg/bin/ffmpeg.exe"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)






@client.event
async def on_ready():
    #print(client.user.id)
    print("ready")
    activity = discord.Game(name="호준이가 노래")
    await client.change_presence(status=discord.Status.online , activity=activity)



@client.event
async def on_message(message):
    if message.author == client.user: #봇이 채팅을 쳤을 때 명령어로 인식되지 않음
        return

    if '호준' in message.content:
        embed = discord.Embed(
            title='호준이는 ',
            description='천재',
            colour=discord.Colour.dark_red()
        )
        await message.channel.send(embed=embed)

    if '상민' in message.content:
        embed = discord.Embed(
            title='상민이는 ',
            description='바보',
            colour=discord.Colour.blue()
        )
        await message.channel.send(embed=embed)
        
    if message.content.startswith("안녕"):
        embed = discord.Embed(
            title='고양이는',
            description='멍멍',
            colour=discord.Colour.green()
        )

        urlBase = 'https://loremflickr.com/320/240?lock='
        randomNum = random.randrange(1, 30977)
        urlF = urlBase+str(randomNum)
        embed.set_image(url = urlF)
        await message.channel.send(embed=embed)

    if message.content.startswith("-p"): #음성채널에 봇을 추가 및 음악 재생
        msg = message.content.split(" ")
        msg = msg[1:]
        msg = "+".join(msg)
        key = os.environ["key"] 
        url = 'https://www.googleapis.com/youtube/v3/search?key={}&part=snippet&q='.format(key) + parse.quote(msg)
        with urllib.request.urlopen(url) as response:
            source = response.read()
            data = json.loads(source)
            id = data['items'][0]['id']['videoId']


        if message.author.voice == None:
            await message.channel.send('You have to join a voice channel.')
        else:
            channel = message.author.voice.channel
            voice_client = await channel.connect()
            print(voice_client.is_connected())
            print(voice_client.channel)
            print(channel)
            #if voice_client.is_connected() and not playerlist[str(server.id)].is_playing(): #봇이 음성채널에 접속해있으나 음악을 재생하지 않을 때
            #    await voice_client.disconnect()
            #elif voice_client.is_connected() and playerlist[str(server.id)].is_playing(): #봇이 음성채널에 접속해있고 음악을 재생할 때
            if voice_client.is_connected():
                
                player = await YTDLSource.from_url('https://www.youtube.com/watch?v='+id)
                voice_client.play(player)
                '''
                if server.id in que: #큐에 값이 들어있을 때
                    que[server.id].append(player)
                else: #큐에 값이 없을 때
                    que[server.id] = [player]
                await message.channel.send(embed=discord.Embed(title=":white_check_mark: 추가 완료!",colour = 0x2EFEF7))
                '''
                
                #playlist.append(player.title) #재생목록에 제목 추가
                return

            try:
                voice_client = await channel.connect()
            except discord.errors.InvalidArgument: #유저가 음성채널에 접속해있지 않을 때
                await message.channel.send(embed=discord.Embed(title=":no_entry_sign: 음성채널에 접속하고 사용해주세요.",colour = 0x2EFEF7))
                return

            try:
                player = await voice_client.create_ytdl_player(url,after=lambda:queue(server.id),before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
                playerlist[server.id] = player
                playlist.append(player.title)
            except youtube_dl.utils.DownloadError: #유저가 제대로 된 유튜브 경로를 입력하지 않았을 때
                await message.channel.send(embed=discord.Embed(title=":no_entry_sign: 존재하지 않는 경로입니다.",colour = 0x2EFEF7))
                await voice_client.disconnect()
                return
            player.start()
'''
    if message.content == "!종료": #음성채널에서 봇을 나가게 하기
        server = message.server
        voice_client = await channel.connect()

        if voice_client == None: #봇이 음성채널에 접속해있지 않았을 때
            await message.channel.send(embed=discord.Embed(title=":no_entry_sign: 봇이 음성채널에 없어요.",colour = 0x2EFEF7))
            return
        
        await message.channel.send(embed=discord.Embed(title=":mute: 채널에서 나갑니다.",colour = 0x2EFEF7)) #봇이 음성채널에 접속해있을 때
        await voice_client.disconnect()

    if message.content == "!스킵":
        id = message.server.id
        if not playerlist[id].is_playing(): #재생 중인 음악이 없을 때
            await message.channel.send(embed=discord.Embed(title=":no_entry_sign: 스킵할 음악이 없어요.",colour = 0x2EFEF7))
            return
        await message.channel.send(embed=discord.Embed(title=":mute: 스킵했어요.",colour = 0x2EFEF7))
        playerlist[id].stop()

    if message.content == "!목록":

        if playlist == []:
            await message.channel.send(embed=discord.Embed(title=":no_entry_sign: 재생목록이 없습니다.",colour = 0x2EFEF7))
            return

        playstr = "```css\n[재생목록]\n\n"
        for i in range(0, len(playlist)):
            playstr += str(i+1)+" : "+playlist[i]+"\n"
        await message.channel.send(playstr+"```")
'''

access_token = os.environ["BOT_TOKEN"]        
client.run(access_token)
