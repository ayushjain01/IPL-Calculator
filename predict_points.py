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
colors = {"RCB": "#D5152C", "GT": "#1C2234", "SRH": "#E34633", "CSK": "#FFD230", "DC": "#32579D",
          "KKR": "#3D245D", "LSG": "#2956C9", "MI": "#285290", "RR": "#264AA5", "PBKS": "#DD212E"}
fcolors = {"RCB": "#000000", "GT": "#ffffff", "SRH": "#000000", "CSK": "#000000", "DC": "#ffffff",
           "KKR": "#ffffff", "LSG": "#000000", "MI": "#ffffff", "RR": "#ffffff", "PBKS": "#000000"}

def fix_overs(no_overs):
    no_overs = str(round(no_overs, 1))
    new = no_overs.split(".")
    if int(new[1]) >= 6:
        if new[0] == "19":
            return 20.0
        else:
            overs = float(new[0]) + 1
            return overs
    else:
        return float(no_overs)


def add_overs(overs1, overs2):
    new = overs1 + overs2
    overs = str(new).split(".")
    if int(overs[1]) >= 6:
        overs[0] = str(int(overs[0]) + 1)
        overs[1] = str(int(overs[1]) - 6)
    return float(".".join(overs))


def find_scores(avg_score_win_for, avg_score_win_ag, avg_score_lose_for, avg_score_lose_ag):
    win_for_runs = avg_score_win_for[0]
    win_for_overs = avg_score_win_for[1]
    win_ag_runs = avg_score_win_ag[0]
    win_ag_overs = avg_score_win_ag[1]
    lose_for_runs = avg_score_lose_for[0]
    lose_for_overs = avg_score_lose_for[1]
    lose_ag_runs = avg_score_lose_ag[0]
    lose_ag_overs = avg_score_lose_ag[1]
    win_score_runs = max(win_for_runs, lose_ag_runs)
    win_score_overs = max(win_for_overs, lose_ag_overs)
    lose_score_runs = min(lose_for_runs, win_ag_runs)
    lose_score_overs = max(lose_for_overs, win_ag_overs)
    if win_score_runs < lose_score_runs:
        win_score_runs, lose_score_runs = lose_score_runs, win_score_runs
    return win_score_runs, lose_score_runs, win_score_overs, lose_score_overs


def get_perf(team, scoreF, scoreA):
    performance = {}
    for i in range(len(team)):
        a, b = scoreF[i].split('/')
        c, d = scoreA[i].split('/')
        a = int(a)
        b = round(float(b), 1)
        c = int(c)
        d = round(float(d), 1)
        performance[team[i]] = [a, b, c, d]
    return performance


def get_nrr(avg_score_for, avg_score_ag):
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
    row = ""


def add_to_table(table, table_count):
    content = Element("copy-content")
    content.element.style.display = "block"
    row = """
    <p class="title-para" id="scenario-table">Final Points Table - </p>
            <table id="table-later">
                <thead>
                    <tr>
                        <th>POS</th>
                        <th>TEAM</th>
                        <th>P</th>
                        <th>W</th>
                        <th>L</th>
                        <th>NR</th>
                        <th>NNR</th>
                        <th>PTS</th>
                    </tr>
                </thead>
                <tbody id="points-data">
    """

    for i in range(len(table)):
        row = row + f"""
    <tr>
        <td>{i+1}</td>
        <td>{table[i][0]}</td>
        <td>{table[i][1]}</td>
        <td>{table[i][2]}</td>
        <td>{table[i][3]}</td>
        <td>{table[i][4]}</td>
        <td>{round(table[i][5],3)}</td>
        <td>{table[i][6]}</td>
    </tr>
    """
    
    row += """</tbody>
            </table>
            <br>
            <hr>"""
    content.element.innerHTML += row


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


