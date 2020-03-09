import discord
import os
import random
import youtube_dl
import asyncio

client = discord.Client()
@client.event
async def on_ready():
    #print(client.user.id)
    print("ready")
    await client.change_presence(game=discord.Game(name='', type=1))



@client.event
async def on_message(message):
    if message.content.startswith("안녕"):
        #await client.send_message(message.channel, "윤호준바아보")
        embed = discord.Embed(
            title='고양이는',
            description='멍멍',
            colour=discord.Colour.green()
        )

        urlBase = 'https://loremflickr.com/320/240?lock='
        randomNum = random.randrange(1, 30977)
        urlF = urlBase+str(randomNum)
        embed.set_image(url = urlF)
        await client.send_message(message.channel, embed=embed)

access_token = os.environ["BOT_TOKEN"]        
client.run(access_token)
