# Discord bot, cumulative incidence values germany

## Table of contents
* [General info](#general-info)
* [Features](#Features)
* [Setup](#Setup)
* [To-Do](#To-Do)

## General info
This is a discord bot (see Features for function). Messages that start with "😷" let's the program search for the cumulative incidence values in the city that is typed behind the emoji. !update, updates the values in the csv file. Should be executed once a day.

## Features

Creates a discord bot that responds to "😷", if a name of a german countie is typed after the "😷" the bot will search trough the newest cumulative incidence values in that countie or city and post it in the channel. It can also return the 5 counties that have the highest cumulative incidence values by typing "😷!top5". "😷!update" will update incidence values. It's recommended to update it everyday especially to make sure the upcoming statistics module will work well with the SQL server.

## Setup

Create a mySQL (I used MariaDB) server and create a database names "mydatabase". The table will be automatically configured once the program is started. Also it should be remembered to add username and password of the SQL database to the .env file.

## To-Do
* Use some more statistics 
