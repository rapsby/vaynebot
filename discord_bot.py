import discord

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
        await message.channel.send("안녕하세요")
        
client.run('Njg0MDA5OTMwNjA0MjgxODkw.XmUahg.T_ULeCfoJuhSziC-EjbVaTJlKS0')
