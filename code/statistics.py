import WebScraping
import DiscordBot

import mysql.connector
import discord
import os
from time import time
from dotenv import load_dotenv
import os

import requests
import json

import numpy as np
import pandas as pd
import matplotlib as mpl 
import matplotlib.pyplot as plt

CSV_FILE_NAME = "RKIData.csv"
API_URL = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&outSR=4326&f=json"

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

    highinzidenz = []
    names = []

    counties = []
    if os.path.exists(CSV_FILE_NAME):
        with open(CSV_FILE_NAME) as file:
    
            next (file)             #remove first line
            for line in file:
                splittedlines = line.split(",")
                inzidenz = float(splittedlines[5])      #looks at incindence values and converts it to float
                if inzidenz >= 200: #checks if float is higher than 200
                    highinzidenz.append(inzidenz) 
                    names.append(splittedlines[0])       #takes the county of the corresponding and appends it

        dictionary = dict(zip(names, highinzidenz))     #combines list to dictionary

        sorteddictionary = {key: value for key, value in sorted(dictionary.items(), key=lambda ele: ele[1], reverse = True)}   
        #sorts the dictionary so that the highest incidence is at first spot

        x = 0
        for item in sorteddictionary:    
            if x < 5: #counts trough first 5 (5 highest) values
                highestcounties = "{}".format(item)
                x = x + 1
                
                counties.append(highestcounties)    #appends names the 5 counties with highest incidence           

        return counties

def SQLadding():

    mydb = SQLconnect()
    cursor = mydb.cursor()
    
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

def stats(county):

    try: 
        os.remove('saved_figure.png')   #remove old img data
    except:
        print("img doesn't exist")
    finally:

        mydb = SQLconnect() #connects to SQL server
        mycursor = mydb.cursor()

        sql_select_query  = """SELECT * FROM landkreis WHERE Stadtname = %s"""  #SQL query
        mycursor.execute(sql_select_query,(county,))    #takes input from DiscordBotDebug and puts in in %s above

        myresult = mycursor.fetchall()  #actually commit query

        date = []
        incidence = []

        for x in myresult:      #search trough results of query
            
            date.append(str(x[6]))      
            incidence.append(float(x[5]))

        d = {'x': date, 'y': np.array(incidence)}   #create numpy array
                
        df = pd.DataFrame(d)            #create panda dataframe
       
        df.plot(x = "x", y = "y", kind="bar")   #plotting stats
        plt.title('Inzidenzwert über mehrere Tage/Wochen')  #name axis and title
        plt.ylabel('Inzidenzfälle')
        plt.xlabel('Datum')       

        plt.savefig('saved_figure.png') #saves plot as img
        imgdata = 'saved_figure.png'    #save and return the img path file
        print("hello")
        return imgdata

#%% 