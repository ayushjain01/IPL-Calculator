import pandas as pd
df = pd.read_csv(r'data/points.csv')
team = list(df["TEAM"])
gamesP = list(df["P"])
gamesW = list(df["W"])
gamesL = list(df["L"])
gamesNR = list(df["NR"])
nrr = list(df["NRR"])
pts = list(df["PTS"])


def reset_table():
    df = pd.read_csv(r'data/points.csv')
    team = list(df["TEAM"])
    gamesP = list(df["P"])
    gamesW = list(df["W"])
    gamesL = list(df["L"])
    gamesNR = list(df["NR"])
    nrr = list(df["NRR"])
    pts = list(df["PTS"])
    table = []
    for i in range(len(team)):
        data = []
        data.append(team[i])
        data.append(gamesP[i])
        data.append(gamesW[i])
        data.append(gamesL[i])
        data.append(gamesNR[i])
        data.append(nrr[i])
        data.append(pts[i])
        table.append(data)
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
        print(
            f"|{count : ^5}|{i[0] : ^6}|{i[1] : ^5}|{i[2] : ^5}|{i[3] : ^5}|{i[4] : ^6}|{i[5] : ^9.3f}|{i[6] : ^7}|")
        count += 1
    print("|-------------------------------------------------------|")


def winners(teams1, teams2):
    possible_winners = []
    possible_losers = []
    for i in range(2**len(teams1)):
        winner = []
        loser = []
        for j in range(len(teams1)):
            if i & (1 << j):
                winner.append(teams2[j])
                loser.append(teams1[j])
            else:
                winner.append(teams1[j])
                loser.append(teams2[j])
        possible_winners.append(winner)
        possible_losers.append(loser)
    return possible_winners, possible_losers


def assign_points(wins, loses, table_dict):
    for i in range(len(wins)):
        # Team    P  W  L  NR   NRR  PTS
        # ['GT', 11, 8, 3, 0, 0.951, 16]
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


def handle_click(event):
    global ch
    team_name = Element("teams").element.value
    iterations = Element("iterations").element.value
    print(team_name, iterations)
    for l in range(len(wins)):
        table = reset_table()
        table_dict = make_dict(table)
        table = assign_points(wins[l], loses[l], table_dict)
        sort_values(table)
        top4 = table[:4]

        for team in top4:
            if team[0] == team_name:            # printing all tables where RCB qualifies
                rcb_wins(teams1, teams2, wins[l])
                print(
                    F"______________________________________________________ITERATION - {ch}______________________________________________________")
                print(f"POINTS TABLE AFTER {team_name} QUALIFIES - ")
                print_table(table)
                print(
                    "NOTE THAT THE RESULTS CAN CHANGE BASED ON THE NRR, THIS PROGRAM ASSUMES THE CHANGE IN NRR TO BE +- 0.05 ONLY")
                ch = ch + 1
                if ch == int(iterations):
                    exit(0)


ch = 0
table = reset_table()
print("CURRENT STANDINGS - ")
print_table(table)
df = pd.read_csv(r'data/ipl_fixtures.csv')
teams1 = list(df["team1"])
teams2 = list(df["team2"])
wins, loses = winners(teams1, teams2)
html = ""
for i in range(1, len(wins)):
    if i > 10:
        break
    html = html + f"""
<option value="{i}">{i}</option>
"""
iterationsmenu = Element("iterations")
iterationsmenu.element.innerHTML = html

buttons = document.querySelectorAll("#calc-button")
for button in buttons:
    print(button)
    button.onclick = handle_click
