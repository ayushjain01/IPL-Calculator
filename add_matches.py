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

html = ""
colors = {"RCB": "#D5152C", "GT": "#1C2234", "SRH": "#E34633", "CSK": "#FFD230", "DC": "#32579D",
          "KKR": "#3D245D", "LSG": "#2956C9", "MI": "#285290", "RR": "#264AA5", "PBKS": "#DD212E"}
fcolors = {"RCB": "#000000", "GT": "#ffffff", "SRH": "#000000", "CSK": "#000000", "DC": "#ffffff",
           "KKR": "#ffffff", "LSG": "#000000", "MI": "#ffffff", "RR": "#ffffff", "PBKS": "#000000"}
match_buttons = {}

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
    match, win, lose = event.target.title.split(" | ")
    
    for button in buttons:

        if button.title == event.target.title:
            match_buttons[match] = (button,win)
            button.style.backgroundColor = colors[win]
            button.children[1].style.color = fcolors[win]
        else:
            button.style.backgroundColor = "#ffffff"
            button.children[1].style.color = "#000000"
    print(match_buttons)
    for i in match_buttons.values():
        i[0].style.backgroundColor = colors[i[1]]
        i[0].children[1].style.color = fcolors[i[1]]

    score[match] = [win, lose]
    print(score)
    winners = []
    losers = []
    for i, j in score.values():
        winners.append(i)
        losers.append(j)
    for m in score.keys():
        win = score[m][0]
        lose = score[m][1]
        print(m, win, lose)
        win_ind = team.index(win)
        lose_ind = team.index(lose)
        gamesP[win_ind] += 1
        gamesW[win_ind] += 1
        nrr[win_ind] = round(nrr[win_ind]+0.05, 3)
        pts[win_ind] += 2
        gamesP[lose_ind] += 1
        gamesL[lose_ind] += 1
        nrr[lose_ind] = round(nrr[lose_ind]-0.05, 3)
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
    print(button)
    button.onclick = handle_click
info = document.querySelectorAll(".team-info")

cells = document.querySelectorAll(".table-cell")

matches = document.querySelectorAll(".matches")
