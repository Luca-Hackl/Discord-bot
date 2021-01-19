import nest_asyncio
import discord
import os

import WebScraping
import statistics

from dotenv import load_dotenv
from importlib import reload
from datetime import date
from sys import argv, platform
from time import time



if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    
    # check if token is present
    if TOKEN == "" or TOKEN == None:
      print("❌ No Token specified")
      print("   Run program with `DISCORD_BOT_TOKEN='<token>' python3 DiscordBot.py` or edit the .env file")
      exit(1)

    FORCEASYNCIO = False
    PREFIX = "😷"
    PRODUCTION_MODE = False

    capture_prefix = False
    for argument in argv:
        # Build prefix
        # From this point on it would probably make more sense to do the whole thing via an Args parse lib 😄
        if capture_prefix:
            if argument.startswith("-"):
                capture_prefix = False
            else:
                PREFIX += (" " if len(PREFIX) > 0 else "") + argument

        if argument == "--prefix":
            capture_prefix = True
            PREFIX = ""

        if argument == "-p":
            PRODUCTION_MODE = True

    dictionary = WebScraping.generate_dict()
    statistics.SQLsetup()
    client = discord.Client()
    
    @client.event
    async def on_ready():
        print("Bot started and connected to Discord...")

    @client.event
    async def on_message(message):
        try:
            command = message.content
            
            # Reload WebScraping module only in development mode, because among other things "requests" is quite a large module,
            # which can lead to longer waiting times.
            # Besides, you don't need the live updating in productive mode anyway.
            if not PRODUCTION_MODE:
                reload(WebScraping)

            if command.startswith(PREFIX):
                # Strip prefix from message ("😷 test" -> "test")
                county = message.content[len(PREFIX):].strip()

                # New update command: 😷!update to prevent prefix overloads with other discord bots
                if county == "!update":
                    msg = await message.channel.send("⏰ Updating Data...")
                    response = WebScraping.download_data()
                    if response[0] == True:
                        statistics.SQLadding()
                        await msg.edit(content=f"✅ Updating Data... Done: {response[1]}")
                    else:
                        await msg.edit(content=f"❌ Updating Data... Failed: {response[1]}")
                    return
                
                elif county == "!top5": 
                    
                    listtop5 = statistics.top5()
                                    
                    for item in listtop5:
                        
                        embed, time_start = WebScraping.discordstring(item, dictionary)
                        fetch_time = round((time()-time_start)*1000, 2)
                        msg = await message.channel.send(f"⏰ Searching for county **{item}**...")

                        await msg.edit(content=f"*Fetched in **{fetch_time}ms***", embed=embed)

                elif county[:6] == "!stats":               

                    croppedinput = county[7:]   #getting rid of the !stats                       

                    img = statistics.stats(croppedinput)    
                        
                    await message.channel.send(file=discord.File(img))
                    

                else:     

                    embed, time_start = WebScraping.discordstring(county, dictionary)
                    fetch_time = round((time()-time_start)*1000, 2)
                    msg = await message.channel.send(f"⏰ Searching for county **{county}**...")

                    await msg.edit(content=f"*Fetched in **{fetch_time}ms***", embed=embed)
    
        except Exception as e:
            print("Error occured: " + e)


    if FORCEASYNCIO or not (platform == "win32" or platform == "win64"):
        print("👉 Using nest_asyncio")
        import nest_asyncio
        nest_asyncio.apply()
    nest_asyncio.apply()    
    client.run(TOKEN)