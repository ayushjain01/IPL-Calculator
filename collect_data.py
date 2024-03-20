from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import pandas as pd


def replace_team(team):
    teams = {"ROYAL CHALLENGERS BENGALURU": "RCB", "GUJARAT TITANS": "GT", "DELHI CAPITALS": "DC", "PUNJAB KINGS": "PBKS", "RAJASTHAN ROYALS": "RR",
             "SUNRISERS HYDERABAD": "SRH", "LUCKNOW SUPER GIANTS": "LSG", "CHENNAI SUPER KINGS": "CSK", "KOLKATA KNIGHT RIDERS": "KKR", "MUMBAI INDIANS": "MI", "ROYAL CHALLENGERS BANGALORE":"RCB", "NO RESULT": "NR"}
    return teams[team]


def split_score(data):
    try:
        score, wickets = data.split("/")
    except ValueError:
        score = data.split("/")[0]
        wickets = 10
    return score, wickets


def get_data(url, year, data):
    cols = []
    driver.get(url)
    import time
    time.sleep(4)
    fixture_table = driver.find_element(By.ID, "team_archive")
    fixture_rows = fixture_table.find_elements(By.XPATH, ".//li")
    for i in fixture_rows:
        match_data = i.text.split("\n")[:10]
        cols.append(match_data[0])
        cols.append(match_data[1])
        date, time = match_data[2].split(" , ")
        cols.append(date)
        cols.append(time)
        if match_data[3] == "NO RESULT":
            cols.append(teams[match_data[4]])
            cols.append(None)
            cols.append(None)
            cols.append(None)
            temp_data = match_data[5:]
            for i in temp_data:
                if i in teams.keys():
                    break
            cols.append(teams[i])
            cols.append(None)
            cols.append(None)
            cols.append(None)
            cols.append("NR")
        else:
            cols.append(teams[match_data[4]])
            score, wickets = split_score(match_data[5])
            cols.append(int(score))
            cols.append(int(wickets))
            overs = match_data[6].strip("() OV")
            cols.append(float(overs))
            cols.append(teams[match_data[7]])
            score, wickets = split_score(match_data[8])
            cols.append(int(score))
            cols.append(int(wickets))
            overs = match_data[9].strip("() OV")
            cols.append(float(overs))
            winner = match_data[3].split(" WON BY ")[0]
            cols.append(replace_team(winner))

        cols.append(year)
        data.append(cols)
        print(cols)
        cols = []


options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.headless = True
options.add_argument("--window-size=1920,1200")
DRIVER_PATH = "webdriver\chromedriver.exe"
service = Service(executable_path=DRIVER_PATH)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
url1 = 'https://www.iplt20.com/matches/results/2022'
url2 = 'https://www.iplt20.com/matches/results/2023'
data = []
teams = {"ROYAL CHALLENGERS BENGALURU": "RCB", "GUJARAT TITANS": "GT", "DELHI CAPITALS": "DC", "PUNJAB KINGS": "PBKS", "RAJASTHAN ROYALS": "RR",
         "SUNRISERS HYDERABAD": "SRH", "LUCKNOW SUPER GIANTS": "LSG", "CHENNAI SUPER KINGS": "CSK", "KOLKATA KNIGHT RIDERS": "KKR", "MUMBAI INDIANS": "MI", "ROYAL CHALLENGERS BANGALORE":"RCB"}

get_data(url1, 2022, data)
get_data(url2, 2023, data)
df = pd.DataFrame(data, columns=['match', 'venue', 'date', 'time', 'team1', 'team1_score', 'team1_wickets',
                  'team1_overs', 'team2', 'team2_score', 'team2_wickets', 'team2_overs', "winner", "year"])

df.to_csv('data\ipl_matches.csv', index=False)
