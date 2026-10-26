import pandas as pd
import numpy as np
from pyscript import document

# Global cache for data
data_cache = {
    'fixtures_df': None,
    'points_df': None,
    'performance_data': None
}

# Global variables for team data
team = None
performance = None
gamesP = None
gamesW = None
gamesL = None
nrr = None
pts = None
colors = {
    "RCB": "#D5152C", "GT": "#1C2234", "SRH": "#E34633", 
    "CSK": "#FFD230", "DC": "#32579D", "KKR": "#3D245D", 
    "LSG": "#2956C9", "MI": "#285290", "RR": "#264AA5", 
    "PBKS": "#DD212E"
}
fcolors = {
    "RCB": "#000000", "GT": "#ffffff", "SRH": "#000000", 
    "CSK": "#000000", "DC": "#ffffff", "KKR": "#ffffff", 
    "LSG": "#000000", "MI": "#ffffff", "RR": "#ffffff", 
    "PBKS": "#000000"
}

match_buttons = {}


def fix_overs(no_overs):
    """Optimized overs calculation"""
    no_overs = round(no_overs, 1)
    if no_overs % 1 >= 0.6:
        if no_overs == 19.6:
            return 20.0
        return int(no_overs) + 1
    return no_overs

def add_overs(overs1, overs2):
    """Optimized overs addition"""
    total = overs1 + overs2
    if total % 1 >= 0.6:
        return int(total) + 1
    return total

def get_perf(team, scoreF, scoreA):
    """Optimized performance calculation"""
    performance = {}
    for i, t in enumerate(team):
        a, b = map(float, scoreF[i].split('/'))
        c, d = map(float, scoreA[i].split('/'))
        performance[t] = [int(a), round(b, 1), int(c), round(d, 1)]
    return performance

def get_nrr(avg_score_for, avg_score_ag):
    """Optimized NRR calculation"""
    nrr_for = avg_score_for[0]/avg_score_for[1]
    nrr_ag = avg_score_ag[0]/avg_score_ag[1]
    return (nrr_for - nrr_ag)/10

def load_data():
    """Load and cache data efficiently"""
    # Load only necessary columns
    fixtures_df = pd.read_csv('data/ipl_fixtures.csv', usecols=['team1', 'team2', 'match'])
    points_df = pd.read_csv('data/points.csv', usecols=['TEAM', 'P', 'W', 'L', 'NR', 'NRR', 'PTS', 'FOR', 'AGAINST'])
    
    # Process data efficiently
    numeric_columns = ['P', 'W', 'L', 'NR', 'PTS']
    for col in numeric_columns:
        points_df[col] = pd.to_numeric(points_df[col], errors='coerce').fillna(0).astype(np.int8)
    points_df['NRR'] = pd.to_numeric(points_df['NRR'], errors='coerce').fillna(0.0).astype(np.float32)
    
    # Cache the processed data
    data_cache['fixtures_df'] = fixtures_df
    data_cache['points_df'] = points_df
    data_cache['performance_data'] = get_perf(
        points_df['TEAM'].tolist(),
        points_df['FOR'].tolist(),
        points_df['AGAINST'].tolist()
    )
    
    # Initialize global variables
    global team, performance, gamesP, gamesW, gamesL, nrr, pts
    team = points_df['TEAM'].tolist()
    performance = data_cache['performance_data']
    gamesP = points_df['P'].values.astype(np.int8)
    gamesW = points_df['W'].values.astype(np.int8)
    gamesL = points_df['L'].values.astype(np.int8)
    nrr = points_df['NRR'].values.astype(np.float32)
    pts = points_df['PTS'].values.astype(np.int8)

def reset_table():
    """Optimized table reset using cached data"""
    if data_cache['points_df'] is None:
        load_data()
    
    df = data_cache['points_df']
    # Create table using numpy for better performance
    teams = df['TEAM'].values
    played = df['P'].values
    won = df['W'].values
    lost = df['L'].values
    nr = df['NR'].values
    nrr = df['NRR'].values
    points = df['PTS'].values
    
    return [{
        'team': teams[i],
        'played': int(played[i]),
        'won': int(won[i]),
        'lost': int(lost[i]),
        'nr': int(nr[i]),
        'nrr': float(nrr[i]),
        'points': int(points[i])
    } for i in range(len(teams))]

def sort_values(values):
    """Optimized sorting with numpy"""
    # Convert to numpy array for sorting
    arr = np.array([(row['points'], row['nrr']) for row in values])
    indices = np.lexsort((arr[:, 1], arr[:, 0]))
    return [values[i] for i in indices[::-1]]

def update_points_table():
    """Update points table efficiently"""
    table = reset_table()
    table = sort_values(table)
    
    # Build HTML string in chunks
    chunk_size = 5
    points_table = document.getElementById("points-table")
    points_table.innerHTML = ""  # Clear existing content
    
    for i in range(0, len(table), chunk_size):
        chunk = table[i:i + chunk_size]
        rows = []
        for j, row_data in enumerate(chunk):
            rows.append(f"""
            <tr>
                <td>{i+j+1}</td>
                <td>{row_data['team']}</td>
                <td>{row_data['played']}</td>
                <td>{row_data['won']}</td>
                <td>{row_data['lost']}</td>
                <td>{row_data['nr']}</td>
                <td>{round(row_data['nrr'], 3)}</td>
                <td>{row_data['points']}</td>
            </tr>
            """)
        points_table.innerHTML += ''.join(rows)

