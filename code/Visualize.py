#%%
import mysql.connector
import discord

import os
import statistics
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib as mpl 
import matplotlib.pyplot as plt

def stats(county):

    parameter = county[0:1]
    if parameter == "/":
        img = piechart(county[1:])
        
        return img
    else:
        img = barplot(county)
        
        return img


def barplot(county):
    
    try: 
        os.remove('saved_figure.png')   #remove old img data
    except: 
        print("Datei nicht auffindbar")
    finally:

        mydb = statistics.SQLconnect() #connects to SQL server
        mycursor = mydb.cursor()

        sql_select_query  = """SELECT * FROM landkreis WHERE Stadtname = %s"""  #SQL query
        mycursor.execute(sql_select_query,(county,))    #takes input from DiscordBotDebug and puts in in %s above

        myresult = mycursor.fetchall()  #actually commit query

        
        mydb.close()
        date = []
        incidence = []

        for x in myresult:      #search trough results of query
            
            date.append(str(x[6]))      
            incidence.append(float(x[5]))

        d = {'x': date, 'Inzidenzwerte': np.array(incidence)}   #create numpy array
                
        df = pd.DataFrame(d)            #create panda dataframe
       
        df.plot(x = "x", y = "Inzidenzwerte", kind="bar", color="g")   #plotting stats
        plt.xticks(rotation=30, horizontalalignment="center")
        plt.title('Inzidenzwert von ' + county)  #name axis and title
        plt.ylabel('Inzidenzfälle')
        plt.xlabel('Datum')       

        figName = 'saved_figure.png'
        fig = plt.gcf()
        fig.set_size_inches((8.5, 11), forward=False)
        fig.savefig(figName, dpi=500)
        
        imgdata = 'saved_figure.png'    #save and return the img path file
        return imgdata

def piechart(county):
    
    try: 
        os.remove('saved_figure.png')   #remove old img data
    finally:

           
        states = {"Brandenburg": "BB", "Berlin": "BE", 
        "Baden-Württemberg": "BW", "Bayern": "BY", 
        "Bremen": "HB", "Hessen": "HE", "Hamburg": "HH", 
        "Mecklenburg-Vorpommern": "MV", "Niedersachsen": "NI",
        "Nordrhein-Westfalen": "NW", "Rheinland-Pfalz": "RP",
        "Schleswig-Holstein": "SH", "Saarland": "SL",
        "Sachsen": "SN", "Sachsen-Anhalt": "ST", "Thüringen": "TH"}

        
        if county in states: 

            cases, deaths = statepiechart(county)

        elif county in states.values():

            key_list = list(states.keys())
            val_list = list(states.values())

            position = val_list.index(county)
            state = key_list[position]

            cases, deaths = statepiechart(state)        

        else:

            querysearch = county

        
            mydb = statistics.SQLconnect() #connects to SQL server
            mycursor = mydb.cursor()

            date_now  = datetime.now()
            currentdate = date_now.date()
            sql_select_query  = """SELECT * FROM landkreis WHERE Zuletzt_geupdatet = %s AND Stadtname = %s"""  #SQL query 
            mycursor.execute(sql_select_query,(currentdate, querysearch,))    #takes input from DiscordBotDebug and puts in in %s above
                                            
            myresult = mycursor.fetchall()  #actually commit query

            
            mydb.close()
            
            cases = []
            deaths = []

            for x in myresult:      #search trough results of query
                
                cases.append(int(x[3]))      
                deaths.append(int(x[4]))

        string1 = f" Fälle: {str(sum(cases))}"
        string2 = f" Tode: {str(sum(deaths))}"

        d = {'Kategorien': [string1, string2], county: [sum(cases), sum(deaths)]}

        df = pd.DataFrame(d)

        df.groupby(['Kategorien']).sum().plot(kind='pie', y=county, startangle=90)
        plt.title('Verhältnis Fälle/Tode von ' + county)
        plt.legend(loc ="lower right")
        figName = 'saved_figure.png'
        
        fig = plt.gcf()
        
        fig.savefig(figName, dpi=500)
        
        imgdata = 'saved_figure.png'    #save and return the img path file
        return imgdata

def statepiechart(state):
    
    mydb = statistics.SQLconnect() #connects to SQL server    
    cursor = mydb.cursor()  

    datetime_1 = datetime.now()
    currentdate = datetime_1.date()
    

    sql_select_query  = """SELECT * FROM landkreis WHERE Bundesland = %s AND Zuletzt_geupdatet = %s"""  #SQL query

    cursor.execute(sql_select_query,(state, currentdate,))    #takes input from DiscordBotDebug and puts in in %s above

    myresult = cursor.fetchall()  #actually commit query

    cursor.close()
    mydb.close()

    cases = []
    death = []
    

    for x in myresult:      #search trough results of query
        
        cases.append(int(x[3]))
        death.append(int(x[4]))   

    return cases,death
#%% 
