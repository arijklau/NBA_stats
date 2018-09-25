'''
LEGEND:
1 Year,        21 blanl,          41 FT,
2 Player,      22 OWS,            42 FTA,
3 Pos,         23 DWS,            43 FT%,
4 Age,         24 WS,             44 ORB,
5 Tm,          25 WS/48,          45 DRB,
6 G,           26 blank2,         46 TRB,
7 GS,          27 OBPM,           47 AST,
8 MP,          28 DBPM,           48 STL,
9 PER,         29 BPM,            49 BLK,
10 TS%,        30 VORP,           50 TOV,
11 3PAr,       31 FG,             51 PF,
12 FTr,        32 FGA,            52 PTS
13 ORB%,       33 FG%,
14 DRB%,       32 3P,
15 TRB%,       35 3PA,
16 AST%,       36 3P%,
17 STL%,       37 2P,
18 BLK%,       38 2PA,
19 TOV%,       39 2P%,
20 USG%,       40 eFG%,
'''
import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model
import operator
import math




def get_data():
    f = open("Seasons_Stats.csv") #csv data file
    data = [] #initialize array to split up csv into
    players = []#initialize array to place relevant data (players who are actually in the league) into
    for line in f:
        data.append(line.strip().split(',')) #split csv up into array


    f.close() #close file

    for i in data:
        try:
            if(int(i[1]) > 2004):
                players.append(i) #if player was in the league in 2010 or after, place
                                  #them into players[] array
        except:
            ValueError  #sometimes there are blanks in the data file


    return players #return relevant data

def make_map():
    #this function is to make it easy to grab a player from the array and score a specific season
    data_map = {} #initialize map
    data = get_data() #get relevant player data

    for i in data:
        key = i[2], int(i[1]) #keys are player (index 2) and year (index 1)
        value = i[3:53]   #value returns all other stats for the player's given season
        data_map[key] = value #add key:val pairs to the map

    return data_map #return the filled map

def get_fantasy_score(data, player, year):
    #use hashmap i.e. "arron afflalo", 2010: stats...
    #pts - 1, dreb - 1, oreb - 2, ast - 1, stl - 2, blk - 2, fgm/ftm -> 1, fgmi/ftmi -> (-1), to -> (-1)
    #fouls -> -1
    # ^scoring settings subject to change, don't remember what actual settings were so can
    #change later on

    #data_map = make_map() #get map (player/year:stats)
    score = 0 #initialize score

    try:
        stats = data[player, year]  #data_map[player, year] #get player's stats for given season
        #print("Player: ", player)
        #print("Season: ", year)
    except:
        KeyError
        #print("Player or Season not found in dictionary")
        return 0

    for i in range(0, len(stats)): #convert relevant stats to floats (for math ops)
        try:
            stats[i] = float(stats[i])
        except:
            ValueError

    #here just storing all the stats as constants to add up for total fantasy score
    games = stats[3] #games played
    ppg = stats[49]/games #points per game (total points/games played)
    orpg = stats[41]/games #off. rebs
    drpg = stats[42]/games #def. rebs
    ast = stats[44]/games #assists
    stl = stats[45]/games #steals
    blk = stats[46]/games #blocks
    fgm = stats[28]/games #fg made
    fgmi = (stats[29] - stats[28])/games #fg missed
    ftm = stats[38]/games #ft made
    ftmi = (stats[39] - stats[38])/games #ft missed
    tov = stats[47]/games #turnovers
    foul = stats[48]/games #personal fouls

    score += ppg + 2*orpg + drpg + ast + 2*stl + 2*blk + fgm + ftm - fgmi - ftmi - tov - foul
    #score = round(score, 1) #round score to 1 decimal point

    return score


def regression(stats, player):
    #Don't know which stats are most indicative of future fantasy success/failure,
    #so perhaps do regression on a variety of combinations of the 45+ statistics? (later on lol)

     #start with only stats counted in fantasy score. Can mess around with other stats after
    x = []
    xfit = []
    y = []

    #add yearly fantasy scores to y array, run OLS on year vs. score to get slope/intercept of line
    for i in range(1, 13):
        pnt = get_fantasy_score(stats, player, i + 2004) #starting 2005, up to 2016
        if(pnt != 0):
            xfit.append([1, i])
            x.append(i)
            y.append(pnt)

    reg = linear_model.LinearRegression()
    try:
        reg.fit(xfit, y)
        #x - years, y - scores, coefficient and y intercept
        return x, y, reg.coef_, reg.intercept_
    except:
        ValueError
        return 0



