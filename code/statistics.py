import WebScraping
import DiscordBot

import mysql.connector
import discord
from time import time
from dotenv import load_dotenv
import os

import requests
import json
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib as mpl 
import matplotlib.pyplot as plt

API_URL = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&outSR=4326&f=json"
CSV_FILE_NAME = "RKIData.csv"

def SQLconnect(): 

    load_dotenv()
    user = os.getenv('user') #gets user from .env file
    password = os.getenv('password') #gets password from .env file

    mydb = mysql.connector.connect(
    host = "localhost",
    user = user,
    passwd = password,
    database = "mydatabase"
    )
    return mydb

def SQLsetup():
    
    mydb = SQLconnect() #connects to SQL server    
    cursor = mydb.cursor()  

    try:
        cursor.execute("CREATE TABLE landkreis (Stadtname VARCHAR(50), Kreis VARCHAR(50), Bundesland VARCHAR(50), Faelle INTEGER, Tode INTEGER, Inzidenz FLOAT, Zuletzt_geupdatet DATE)")
    except:
        print("Database is set up") #if TABLE already exist it exit, if it doesnt exist it gets created

    cursor.close()
    mydb.close()

def top5():

    mydb = SQLconnect() #connects to SQL server    
    cursor = mydb.cursor(buffered=True)  

    sql_select_query  = """SELECT * FROM landkreis ORDER BY Zuletzt_geupdatet DESC, Inzidenz DESC"""  #SQL query
    
    cursor.execute(sql_select_query) 

    mynames = []
    myvalues = []

    for i in range(0,5):
        myresult = cursor.fetchone()
        mynames.append(myresult[0])
        myvalues.append(myresult[5])

         
    embed = discord.Embed(
        title=":red_circle: **Top 5 incidence counties**",
        color=15859792
    )
    embed.add_field(name=mynames[0], value=f"👉 Inzidenz: {str(myvalues[0])}", inline=False)

    embed.add_field(name="** ** ", value="** ** ", inline=False)

    embed.add_field(name=mynames[1], value=f"👉 Inzidenz: {str(myvalues[1])}", inline=False)

    embed.add_field(name="** ** ", value="** ** ", inline=False)

    embed.add_field(name=mynames[2], value=f"👉 Inzidenz: {str(myvalues[2])}", inline=False)

    embed.add_field(name="** ** ", value="** ** ", inline=False)

    embed.add_field(name=mynames[3], value=f"👉 Inzidenz: {str(myvalues[3])}", inline=False)

    embed.add_field(name="** ** ", value="** ** ", inline=False)

    embed.add_field(name=mynames[4], value=f"👉 Inzidenz: {str(myvalues[4])}", inline=False)

    
    mydb.close()
    return embed

def SQLadding():

    mydb = SQLconnect() #connects to SQL server    
    cursor = mydb.cursor()  

    datetime_1 = datetime.now()
    currentdate = datetime_1.date()
    
    
    #sql_select_query  =   #SQL query

    sql_select_query  = """SELECT * FROM landkreis ORDER BY Zuletzt_geupdatet"""  #SQL query
    cursor.execute(sql_select_query)    #takes input from DiscordBot and puts in in %s above
    myresult = cursor.fetchall()
    for x in myresult:
        if currentdate == x[6]:
            print("already upto date")
            return
        else:                     
            r = requests.get(API_URL)
            res = r.json()
            countydata = res["features"]
            length = len(list(countydata))

            for i in range(0, length):
                for channel in countydata[i].values():  #takes JSON data and extracts values
                    Stadtname = channel['GEN']
                    Kreis = channel['BEZ']
                    Bundesland = channel['BL']
                    Faelle = channel['cases']
                    Tode= channel['deaths']
                    Inzidenz = channel['cases7_per_100k_txt'].replace(',','.')
                    Zuletzt_geupdatet = channel['last_update']
                    day = Zuletzt_geupdatet[0:2]
                    month = Zuletzt_geupdatet[3:5]
                    year = Zuletzt_geupdatet[6:10]
                    date = (year + "-" + month + "-" + day) #conversion to american date format (yyyy-mm-dd)

                    sql_command = """INSERT INTO landkreis (Stadtname, Kreis, Bundesland, Faelle, Tode, Inzidenz, Zuletzt_geupdatet)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);"""
                                
                    data=  (Stadtname, Kreis, Bundesland, Faelle, Tode, Inzidenz, date)
                    cursor.execute(sql_command, data)
                
            mydb.commit()
            mydb.close()
            
        return

def statesearch(state):

    mydb = SQLconnect() #connects to SQL server    
    cursor = mydb.cursor()  

    datetime_1 = datetime.now()
    currentdate = datetime_1.date()
    

    sql_select_query  = """SELECT * FROM landkreis WHERE Bundesland = %s AND Zuletzt_geupdatet = %s"""  #SQL query

    cursor.execute(sql_select_query,(state, currentdate,))    #takes input from DiscordBot and puts in in %s above

    myresult = cursor.fetchall()  #actually commit query

    cursor.close()
    mydb.close()

    cases = []
    death = []


    for x in myresult:      #search trough results of query
        
        cases.append(int(x[3]))
        death.append(int(x[4]))
 

    embed = discord.Embed(
        title=f"**{state}**",
        
    )
    embed.add_field(name="👥 Fälle (Gesamt)", value=sum(cases), inline=True)
    embed.add_field(name="☠️ Tode (Gesamt)", value=sum(death), inline=True)

    return embed

    
#%% 