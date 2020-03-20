import discord
import asyncio
import random
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot
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
pid = 0


class VoiceState(object):
    def __init__(self, client):
        self.current = None
        self.client = client
        self.channel = None
        self.plist = list()
        self.songs = asyncio.Queue()
        self.play_next_song = asyncio.Event()

    def toggle_next(self, *args):
        print('toggle_next')
        self.client.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            self.plist.pop(0)
            self.channel.play(self.current, after=self.toggle_next)
            await self.play_next_song.wait()

vs = VoiceState(client)

def task():
    print('task')
    client.loop.create_task(vs.audio_player_task())
    
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
    'options': '-vn'
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
    print(discord.__version__)
    activity = discord.Game(name="호준이가 노래")
    await client.change_presence(status=discord.Status.online , activity=activity)



@client.event
async def on_message(message):
    global vs
    if message.author == client.user:
        return
    if message.content.startswith("-pl") or message.content.startswith("-ㅔㅣ") or message.content.startswith("ㅔㅣ"):
        if message.author.voice and message.author.voice.channel:
            channel = message.author.voice.channel
            msg = message.content.split(" ")
            q = msg[1:]
            q = "+".join(q)
            key = os.environ["key"] 
            url = 'https://www.googleapis.com/youtube/v3/search?key={}&part=snippet&type=video&q='.format(key) + parse.quote(q)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            
            
            with urllib.request.urlopen(req) as response:
                source = response.read()
                data = json.loads(source)
                id_list = list()
                title_list = list()
                for i in range(5):
                    sid = data['items'][i]['id']['videoId']
                    title = data['items'][i]['snippet']['title']
                    id_list.append(sid)
                    title_list.append(title)
            
            titlestr = "```css\n[음악선택]\n\n"
            titlestr += "TYPE TO SELECT : 1 ~ 5\nTYPE TO Exit : anything\n"            
            for i in range(0, len(title_list)):
                titlestr += str(i+1)+" : "+title_list[i]+"\n"
            await message.channel.send(titlestr+"```")   
            
            try:
                answer = await client.wait_for('message', timeout=60)
                selected = None
                if answer:
                    if 1<=answer.content[0]<=5:
                        selected = answer.content[0]-1
                    else:
                        return
            except asyncio.TimeoutError:
                return
                
            id = selected

            if client.voice_clients and channel == client.voice_clients[0].channel:
                voice_client = client.voice_clients[0]
            else:
                voice_client = await channel.connect()
                vs.channel = voice_client
            player = await YTDLSource.from_url('https://www.youtube.com/watch?v='+id)

            embed = discord.Embed(
                title=player.data['title'],
                description=time.strftime('%H:%M:%S', time.gmtime(player.data['duration'])),
                colour=discord.Colour.blue()
            )
            
            '''
            server = message.guild
            if server.id in que:
                que[server.id].append(player)
            else: 
                que[server.id] = [player]

            queue(server.id, voice_client)
            '''
            
            
            await vs.songs.put(player)
            vs.plist.append(player.title)
            
            await message.channel.send(embed = embed)

    elif message.content.startswith("-p") or message.content.startswith("-P") or message.content.startswith("-ㅔ") or message.content.startswith("ㅔㅔ"):
        if message.author.voice and message.author.voice.channel:
            channel = message.author.voice.channel
            msg = message.content.split(" ")
            q = msg[1:]
            q = "+".join(q)
            key = os.environ["key"] 
            url = 'https://www.googleapis.com/youtube/v3/search?key={}&part=snippet&type=video&q='.format(key) + parse.quote(q)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                source = response.read()
                data = json.loads(source)
                id = data['items'][0]['id']['videoId']
            
            if client.voice_clients and channel == client.voice_clients[0].channel:
                voice_client = client.voice_clients[0]
            else:
                voice_client = await channel.connect()
                vs.channel = voice_client
            player = await YTDLSource.from_url('https://www.youtube.com/watch?v='+id)

            embed = discord.Embed(
                title=player.data['title'],
                description=time.strftime('%H:%M:%S', time.gmtime(player.data['duration'])),
                colour=discord.Colour.blue()
            )
            
            '''
            server = message.guild
            if server.id in que:
                que[server.id].append(player)
            else: 
                que[server.id] = [player]

            queue(server.id, voice_client)
            '''
            
            
            await vs.songs.put(player)
            vs.plist.append(player.title)
            
            await message.channel.send(embed = embed)
            
            
    if message.content.startswith("-l") or message.content.startswith("-ㅣ"):

        if vs.plist or vs.current and vs.channel and vs.channel.is_playing():
            playstr = "```css\n[재생목록]\n\n"
            playstr += str(1)+" : " + vs.current.title + "\n[-----playing] \n"            
            for i in range(0, len(vs.plist)):
                playstr += str(i+2)+" : "+vs.plist[i].title()+"\n"
            await message.channel.send(playstr+"```")
            
        else:
            await message.channel.send(embed=discord.Embed(title=":no_entry_sign: 재생목록이 없습니다.",colour = 0x2EFEF7))
            return
        

       
    if message.content.startswith("-s") or message.content.startswith("-ㄴ"):
        if message.author.voice and message.author.voice.channel:
            channel = message.author.voice.channel            
            if client.voice_clients and channel == client.voice_clients[0].channel:
                if client.voice_clients[0].is_playing():
                    client.voice_clients[0].stop()
                    await message.channel.send(embed=discord.Embed(title="컽! by {}".format(message.author), colour = 0x2EFEF7))

    if message.content.startswith("-q") or message.content.startswith("-ㅂ"):
        if message.author.voice and message.author.voice.channel:
            channel = message.author.voice.channel            
            if client.voice_clients and channel == client.voice_clients[0].channel:
                await client.voice_clients[0].disconnect()
                vs = VoiceState(client)

    if message.content.startswith("-?") or message.content.startswith("-h") or message.content.startswith("-ㅗ"):
        description = "-p(lay) song title \n-l(ist)\n-s(kip)\n-q(uit)\n-?\n-h(elp)"
        embed = discord.Embed(
            title="명령어",
            description=description,
            colour=discord.Colour.blue()
            )
        await message.channel.send(embed=embed)
        
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

task()
access_token = os.environ["BOT_TOKEN"]        
client.run(access_token)
