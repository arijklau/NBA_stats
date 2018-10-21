'''
Since my fantasy commissioner changed our setting to week-long lineups, I have to come up with some way
to pick the best lineup for each week, leaving out 5 players.
My strategy will be to use the season-long NBA schedule, Ranking my players based on scoring avg*num games
that week and picking the top 10 to feature that week. If two players are closely ranked, one with a smaller
variance will probably win out for my lineup.
'''
from datetime import datetime

#store full schedule in one massive array
def get_full_schedule():
    f = open("nba-2018-EasternStandardTime.csv")
    schedule = []
    for line in f:
        schedule.append(line.strip().split(','))

    f.close()

    return schedule

full_schedule = get_full_schedule()

#get given team's schedule for a date range (in dd/mm/yyyy format)
def get_team_sched(team, start_date, finish_date):

    team_sched = []

    #convert string dates to datetime objects
    dt_start = datetime.strptime(start_date, "%d/%m/%Y")
    dt_end =  datetime.strptime(finish_date, "%d/%m/%Y")

    for line in full_schedule:
        d_and_t = line[1].strip().split(' ') #have to split since line[1] includes date and start time of game
        date = d_and_t[0]
        dt_date = datetime.strptime(date, "%d/%m/%Y")

        if(dt_date >= dt_start and dt_date <= dt_end): #is current game within the date range
            if(team == line[3]): #team is home team
                team_sched.append(line[4]) #add opponent (away team) to sched
            elif(team == line[4]): #team is away team
                team_sched.append(line[3]) #add opponent (home team) to sched


    return team_sched

def rank_players(start, finish):
    #[player, team, scoring average]
    players = [
        ['Damian Lillard', 'Portland Trail Blazers', 47.0],
        ['Jrue Holiday', 'New Orleans Pelicans', 26.0],
        ['Tim Hardaway', 'New York Knicks', 34.0],
        ['Taj Gibson', 'Minnesota Timberwolves', 18.7],
        ['Nikola Jokic', 'Denver Nuggets', 59.0],
        ['Kemba Walker', 'Charlotte Hornets', 43.3],
        ['Taurean Prince', 'Atlanta Hawks', 32.5],
        ['Eric Bledsoe', 'Milwaukee Bucks', 26.5],
        ['Steven Adams', 'Oklahoma City Thunder', 39.5],
        ['Derrick Rose', 'Minnesota Timberwolves', 26.0],
        ['Dwight Howard', 'Washington Wizards', 0.0],
        ['Serge Ibaka', 'Toronto Raptors', 26.7],
        ['Brandon Ingram', 'Los Angeles Lakers', 19.5],
        ['Otto Porter', 'Washington Wizards', 20.5],
        ['Dario Saric', 'Philadelphia 76ers', 17.7],
        ['Evan Fournier', 'Orlando Magic', 18.7]
    ]

    for player in players:
        week = get_team_sched(player[1], start, finish) #get the player's schedule for given week
        player.append(len(week)) #add number of games that week as 4th element in player's info
        #now it is [player, team, scoring average, num games this week]

    return sorted(players, key=lambda player: player[2]*player[3], reverse=True) #return sorted list based on avg*num games



arr = get_team_sched("Portland Trail Blazers", "29/10/2018", "4/11/2018")
print(arr)
weekly_rank = rank_players("22/10/2018", "28/10/2018")

for i in range(len(weekly_rank)):
    print(i+1,"-", weekly_rank[i])
