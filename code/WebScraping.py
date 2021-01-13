import json
import requests
import os
from datetime import date
import csv

from difflib import get_close_matches 

def dictgenerator ():

    csvData = []
    dictionary = {}
    
    if os.path.exists("RKIData.csv") == False:
        response = downloadData()
        if response[0] == True:
            print("Success: " + response[1])
        else:
            print("Failed: " + response[1])

    i = 0
    with open("RKIData.csv") as file:
        data = csv.reader(file)
        for line in data:
            if i != 0:
                csvData.append(line)
            i = i + 1

    for line in csvData:
        dictionary[line[0] + " " + line[1]] = (line[3], line[4], line[5])
        
    return dictionary

def findCountie(countie, dictionary):
    prefix = ""
    
    #load config file
    config = loadConfig("config.json")

    dictlist = list(dictionary)     #take dict from dictgenerator and convert it to a list
    namecountie = get_close_matches(countie, dictlist, cutoff = 0)[0]   #take user input from discord and match it to the closest match in the dictionary
    
    
    comulative = float(dictionary[namecountie][2])
    if comulative >= config["highInzidenz"]:
        prefix = "🔴"
    elif comulative >= config["middleInzidenz"]:
        prefix = "🟡"
    else:
        prefix = "🟢"

    stringfordiscordchat = f"{prefix} {namecountie}: Gesamtfälle: {dictionary[namecountie][0]}, Gesamttode: {dictionary[namecountie][1]}, Inzidenz: {dictionary[namecountie][2]}"#create string that can be returned and used

    return stringfordiscordchat

def loadConfig(path):
    config = {}
    if os.path.exists(path) == False:
            config["lowInzidenz"] = 0
            config["middleInzidenz"] = 100
            config["highInzidenz"] = 200
    else:
        file = open(path)
        config = json.loads(file.read())
        file.close()
        
    return config

def downloadData():

    if os.path.exists("RKIData.csv"):
        with open("RKIData.csv") as file:
            file.readline()
            dateLastUpdated = file.readline()
            dateLastUpdated = dateLastUpdated.split(",")[6][:10]
            dateToday = date.today().strftime("%d.%m.%Y")
            if dateLastUpdated == dateToday:
                print("Already updated data today...")
                return False, "Already updated data today..."

    r = requests.get("https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&outSR=4326&f=json") #get json data from RKI website
    res = r.json()

    countydata = res["features"]
    length = len(list(countydata))
    
    with open("RKIData.csv", "w") as file:
        file.write("Stadtname, Kreis, Bundesland, Faelle, Tode, Inzidenz, Zuletzt_geupdatet\n")
        for i in range(0, length):
            for channel in countydata[i].values():                
                data = f"{channel['GEN']},{channel['BEZ']},{channel['BL']},{channel['cases']},{channel['deaths']},{channel['cases7_per_100k_txt'].replace(',','.')},{channel['last_update']}\n"
                file.write(data)

    return True, "Updated sucessfully..."