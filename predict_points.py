import pandas as pd
df = pd.read_csv(r'data/points.csv')
qualified = list(df["QUALIFIED"])
team = list(df["TEAM"])
gamesP = list(df["P"])
gamesW = list(df["W"])
gamesL = list(df["L"])
gamesNR = list(df["NR"])
nrr = list(df["NRR"])
pts = list(df["PTS"])
scoreF = list(df["FOR"])
scoreA = list(df["AGAINST"])

def fix_overs(no_overs):
    no_overs = str(round(no_overs,1))
    new = no_overs.split(".")
    if int(new[1]) >= 6:
        if new[0] == "19":
            return 20.0
        else:
            overs = float(new[0]) + 1
            return overs
    else:
        return float(no_overs)

def add_overs(overs1,overs2):
    new = overs1 + overs2
    overs = str(new).split(".")
    if int(overs[1]) >= 6:
        overs[0] = str(int(overs[0]) + 1)
        overs[1] = str(int(overs[1]) - 6)
    return float(".".join(overs))


def find_scores(avg_score_win_for,avg_score_win_ag,avg_score_lose_for,avg_score_lose_ag):
    win_for_runs = avg_score_win_for[0]
    win_for_overs = avg_score_win_for[1]
    win_ag_runs = avg_score_win_ag[0]
    win_ag_overs = avg_score_win_ag[1]
    lose_for_runs = avg_score_lose_for[0]
    lose_for_overs = avg_score_lose_for[1]
    lose_ag_runs = avg_score_lose_ag[0]
    lose_ag_overs = avg_score_lose_ag[1]
    win_score_runs = max(win_for_runs,lose_ag_runs)
    win_score_overs = max(win_for_overs,lose_ag_overs)
    lose_score_runs = min(lose_for_runs,win_ag_runs)
    lose_score_overs = max(lose_for_overs,win_ag_overs)
    if win_score_runs < lose_score_runs:
        win_score_runs,lose_score_runs = lose_score_runs,win_score_runs
    return win_score_runs,lose_score_runs,win_score_overs,lose_score_overs

def get_perf(team,scoreF,scoreA):
    performance = {}
    for i in range(len(team)):
        a, b = scoreF[i].split('/')
        c, d = scoreA[i].split('/')
        a = int(a)
        b = round(float(b),1)
        c = int(c)
        d = round(float(d) ,1)
        performance[team[i]] = [a,b,c,d]
    return performance

def get_nrr(avg_score_for,avg_score_ag):
    nrr_for = avg_score_for[0]/avg_score_for[1]
    nrr_ag = avg_score_ag[0]/avg_score_ag[1]
    return (nrr_for - nrr_ag)/10

def reset_table():
    df = pd.read_csv(r'data/points.csv')
    team = list(df["TEAM"])
    gamesP = list(df["P"])
    gamesW = list(df["W"])
    gamesL = list(df["L"])
    gamesNR = list(df["NR"])
    nrr = list(df["NRR"])
    pts = list(df["PTS"])
    qualified = list(df["QUALIFIED"])
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
        data.append(qualified[i])
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


