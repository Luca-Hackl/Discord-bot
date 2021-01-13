import nest_asyncio
import discord
import os

import WebScraping

from dotenv import load_dotenv
from importlib import reload
from datetime import date
from sys import argv
from time import time

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')

    # check if token is present
    if TOKEN == "" or TOKEN == None:
      print("❌ No Token specified")
      print("   Run program with `DISCORD_BOT_TOKEN='<token>' python3 DiscordBot.py` or edit the .env file")
      exit(1)

    PREFIX = "😷"
    PRODUCTION_MODE = False

    capture_prefix = False
    for argument in argv:
        print(argument)

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
                        await msg.edit(content=f"✅ Updating Data... Done: {response[1]}")
                    else:
                        await msg.edit(content=f"❌ Updating Data... Failed: {response[1]}")
                    return

                msg = await message.channel.send(f"⏰ Searching for county **{county}**...")
                time_start = time()

                prefix, color, name, cases, deaths, incidence = WebScraping.find_county(county, dictionary)
                # build embed
                embed = discord.Embed(
                  title=f"{prefix} **{name}**",
                  color=color
                )
                embed.add_field(name="👥 Fälle (Gesamt)", value=cases, inline=True)
                embed.add_field(name="☠️ Tode (Gesamt)", value=deaths, inline=True)

                # Add emoji if not in production mode
                # to be able to distinguish the development mode in a productive environment
                if not PRODUCTION_MODE:
                  embed.add_field(name="👾", value="yes", inline=True)

                embed.add_field(name="👉 Inzidenz", value=incidence, inline=False)

                await msg.edit(content=f"*Fetched in **{round((time()-time_start)*1000, 2)}ms***", embed=embed)
        except Exception as e:
            print("Error occured: " + e)

    client.run(TOKEN)
