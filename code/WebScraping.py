import json
import requests
import os
import discord
from datetime import date
import csv
from time import time
from difflib import get_close_matches
import statistics

API_URL = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&outSR=4326&f=json"
CSV_FILE_NAME = "RKIData.csv"

def generate_dict():
    csv_data = []
    dictionary = {}

    if not os.path.exists(CSV_FILE_NAME):
        response = download_data()
        if response[0] == True:
            print("Success: " + response[1])
        else:
            print("Failed: " + response[1])

    with open(CSV_FILE_NAME) as f:
        data = csv.reader(f)
        for i, line in enumerate(data):
            # skip header
            if i == 0:
                continue
            csv_data.append(line)

    f.close()
    
    for line in csv_data:
        dictionary[line[0] + " " + line[1]] = (line[3], line[4], line[5])

    return dictionary


"""
Returns: Prefix, PrefixColor, Name, Cases, Deaths, Incidence
"""
def find_county(county, dictionary) -> [str, str, int, int, int]:
    # take dict from dictgenerator and convert it to a list
    dictlist = list(dictionary)

    # take user input from discord and match it to the closest match in the dictionary
    namecounty = get_close_matches(county, dictlist, cutoff=0)[0]

    cumulative = float(dictionary[namecounty][2])

    # load config file
    config = load_config("config.json")
    prefix, color = check_filters(cumulative, config)

    return prefix, color, namecounty, dictionary[namecounty][0], dictionary[namecounty][1], dictionary[namecounty][2]


"""
Returns the prefix and color from a cumulative
"""
def check_filters(cumulative: float, config: dict) -> [str, int]:
    filters = config["filters"]
    
    for f in filters:
        if "lt" in f and not cumulative < f["lt"]:
            continue
        if "lte" in f and not cumulative <= f["lte"]:
            continue
        if "gt" in f and not cumulative > f["gt"]:
            continue
        if "gte" in f and not cumulative >= f["gte"]:
            continue
        if "eq" in f and not cumulative == f["eq"]:
            continue
        return f["prefix"], f["color"]
    
    # you can override the default by not specifing any filters in the array
    print("Warn: No filter found for cumulative:", cumulative, "in config!")
    return "😷", 0


def load_config(path) -> dict:
    # default config
    config = {
        "lowInzidenz": 0,
        "middleInzidenz": 50,
        "highInzidenz": 100,
    }

    if os.path.exists(path):
        with open(path) as f:
            config = json.loads(f.read())

    return config


def download_data():
    if os.path.exists(CSV_FILE_NAME):
        with open(CSV_FILE_NAME) as f:
            f.readline()
            date_last_updated = f.readline()
            date_last_updated = date_last_updated.split(",")[6][:10]
            date_today = date.today().strftime("%d.%m.%Y")
            if date_last_updated == date_today:
                print("Already updated data today...")
                return False, "Already updated data today..."

    f.close()
    # get json data from RKI website
    r = requests.get(API_URL)
    res = r.json()

    countydata = res["features"]
    length = len(list(countydata))

    with open("RKIData.csv", "w") as f:
        f.write(
            "Stadtname, Kreis, Bundesland, Faelle, Tode, Inzidenz, Zuletzt_geupdatet\n")
        for i in range(0, length):
            for channel in countydata[i].values():
                data = f"{channel['GEN']},{channel['BEZ']},{channel['BL']},{channel['cases']},{channel['deaths']},{channel['cases7_per_100k_txt'].replace(',','.')},{channel['last_update']}\n"
                f.write(data)

    f.close()     

    return True, "Updated sucessfully..."

def discordstring(county, dictionary):

    time_start = time()

    prefix, color, name, cases, deaths, incidence = find_county(county, dictionary)
    # build embed
    embed = discord.Embed(
        title=f"{prefix} **{name}**",
        color=color
    )
    embed.add_field(name="👥 Fälle (Gesamt)", value=cases, inline=True)
    embed.add_field(name="☠️ Tode (Gesamt)", value=deaths, inline=True)

    # Add emoji if not in production mode
    # to be able to distinguish the development mode in a productive environment

    embed.add_field(name="👉 Inzidenz", value=incidence, inline=False)

    return embed,time_start


def helpembed():
    
    
    embed = discord.Embed(
        title=f"**Available commands**",
        color=3066993
    )
    embed.add_field(name="Overview", value=":mask: <LK>", inline=False)

    embed.add_field(name="** ** ", value="** ** ", inline=False)

    embed.add_field(name=":bar_chart: Barplot ** **", value=":mask:stats <LK> ** **", inline=True)

    embed.add_field(name=":bar_chart: Comparison", value=":mask:stats <LK> vs <LK2>", inline=True)

    embed.add_field(name="** ** ", value="** ** ", inline=False)

    embed.add_field(name=":chart_with_upwards_trend: Lineplot", value=":mask:line <LK>", inline=True)

    embed.add_field(name=":chart_with_upwards_trend: Comparison Lineplot", value=":mask:line <LK> vs <LK2>", inline=True)

    

    return embed
