import pandas as pd

def reset_table():
    table = [['GT', 11, 8, 3, 0, 0.951, 16], ['CSK', 12, 7, 4, 1, 0.493, 15], ['RR', 12, 6, 6, 0, 0.633, 12], ['MI', 11, 6, 5, 0, -0.255, 12], ['LSG', 11, 5, 5, 1, 0.294, 11], ['RCB', 11, 5, 6, 0, -0.345, 10], ['KKR', 12, 5, 7, 0, -0.357, 10], ['PBKS', 11, 5, 6, 0, -0.441, 10], ['SRH', 10, 4, 6, 0, -0.472, 8], ['DC', 11, 4, 7, 0, -0.605, 8]]
    return table

def make_dict(table):
    table_dict = {}
    for i in table:
        table_dict[i[0]] = i
    return table_dict

def sort_values(values):
    for ind in range(len(values)):
        min_index = ind
        for j in range(ind + 1, len(values)):
            # select the minimum element in every iteration
            if values[j][6] < values[min_index][6]:
                min_index = j
            elif values[j][6] == values[min_index][6]:
                if values[j][5] < values[min_index][5]:
                    min_index = j
         # swapping the elements to sort the array
        (values[ind], values[min_index]) = (values[min_index], values[ind])
    values.reverse()


def print_table(table):
    print("|-------------------------------------------------------|")
    print("| POS | TEAM |  P  |  W  |  L  |  NR  |   NNR   |  PTS  | ")
    print("|-------------------------------------------------------|")
    count = 1
    for i in table:
        print(f"|{count : ^5}|{i[0] : ^6}|{i[1] : ^5}|{i[2] : ^5}|{i[3] : ^5}|{i[4] : ^6}|{i[5] : ^9.3f}|{i[6] : ^7}|")
        count += 1
    print("|-------------------------------------------------------|")

def winners(teams1,teams2):
    possible_winners = []
    possible_losers = []
    for i in range(2**len(teams1)):
        winner = []
        loser = []
        for j in range(len(teams1)):
            if i & (1<<j):
                winner.append(teams2[j])
                loser.append(teams1[j])
            else:
                winner.append(teams1[j])
                loser.append(teams2[j])
        possible_winners.append(winner)
        possible_losers.append(loser)
    return possible_winners, possible_losers

def assign_points(wins,loses,table_dict):
    for i in range(len(wins)):
        #Team    P  W  L  NR   NRR  PTS
        #['GT', 11, 8, 3, 0, 0.951, 16]
        #  0     1  2  3  4    5     6
        win_team = list(table_dict[wins[i]])
        lose_time = list(table_dict[loses[i]])
        win_team[1] += 1                    
        win_team[2] += 1
        win_team[5] += 0.05    # avg nrr improvement after winning = +0.05
        win_team[6] += 2
        lose_time[1] += 1
        lose_time[3] += 1
        lose_time[5] -= 0.05    # avg nrr deterioration after winning = -0.05
        table_dict[wins[i]] = win_team
        table_dict[loses[i]] = lose_time
        table = list(table_dict.values())
    return table

def rcb_wins(teams1, teams2, wins):
    print("RCB WILL QUALIFY IF - ")
    for i in range(len(wins)):
        print(f"{wins[i] : ^4} wins - {teams1[i] : ^4} VS {teams2[i] : ^4}")

table = reset_table()
print("CUREENT STANDINGS - ")
print_table(table)
df = pd.read_csv('ipl_fixtures.csv')
teams1 = list(df["team1"])
teams2 = list(df["team2"])
wins,loses = winners(teams1,teams2)
for l in range(len(wins)):
    table = reset_table()
    table_dict = make_dict(table)
    table = assign_points(wins[l],loses[l],table_dict)
    sort_values(table)
    top4 = table[:4]
    for team in top4:
        if team[0] == "RCB":            # printing all tables where RCB qualifies
            rcb_wins(teams1,teams2,wins[l])
            print("POINTS TABLE AFTER RCB QUALIFIES - ")
            print_table(table)
            print("NOTE THAT THE RESULTS CAN CHANGE BASED ON THE NRR, THIS PROGRAM ASSUMES THE CHANGE IN NRR TO BE +- 0.05 ONLY")
            print("ENTER Y IF YOU WANT TO CONTINUE : ")
            ch = input(">>>")
            if ch != "Y":
                exit(0)
print("EXECUTION COMPLETED")