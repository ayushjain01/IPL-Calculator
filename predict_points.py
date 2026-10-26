import pandas as pd
import numpy as np
from pyscript import document, window

# Global cache for data
data_cache = {
    'points_df': None,
    'fixtures_df': None,
    'performance_data': None
}

def load_data():
    """Load and cache data efficiently with memory optimization"""
    # Load data in chunks to reduce memory usage
    points_df = pd.read_csv('data/points.csv', usecols=['TEAM', 'P', 'W', 'L', 'NR', 'NRR', 'PTS', 'QUALIFIED', 'FOR', 'AGAINST'])
    fixtures_df = pd.read_csv('data/ipl_fixtures.csv', usecols=['team1', 'team2'])
    
    # Process data efficiently
    numeric_columns = ['P', 'W', 'L', 'NR', 'PTS']
    for col in numeric_columns:
        points_df[col] = pd.to_numeric(points_df[col], errors='coerce').fillna(0).astype(np.int8)
    points_df['NRR'] = pd.to_numeric(points_df['NRR'], errors='coerce').fillna(0.0).astype(np.float32)
    
    # Cache the processed data
    data_cache['points_df'] = points_df
    data_cache['fixtures_df'] = fixtures_df
    data_cache['performance_data'] = get_perf(
        points_df['TEAM'].tolist(),
        points_df['FOR'].tolist(),
        points_df['AGAINST'].tolist()
    )

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
    qualified = df['QUALIFIED'].values
    
    return [{
        'team': teams[i],
        'played': int(played[i]),
        'won': int(won[i]),
        'lost': int(lost[i]),
        'nr': int(nr[i]),
        'nrr': float(nrr[i]),
        'points': int(points[i]),
        'qualified': qualified[i]
    } for i in range(len(teams))]

def print_table(table):
    """Optimized table printing"""
    print("|-------------------------------------------------------|")
    print("| POS | TEAM |  P  |  W  |  L  |  NR  |   NNR   |  PTS  |")
    print("|-------------------------------------------------------|")
    for i, row in enumerate(table, 1):
        print(f"|{i:^5}|{row['team']:^6}|{row['played']:^5}|{row['won']:^5}|{row['lost']:^5}|{row['nr']:^6}|{row['nrr']:^9.3f}|{row['points']:^7}|")
    print("|-------------------------------------------------------|")

def add_to_table(table, table_count):
    """Optimized table addition to HTML"""
    content = document.getElementById("copy-content")
    content.style.display = "block"
    
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

    for i, row_data in enumerate(table, 1):
        row += f"""
        <tr>
            <td>{i}</td>
            <td>{row_data['team']}</td>
            <td>{row_data['played']}</td>
            <td>{row_data['won']}</td>
            <td>{row_data['lost']}</td>
            <td>{row_data['nr']}</td>
            <td>{round(row_data['nrr'], 3)}</td>
            <td>{row_data['points']}</td>
        </tr>
        """
    
    row += """</tbody></table><br><hr>"""
    content.innerHTML += row

def make_dict(table):
    """Optimized dictionary creation"""
    return {row['team']: row for row in table}

def sort_values(values):
    """Optimized sorting with numpy"""
    # Convert to numpy array for sorting
    arr = np.array([(row['points'], row['nrr']) for row in values])
    indices = np.lexsort((arr[:, 1], arr[:, 0]))
    return [values[i] for i in indices[::-1]]

def winners(teams1, teams2):
    """Optimized winners calculation"""
    print("calculating this first")
    n = len(teams1)
    possible_winners = []
    possible_losers = []
    
    for i in range(2**n):
        winner = []
        loser = []
        for j in range(n):
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
    """Optimized points assignment"""
    table_dict = make_dict(table)
    performance = get_perf(team, scoreF, scoreA)
    
    for i in range(len(wins)):
        win_team = list(table_dict[wins[i]])
        lose_team = list(table_dict[loses[i]])
        
        # Calculate scores
        win_perf = performance[wins[i]]
        lose_perf = performance[loses[i]]
        
        avg_score_win_for = [round(win_perf[0]/win_team[1]), 
                            fix_overs(win_perf[1]/win_team[1])]
        avg_score_win_ag = [round(win_perf[2]/win_team[1]), 
                           fix_overs(win_perf[3]/win_team[1])]
        avg_score_lose_for = [round(lose_perf[0]/lose_team[1]), 
                             fix_overs(lose_perf[1]/lose_team[1])]
        avg_score_lose_ag = [round(lose_perf[2]/lose_team[1]), 
                            fix_overs(lose_perf[3]/lose_team[1])]

        # Update performance
        win_score_runs = max(avg_score_win_for[0], avg_score_lose_ag[0])
        lose_score_runs = min(avg_score_lose_for[0], avg_score_win_ag[0])
        win_score_overs = max(avg_score_win_for[1], avg_score_lose_ag[1])
        lose_score_overs = max(avg_score_lose_for[1], avg_score_win_ag[1])

        # Update stats
        performance[wins[i]][0] += win_score_runs
        performance[wins[i]][1] = add_overs(performance[wins[i]][1], win_score_overs)
        performance[loses[i]][2] += win_score_runs
        performance[loses[i]][3] = add_overs(performance[loses[i]][3], win_score_overs)

        performance[loses[i]][0] += lose_score_runs
        performance[loses[i]][1] = add_overs(performance[loses[i]][1], lose_score_overs)
        performance[wins[i]][2] += lose_score_runs
        performance[wins[i]][3] = add_overs(performance[wins[i]][3], lose_score_overs)

        # Update points and games
        win_team[1] += 1
        win_team[2] += 1
        win_team[6] += 2
        lose_team[1] += 1
        lose_team[3] += 1

        # Calculate NRR
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
        lose_team[5] += lose_nrr_new
        
        table_dict[wins[i]] = win_team
        table_dict[loses[i]] = lose_team

    return list(table_dict.values())

