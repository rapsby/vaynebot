import discord
import os

client = discord.Client()
@client.event
async def on_ready():
    #print(client.user.id)
    print("ready")
    game = discord.Game("상태메시지")
    await client.change_presence(status=discord.Status.online, activity=game)



@client.event
async def on_message(message):
    if message.content.startswith("!안녕"):
        await message.channel.send("윤호준바보")

access_token = os.environ["BOT_TOKEN"]        
client.run(access_token)
