import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import time
import math
import os

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name='Standing by...'), status=discord.Status.online)

#TODO: Have it skim the file to produce a simple number of messages sent
@client.command()
async def history(ctx): 
    pass

#TODO: If file already exists, find last message date and go off from there
@client.command()
async def WriteToFile(ctx):
    print("Started indexing messages in " + ctx.guild.name + " - " + ctx.message.channel.name)
    timeStart = time.time()
    async with ctx.channel.typing():
        await client.change_presence(activity=discord.Game(name="Counting messages...", status=discord.Status.dnd))
        messages = await ctx.channel.history(limit=None, oldest_first = True).flatten()
        fileName = ctx.guild.name + " - " + ctx.message.channel.name + ".txt" 

        with open(fileName, "a+", encoding="utf-8") as f:
            print(*messages, sep="\n", file=f)
            print(ctx.message.created_at)
    timeEnd = time.time()
    timeElapsed = timeEnd - timeStart
    await ctx.channel.send(
        "Wrote message metadata to file!\n" + 
        "Time elapsed: " + str(math.floor(timeElapsed / 60)) + " minutes " + str(round(timeElapsed % 60, 2)) + " seconds"
    )
    await client.change_presence(activity=discord.Game(name='Standing by...', status = discord.Status.online))

# Takes in an amount parameter which sets how many to show on the leaderboard
@client.command()
async def Graph(ctx, amount=5):
    # The text channel needs to be indexed before anything can be done.
    if os.path.isfile(ctx.guild.name + " - " + ctx.message.channel.name + ".txt") is not True:
            return ctx.send("You need to run ``!WriteToFile`` before any graphs can be generated!")

    messageCount = dict() 
    filename = ctx.guild.name + " - " + ctx.channel.name + ".txt"
    with open(filename, "r", encoding="utf8") as f:
        for line in f:
            # There are three "name=" fields in a line.
            # We want the second one, so we start the search one index after the first.
            # After finding it we increment the index by 6 to bypass name= and place us 
            # at the beginning of the actual name.
            start = line.find("name=", line.find("name=")+1) + 6
            
            # Skip the line if the field couldn't be found.
            if start == -1:
                continue

            end = line.find("'", start)
            author = line[start : end]
            if author not in messageCount:
                messageCount[author] = 0
            messageCount[author] += 1


    # Sort from greatest to least before graphing
    messageCount = {k: v for k, v in sorted(messageCount.items(), key=lambda item: item[1], reverse=True)}
    messageCount = dict(list(messageCount.items())[0: amount]) 

    # Create the graph
    plt.bar(*zip(*messageCount.items()))
    plt.title("Amount of Messages Sent", fontsize = 12)
    plt.ylabel('Messages', fontsize=12)
    plt.xlabel('User', fontsize=12)
    plt.xticks(rotation = 20, fontsize = 10)
    
    # The graph needs to be saved to a file before it can be uploaded to the text channel in Discord.
    plt.savefig("graph.png")
    plt.clf()
    await ctx.channel.send(file=discord.File('graph.png'))
    os.remove("graph.png")
    

@client.command()
async def Time(ctx):
    print(ctx.message.created_at)


client.run('INSERT KEY HERE')