def create_match_buttons():
    """Create match buttons efficiently"""
    if data_cache['fixtures_df'] is None:
        load_data()
    
    df = data_cache['fixtures_df']
    teams1 = df["team1"].tolist()
    teams2 = df["team2"].tolist()
    matches = df["match"].tolist()
    
    # Build HTML string in chunks
    chunk_size = 3
    mainbox = document.getElementById("mainbox")
    mainbox.innerHTML = ""  # Clear existing content
    
    for i in range(0, len(matches), chunk_size):
        chunk_html = ""
        for j in range(i, min(i + chunk_size, len(matches))):
            chunk_html += f"""
            <div class="container">
                <div class="matches">
                    <div class="match-container">
                        <div class="match">
                            <span>{matches[j]}</span>
                        </div>
                        <hr>
                        <div class="table-row" title="{matches[j]} | {teams1[j]} | {teams2[j]}">
                            <div class="table-cell" title="{matches[j]} | {teams1[j]} | {teams2[j]}">
                                <button class="team-info" id="my-team-info" title="{matches[j]} | {teams1[j]} | {teams2[j]}">
                                    <img src="static/teams/{teams1[j]}.png" alt="{teams1[j]} Logo" title="{matches[j]} | {teams1[j]} | {teams2[j]}">
                                    <span title="{matches[j]} | {teams1[j]} | {teams2[j]}">{teams1[j]}</span>
                                </button>
                            </div>
                        </div>
                        <div class="table-row" title="{matches[j]} | {teams2[j]} | {teams1[j]}">
                            <div class="table-cell" title="{matches[j]} | {teams2[j]} | {teams1[j]}">
                                <button class="team-info" id="my-team-info" title="{matches[j]} | {teams2[j]} | {teams1[j]}">
                                    <img src="static/teams/{teams2[j]}.png" alt="{teams2[j]} Logo" title="{matches[j]} | {teams2[j]} | {teams1[j]}">
                                    <span title="{matches[j]} | {teams2[j]} | {teams1[j]}">{teams2[j]}</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        mainbox.innerHTML += chunk_html
    
    # Setup event listeners
    buttons = document.querySelectorAll("#my-team-info")
    for button in buttons:
        button.onclick = handle_click

def find_scores(avg_score_win_for, avg_score_win_ag, avg_score_lose_for, avg_score_lose_ag):
    """Optimized score calculation"""
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

def handle_click(event):
    """Optimized click handler"""
    # Get match data
    match, win, lose = event.target.title.split(" | ")
    
    # Update button states
    buttons = document.querySelectorAll("#my-team-info")
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

    # Update scores
    score = {match: [win, lose]}
    
    # Process each match
    for m in score:
        win, lose = score[m]
        win_ind = team.index(win)
        lose_ind = team.index(lose)
        
        # Calculate average scores
        avg_score_win_for = [
            round(performance[win][0]/gamesP[win_ind]),
            fix_overs(performance[win][1]/gamesP[win_ind])
        ]
        avg_score_win_ag = [
            round(performance[win][2]/gamesP[win_ind]),
            fix_overs(performance[win][3]/gamesP[win_ind])
        ]
        avg_score_lose_for = [
            round(performance[lose][0]/gamesP[lose_ind]),
            fix_overs(performance[lose][1]/gamesP[lose_ind])
        ]
        avg_score_lose_ag = [
            round(performance[lose][2]/gamesP[lose_ind]),
            fix_overs(performance[lose][3]/gamesP[lose_ind])
        ]
        
        # Calculate new scores
        win_score_runs, lose_score_runs, win_score_overs, lose_score_overs = find_scores(
            avg_score_win_for, avg_score_win_ag, avg_score_lose_for, avg_score_lose_ag
        )
        
        # Update performance
        performance[win][0] += win_score_runs
        performance[win][1] = add_overs(performance[win][1], win_score_overs)
        performance[lose][2] += win_score_runs
        performance[lose][3] = add_overs(performance[lose][3], win_score_overs)

        performance[lose][0] += lose_score_runs
        performance[lose][1] = add_overs(performance[lose][1], lose_score_overs)
        performance[win][2] += lose_score_runs
        performance[win][3] = add_overs(performance[win][3], lose_score_overs)
        
        # Update games and points
        gamesP[win_ind] += 1
        gamesW[win_ind] += 1
        pts[win_ind] += 2
        gamesP[lose_ind] += 1
        gamesL[lose_ind] += 1
        
        # Calculate NRR
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
        
        nrr[win_ind] = round(nrr[win_ind] + win_nrr_new, 3)
        nrr[lose_ind] = round(nrr[lose_ind] + lose_nrr_new, 3)
    
    # Update points table
    update_points_table()

# Initialize the application
def init():
    """Initialize the application"""
    load_data()
    create_match_buttons()
    update_points_table()

# Start the application
init()