def assign_points(team_name, wins, loses, table):
    for i in range(len(wins)):
        # Team    P  W  L  NR   NRR  PTS
        # ['GT', 11, 8, 3, 0, 0.951, 16]
        #  0     1  2  3  4    5     6
        table_dict = make_dict(table)

        win_team = list(table_dict[wins[i]])
        lose_time = list(table_dict[loses[i]])
        performance = get_perf(team, scoreF, scoreA)
        avg_score_win_for = [round(
            performance[wins[i]][0]/win_team[1]), fix_overs(performance[wins[i]][1]/win_team[1])]
        avg_score_win_ag = [round(performance[wins[i]][2]/win_team[1]),
                            fix_overs(performance[wins[i]][3]/win_team[1])]
        avg_score_lose_for = [round(
            performance[loses[i]][0]/lose_time[1]), fix_overs(performance[loses[i]][1]/lose_time[1])]
        avg_score_lose_ag = [round(performance[loses[i]][2]/lose_time[1]),
                             fix_overs(performance[loses[i]][3]/lose_time[1])]
        win_score_runs, lose_score_runs, win_score_overs, lose_score_overs = find_scores(
            avg_score_win_for, avg_score_win_ag, avg_score_lose_for, avg_score_lose_ag)

        performance[wins[i]][0] += win_score_runs
        performance[wins[i]][1] = add_overs(
            performance[wins[i]][1], win_score_overs)
        performance[loses[i]][2] += win_score_runs
        performance[loses[i]][3] = add_overs(
            performance[loses[i]][3], win_score_overs)

        performance[loses[i]][0] += lose_score_runs
        performance[loses[i]][1] = add_overs(
            performance[loses[i]][1], lose_score_overs)
        performance[wins[i]][2] += lose_score_runs
        performance[wins[i]][3] = add_overs(
            performance[wins[i]][3], lose_score_overs)

        win_team[1] += 1
        win_team[2] += 1
        win_team[6] += 2
        lose_time[1] += 1
        lose_time[3] += 1
        score_win_for = [performance[wins[i]][0], performance[wins[i]][1]]
        score_win_ag = [performance[wins[i]][2], performance[wins[i]][3]]
        score_lose_for = [performance[loses[i]][0], performance[loses[i]][1]]
        score_lose_ag = [performance[loses[i]][2], performance[loses[i]][3]]
        win_nrr_new = get_nrr(score_win_for, score_win_ag)
        lose_nrr_new = get_nrr(score_lose_for, score_lose_ag)
        if win_nrr_new < 0:
            win_nrr_new *= -1
        if lose_nrr_new > 0:
            lose_nrr_new *= -1
        win_team[5] += win_nrr_new
        lose_time[5] += lose_nrr_new
        table_dict[wins[i]] = win_team
        table_dict[loses[i]] = lose_time
        table = list(table_dict.values())

    return table


def team_wins(team, teams1, teams2, wins, table_count):
    content = Element("copy-content")
    content.element.style.display = "block"
    content_text = f"""<br>
            <p class="title-para" style="background-color:{colors[team]};color:{fcolors[team]}" id="scenario-number">Scenario - {table_count+1}</p>
            <div id="scenarios">
                <h1>{team} will qualify if -</h1>
                <hr>
            """
    for i in range(len(wins)):
        content_text += f"<p class = 'winner_row'> {wins[i] : <4} wins - {teams1[i] : <4} VS {teams2[i] : <4} </p>"
    content_text += "</div>"
    content.element.innerHTML += content_text
    table_count += 1
    return table_count


def handle_click(event):
    table_count = 0
    resultText = Element("results")
    resultText.element.style.display = "none"
    content = Element("copy-content" )
    content.element.innerHTML = ""
    content.element.style.display = "none"
    global ch, wins, team, qualified
    team_name = Element("teams").element.value
    iterations = Element("iterations").element.value
    ch = 0
    results_printed = False
    teamInd = team.index(team_name)
    # in case, IPL.COM removes the Q sign,
    if qualified[teamInd] == "Yes" or team_name == "GT":
        resultText = Element("results")
        resultText.element.innerHTML = f"Congratulations!🎉 Your team {team_name} has already qualified" + "🥳"
        resultText.element.style.display = "block"
        exit(0)
    for l in range(len(wins)):
        table = reset_table()
        if team_name in loses[l]:
            continue
        table = assign_points(team_name, wins[l], loses[l], table)
        sort_values(table)
        top4 = table[:4]
        for team_q in top4:
            if team_q[0] == team_name:            # printing all tables where RCB qualifies
                table_count = team_wins(team_q[0], teams1, teams2, wins[l], table_count)

                

                print_table(table)
                add_to_table(table, table_count)
                ch = ch + 1
                results_printed = True

                if ch == int(iterations):
                    exit(0)
    if results_printed == False:
        resultText = Element("results")
        resultText.element.innerHTML = f"Sorry🥹 but your team {team_name} cannot qualify this season. Better luck next time."
        resultText.element.style.display = "block"
        exit(0)


ch = 0
table = reset_table()
row = ""
for i in range(len(table)):
    row = row + f"""
<tr>
    <td>{i+1}</td>
    <td>{table[i][0]}</td>
    <td>{table[i][1]}</td>
    <td>{table[i][2]}</td>
    <td>{table[i][3]}</td>
    <td>{table[i][4]}</td>
    <td>{table[i][5]}</td>
    <td>{table[i][6]}</td>
</tr>
"""
pointsbody = Element("points-table")
pointsbody.element.innerHTML = row

df = pd.read_csv(r'data/ipl_fixtures.csv')
teams1 = list(df["team1"])
teams2 = list(df["team2"])
wins, loses = winners(teams1, teams2)
html = ""
for i in range(1, len(wins)):
    if i > 10 or i > 2**len(wins):
        break
    html = html + f"""
<option value="{i}">{i}</option>
"""
iterationsmenu = Element("iterations")
iterationsmenu.element.innerHTML = html

buttons = document.querySelectorAll("#calc-button")
for button in buttons:
    button.onclick = handle_click