def assign_points(team_name,wins, loses, table):
    for i in range(len(wins)):
        # Team    P  W  L  NR   NRR  PTS
        # ['GT', 11, 8, 3, 0, 0.951, 16]
        #  0     1  2  3  4    5     6
        table_dict = make_dict(table)

        win_team = list(table_dict[wins[i]])
        lose_time = list(table_dict[loses[i]])
        performance = get_perf(team,scoreF,scoreA)
        avg_score_win_for = [round(performance[wins[i]][0]/win_team[1]), fix_overs(performance[wins[i]][1]/win_team[1])]
        avg_score_win_ag = [round(performance[wins[i]][2]/win_team[1]), fix_overs(performance[wins[i]][3]/win_team[1])]
        avg_score_lose_for = [round(performance[loses[i]][0]/lose_time[1]),fix_overs(performance[loses[i]][1]/lose_time[1])]
        avg_score_lose_ag = [round(performance[loses[i]][2]/lose_time[1]), fix_overs(performance[loses[i]][3]/lose_time[1])]
        print("BEFORE MATCH - ",avg_score_win_for,avg_score_win_ag,avg_score_lose_for,avg_score_lose_ag)
        win_score_runs,lose_score_runs,win_score_overs,lose_score_overs = find_scores(avg_score_win_for,avg_score_win_ag,avg_score_lose_for,avg_score_lose_ag)
        
        performance[wins[i]][0] += win_score_runs
        performance[wins[i]][1] = add_overs(performance[wins[i]][1],win_score_overs)
        performance[loses[i]][2] += win_score_runs
        performance[loses[i]][3] = add_overs(performance[loses[i]][3],win_score_overs)

        performance[loses[i]][0] += lose_score_runs
        performance[loses[i]][1] = add_overs(performance[loses[i]][1],lose_score_overs)
        performance[wins[i]][2] += lose_score_runs
        performance[wins[i]][3] = add_overs(performance[wins[i]][3],lose_score_overs)

        win_team[1] += 1
        win_team[2] += 1
        win_team[6] += 2
        lose_time[1] += 1
        lose_time[3] += 1
        score_win_for = [performance[wins[i]][0], performance[wins[i]][1]]
        score_win_ag = [performance[wins[i]][2], performance[wins[i]][3]]
        score_lose_for = [performance[loses[i]][0],performance[loses[i]][1]]
        score_lose_ag = [performance[loses[i]][2], performance[loses[i]][3]]
        print(f"Current NRR - {win_team[5]}, {lose_time[5]}")
        win_nrr_new = get_nrr(score_win_for,score_win_ag) 
        lose_nrr_new = get_nrr(score_lose_for,score_lose_ag)
        if win_nrr_new < 0:
            win_nrr_new *= -1
        if lose_nrr_new > 0:
            lose_nrr_new *= -1
        win_team[5] += win_nrr_new
        lose_time[5] += lose_nrr_new
        table_dict[wins[i]] = win_team
        table_dict[loses[i]] = lose_time
        print(f"{win_team[0]} scores {win_score_runs} in {win_score_overs} and {lose_time[0]} scores {lose_score_runs} in {lose_score_overs}, {win_team[5]}, {lose_time[5]}")
        print("AFTER MATCH - ",avg_score_win_for,avg_score_win_ag,avg_score_lose_for,avg_score_lose_ag)

        table = list(table_dict.values())

    return table


def team_wins(team,teams1, teams2, wins):
    print(f"{team} WILL QUALIFY IF - ")
    for i in range(len(wins)):
        print(f"{wins[i] : ^4} wins - {teams1[i] : ^4} VS {teams2[i] : ^4}")


def handle_click(event):
    global ch,wins,team,qualified
    team_name = Element("teams").element.value
    iterations = Element("iterations").element.value
    print(team_name, iterations)
    ch = 0
    results_printed = False
    teamInd = team.index(team_name)
    if qualified[teamInd] == "Yes":
        print(f"Congratulations! Your team {team_name} has already qualified")
        exit(0)
    for l in range(len(wins)):
        table = reset_table()
        if team_name in loses[l]:
            continue
        table = assign_points(team_name,wins[l], loses[l], table)
        sort_values(table)
        top4 = table[:4]
        for team_q in top4:
            if team_q[0] == team_name:            # printing all tables where RCB qualifies
                team_wins(team_q[0],teams1, teams2, wins[l])
                print(
                    F"______________________________________________________ITERATION - {ch}______________________________________________________")
                print(f"POINTS TABLE AFTER {team_name} QUALIFIES - ")
                print_table(table)
                print(
                    "NOTE THAT THE RESULTS CAN CHANGE BASED ON THE NRR, THIS PROGRAM ASSUMES THE CHANGE IN NRR TO BE +- 0.05 ONLY")
                ch = ch + 1
                results_printed = True

                if ch == int(iterations):
                    exit(0)
    if results_printed == False:
        print(f"Sorry but your team {team_name} cannot qualify this season. Better luck next time.")
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
