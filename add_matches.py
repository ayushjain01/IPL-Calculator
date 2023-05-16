import pandas as pd
df = pd.read_csv(r'data/ipl_fixtures.csv')
teams1 = list(df["team1"])
teams2 = list(df["team2"])
match = list(df["match"])
df2 = pd.read_csv(r'data/points.csv')
team = list(df2["TEAM"])
gamesP = list(df2["P"])
gamesW = list(df2["W"])
gamesL = list(df2["L"])
gamesNR = list(df2["NR"])
nrr = list(df2["NRR"])
pts = list(df2["PTS"])
scoreF = list(df2["FOR"])
scoreA = list(df2["AGAINST"])

html = ""
colors = {"RCB": "#D5152C", "GT": "#1C2234", "SRH": "#E34633", "CSK": "#FFD230", "DC": "#32579D",
          "KKR": "#3D245D", "LSG": "#2956C9", "MI": "#285290", "RR": "#264AA5", "PBKS": "#DD212E"}
fcolors = {"RCB": "#000000", "GT": "#ffffff", "SRH": "#000000", "CSK": "#000000", "DC": "#ffffff",
           "KKR": "#ffffff", "LSG": "#000000", "MI": "#ffffff", "RR": "#ffffff", "PBKS": "#000000"}
match_buttons = {}


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


def handle_click(event):
    global team
    global buttons
    global fcolors

    df2 = pd.read_csv(r'data/points.csv')
    team = list(df2["TEAM"])
    gamesP = list(df2["P"])
    gamesW = list(df2["W"])
    gamesL = list(df2["L"])
    gamesNR = list(df2["NR"])
    nrr = list(df2["NRR"])
    pts = list(df2["PTS"])
    scoreF = list(df2["FOR"])
    scoreA = list(df2["AGAINST"])
    performance = get_perf(team, scoreF, scoreA)
    match, win, lose = event.target.title.split(" | ")

    for button in buttons:

        if button.title == event.target.title:
            match_buttons[match] = (button, win)
            button.style.backgroundColor = colors[win]
            button.children[1].style.color = fcolors[win]
        else:
            button.style.backgroundColor = "#ffffff"
            button.children[1].style.color = "#000000"
    for i in match_buttons.values():
        i[0].style.backgroundColor = colors[i[1]]
        i[0].children[1].style.color = fcolors[i[1]]

    score[match] = [win, lose]
    winners = []
    losers = []
    for i, j in score.values():
        winners.append(i)
        losers.append(j)
    for m in score.keys():
        win = score[m][0]
        lose = score[m][1]
        win_ind = team.index(win)
        lose_ind = team.index(lose)
        avg_score_win_for = [round(
            performance[win][0]/gamesP[win_ind]), fix_overs(performance[win][1]/gamesP[win_ind])]
        avg_score_win_ag = [round(performance[win][2]/gamesP[win_ind]),
                            fix_overs(performance[win][3]/gamesP[win_ind])]
        avg_score_lose_for = [round(
            performance[lose][0]/gamesP[lose_ind]), fix_overs(performance[lose][1]/gamesP[lose_ind])]
        avg_score_lose_ag = [round(performance[lose][2]/gamesP[lose_ind]),
                             fix_overs(performance[lose][3]/gamesP[lose_ind])]

        win_score_runs, lose_score_runs, win_score_overs, lose_score_overs = find_scores(
            avg_score_win_for, avg_score_win_ag, avg_score_lose_for, avg_score_lose_ag)

        performance[win][0] += win_score_runs
        performance[win][1] = add_overs(performance[win][1], win_score_overs)
        performance[lose][2] += win_score_runs
        performance[lose][3] = add_overs(performance[lose][3], win_score_overs)

        performance[lose][0] += lose_score_runs
        performance[lose][1] = add_overs(
            performance[lose][1], lose_score_overs)
        performance[win][2] += lose_score_runs
        performance[win][3] = add_overs(performance[win][3], lose_score_overs)

        gamesP[win_ind] += 1
        gamesW[win_ind] += 1
        pts[win_ind] += 2
        gamesP[lose_ind] += 1
        gamesL[lose_ind] += 1

        score_win_for = [performance[win][0], performance[win][1]]
        score_win_ag = [performance[win][2], performance[win][3]]
        score_lose_for = [performance[lose][0], performance[lose][1]]
        score_lose_ag = [performance[lose][2], performance[lose][3]]

        win_nrr_new = get_nrr(score_win_for, score_win_ag)
        lose_nrr_new = get_nrr(score_lose_for, score_lose_ag)
        if win_nrr_new < 0:
            win_nrr_new *= -1
        if lose_nrr_new > 0:
            lose_nrr_new *= -1

        nrr[win_ind] += round(win_nrr_new, 3)
        nrr[lose_ind] += round(lose_nrr_new, 3)
        nrr[win_ind] = round(nrr[win_ind], 3)
        nrr[lose_ind] = round(nrr[lose_ind], 3)
    table = []
    # Team    P  W  L  NR   NRR  PTS
    # ['GT', 11, 8, 3, 0, 0.951, 16]
    for k in range(len(team)):
        table_row = []
        table_row.append(team[k])
        table_row.append(gamesP[k])
        table_row.append(gamesW[k])
        table_row.append(gamesL[k])
        table_row.append(gamesNR[k])
        table_row.append(nrr[k])
        table_row.append(pts[k])
        table.append(table_row)
    sort_values(table)
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


score = {}

for i in range(len(teams1)):
    html = html + f"""
<div class="container">
    <div class="matches">
        <div class="match-container">
            <div class="match">
                <span>{match[i]}</span>
            </div>
            <hr>
            <div class="table-row" title ="{match[i]} | {teams1[i]} | {teams2[i]}">
                <div class="table-cell" title ="{match[i]} | {teams1[i]} | {teams2[i]}">
                    <button class="team-info" id = "my-team-info" title ="{match[i]} | {teams1[i]} | {teams2[i]}">
                        <img src="static/teams/{teams1[i]}.png" alt="{teams1[i]} Logo" title ="{match[i]} | {teams1[i]} | {teams2[i]}">
                        <span title ="{match[i]} | {teams1[i]} | {teams2[i]}">{teams1[i]}</span>
                    </button>
                </div>
            </div>

            <div class="table-row"  title ="{match[i]} | {teams2[i]} | {teams1[i]}">
                <div class="table-cell"  title ="{match[i]} | {teams2[i]} | {teams1[i]}">
                    <button class="team-info" id = "my-team-info" title ="{match[i]} | {teams2[i]} | {teams1[i]}">
                        <img src="static/teams/{teams2[i]}.png" alt="{teams2[i]} Logo"  title ="{match[i]} | {teams2[i]} | {teams1[i]}">
                        <span title ="{match[i]} | {teams2[i]} | {teams1[i]}">{teams2[i]}</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
"""
matchdiv = Element("mainbox")
matchdiv.element.innerHTML = html
row = ""

for i in range(len(team)):
    row = row + f"""
<tr>
    <td>{i+1}</td>
    <td>{team[i]}</td>
    <td>{gamesP[i]}</td>
    <td>{gamesW[i]}</td>
    <td>{gamesL[i]}</td>
    <td>{gamesNR[i]}</td>
    <td>{nrr[i]}</td>
    <td>{pts[i]}</td>
</tr>
"""
pointsbody = Element("points-table")
pointsbody.element.innerHTML = row


buttons = document.querySelectorAll("#my-team-info")
for button in buttons:
    button.onclick = handle_click
info = document.querySelectorAll(".team-info")

cells = document.querySelectorAll(".table-cell")

matches = document.querySelectorAll(".matches")