def team_wins(team, teams1, teams2, wins, table_count):
    """Optimized team wins display"""
    content = document.getElementById("copy-content")
    content.style.display = "block"
    
    content_text = f"""<br>
    <p class="title-para" style="background-color:{colors[team]};color:{fcolors[team]}" id="scenario-number">Scenario - {table_count+1}</p>
    <div id="scenarios">
        <h1>{team} will qualify if -</h1>
        <hr>
    """
    
    for i in range(len(wins)):
        content_text += f"<p class='winner_row'> {wins[i]:<4} wins - {teams1[i]:<4} VS {teams2[i]:<4} </p>"
    
    content_text += "</div>"
    content.innerHTML += content_text
    return table_count + 1

def update_ui():
    """Update UI elements efficiently with memory optimization"""
    table = reset_table()
    table = sort_values(table)
    
    # Build HTML string in chunks to reduce memory usage
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
    
    # Update iterations menu
    if data_cache['fixtures_df'] is not None:
        teams1 = data_cache['fixtures_df']["team1"].tolist()
        teams2 = data_cache['fixtures_df']["team2"].tolist()
        wins, loses = winners(teams1, teams2)
        
        # Build options efficiently
        options = [f"""<option value="{i}">{i}</option>""" for i in range(1, min(11, len(wins)))]
        
        iterations_menu = document.getElementById("iterations")
        iterations_menu.innerHTML = ''.join(options)

def handle_click(event):
    """Optimized click handler with memory management"""
    table_count = 0
    resultText = document.getElementById("results")
    resultText.style.display = "none"
    
    content = document.getElementById("copy-content")
    content.innerHTML = ""
    content.style.display = "none"
    
    team_name = document.getElementById("teams").value
    iterations = document.getElementById("iterations").value
    ch = 0
    results_printed = False
    
    # Get data from cache
    df = data_cache['points_df']
    team = df["TEAM"].tolist()
    qualified = df["QUALIFIED"].tolist()
    
    teamInd = team.index(team_name)
    if qualified[teamInd] == "Yes":
        resultText.innerHTML = f"Congratulations!🎉 Your team {team_name} has already qualified🥳"
        resultText.style.display = "block"
        return
    
    # Process scenarios in chunks
    chunk_size = 5
    for i in range(0, len(wins), chunk_size):
        chunk_wins = wins[i:i + chunk_size]
        chunk_loses = loses[i:i + chunk_size]
        
        for l in range(len(chunk_wins)):
            if team_name in chunk_loses[l]:
                continue
                
            result = process_scenario(team_name, chunk_wins[l], chunk_loses[l], i + l)
            if result:
                ch += 1
                results_printed = True
                
            if ch >= int(iterations):
                break
        
        if ch >= int(iterations):
            break
    
    if not results_printed:
        resultText.innerHTML = f"Sorry🥹 but your team {team_name} cannot qualify this season. Better luck next time."
        resultText.style.display = "block"

def process_scenario(team_name, win_teams, lose_teams, scenario_index):
    """Process a single scenario efficiently"""
    table = reset_table()
    table = assign_points(team_name, win_teams, lose_teams, table)
    table = sort_values(table)
    top4 = table[:4]
    
    for team_q in top4:
        if team_q['team'] == team_name:
            team_wins(team_q['team'], teams1, teams2, win_teams, scenario_index)
            print_table(table)
            add_to_table(table, scenario_index)
            return True
    return False

# Initialize the application
def init():
    """Initialize the application"""
    load_data()
    update_ui()
    
    # Setup event listeners
    calc_button = document.getElementById("calc-button")
    calc_button.onclick = handle_click

# Start the application
init()
