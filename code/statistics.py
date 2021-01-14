import discord
import os
from time import time

def top5():

    highinzidenz = []
    names = []

    counties = []

    with open(r"E:\VSC\Inzidenz\code\RKIData.csv") as file:
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