def predict_score(stats, player):
    #given a player, get their fantasy scores from the past several seasons (13 max, others
    #depends how long they've been in the league), and get the value for the next year (2017)

    try:
        x, y, theta, epsilon = regression(stats, player) #get arrays, slope, intercept of line
        predicted = 13*theta[1] + epsilon #year after data stops (2018, 15th year after start of data)
    except:
        TypeError
        predicted = 0

    return predicted #return predicted score rounded to 2 decimals

def score_and_rank():
    #systematically go through player data, getting yearly fantasy scores for each player,
    #find line of best fit, predict 2017 fantasy score, then rank players based on 2017 score

    raw_players = get_data() #all players and years so most players repeated multiple times
    player_list = []
    for i in range(len(raw_players)): #add player only once to new array to avoid repeats
        if(raw_players[i][2] not in player_list):
            player_list.append(raw_players[i][2])

    map = make_map()
    rankings = []

    for i in range(len(player_list)):
        player = player_list[i] #get player from array
        #print(player)
        predicted = predict_score(map, player) #predict player's 2017 score
        actual = get_fantasy_score(map, player, 2017) #player's actual 2017 score

        try:
            if(actual < predicted):
                error = actual/predicted
            else:
                error = predicted/actual
        except:
            ZeroDivisionError

        if(actual != 0 and predicted != 0 and actual > 0 and predicted > 0): #if actual = 0 then player was not in the league in 2017, predicted = 0 means player is rookie
            rankings.append([player, round(predicted, 2), round(actual, 2), round(error, 2)]) #add to rankings (unsorted), actual rounded to 2 decimals

    rankings.sort(key=lambda x: x[3]) #sort by error

    return rankings

def scoring_accuracy():
    #take difference between predicted scores and actual 2017 scores, sum and divide by total number of players
    #get stats on how many players' predicted were within 5, 10, 15, etc. of actual?

    sum_err = 0 #sum of error

    #how many players had a prediction accuracy greater than (or less than) these benchmarks
    below_sixty = 0
    above_sixty = 0
    above_seventy = 0
    above_eighty = 0
    above_ninety = 0

    rankings = score_and_rank() #get list of all predicted/actual scores
    for i in range(len(rankings)):
        accuracy = rankings[i][3] #set constant

        sum_err += accuracy #add error for each player to sum

        if(accuracy < .60):
            below_sixty += 1
        if(accuracy > .60):
            above_sixty += 1
        if(accuracy > .70):
            above_seventy += 1
        if(accuracy > .80):
            above_eighty += 1
        if(accuracy > .90):
            above_ninety += 1


    num_players = len(rankings)
    error = sum_err/num_players



    return {"error": error,
            "Accuracy <60%": round(below_sixty/num_players, 2),
            "Accuracy >60%": round(above_sixty/num_players, 2),
            "Accuracy >70%": round(above_seventy/num_players, 2),
            "Accuracy >80%": round(above_eighty/num_players, 2),
            "Accuracy >90%": round(above_ninety/num_players, 2)}



def main():

   data_map = make_map() #get map (player/year:stats)

   x, y, theta, epsilon = regression(data_map, "LeBron James")
   y1 = theta[1]
   y2 = 15*theta[1]
   xarr = [1, 15]
   yarr = [y1 + epsilon, y2 + epsilon]

   #print(predict_score(data_map, "LeBron James"))

   #plt.xlim(0, 15)
   #plt.ylim(0, 70)
   #plt.xlabel("2005 to 2016")
   #plt.plot(x, y, ".", color="black")
   #plt.plot(xarr, yarr, color="red")
   #plt.grid()
   #plt.show()

   rankings = score_and_rank()
   #for i in rankings:
    #print(i)

   print(scoring_accuracy())


   return 0



#run it
main()






