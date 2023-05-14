import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import pandas as pd


async def main(url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
    await page.waitFor(3000)
    html = await page.content()
    await browser.close()
    print("SCRAPPED ALL DATA")
    return html


def replace_team(team):
    teams = {"ROYAL CHALLENGERS BANGALORE": "RCB", "GUJARAT TITANS": "GT", "DELHI CAPITALS": "DC", "PUNJAB KINGS": "PBKS", "RAJASTHAN ROYALS": "RR",
             "SUNRISERS HYDERABAD": "SRH", "LUCKNOW SUPER GIANTS": "LSG", "CHENNAI SUPER KINGS": "CSK", "KOLKATA KNIGHT RIDERS": "KKR", "MUMBAI INDIANS": "MI", "NO RESULT": "NR"}
    return teams[team]


def split_score(data):
    try:
        score, wickets = data.split("/")
    except ValueError:
        score = data.split("/")[0]
        wickets = 10
    return score, wickets


def clean_string(string):
    if string[0] == " ":
        return string[1:]
    return string


def get_data(url, year, data):
    cols = []
    html_response = asyncio.get_event_loop().run_until_complete(main(url))
    soup = BeautifulSoup(html_response, "html.parser")
    fixture_table = soup.find('ul', {"id": "team_archive"})
    fixture_rows = fixture_table.findChildren("li", recursive=False)
    for i in fixture_rows:
        match_data = []
        for j in i:
            record = j.text.split("  ")
            item = [x for x in record if x != "" and x != " "]
            if item == []:
                continue
            else:
                match_data += item
        print(match_data)
        cols.append(clean_string(match_data[0]))
        cols.append(clean_string(match_data[1]))
        date, time = match_data[2].split(" , ")
        cols.append(clean_string(date))
        cols.append(clean_string(time))
        if "Wickets" in match_data[4] or "Runs" in match_data[4] or "Overs" in match_data[4]:
            match_data.pop(4)
        if match_data[3] == "NO RESULT":
            cols.append(teams[clean_string(match_data[4]).upper()])
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
            cols.append(teams[clean_string(match_data[4]).upper()])
            score, wickets = split_score(clean_string(match_data[6]))
            cols.append(int(score))
            cols.append(int(wickets))
            overs = clean_string(match_data[7]).strip("() OV")
            cols.append(float(overs))
            cols.append(teams[clean_string(match_data[8]).upper()])
            score, wickets = split_score(clean_string(match_data[10]))
            cols.append(int(score))
            cols.append(int(wickets))
            overs = clean_string(match_data[11]).strip("() OV")
            cols.append(float(overs))
            winner = clean_string(match_data[3].upper().split(" WON BY ")[0])
            cols.append(replace_team(winner))

        cols.append(year)
        data.append(cols)
        print(cols)
        cols = []


url1 = 'https://www.iplt20.com/matches/results/2022'
url2 = 'https://www.iplt20.com/matches/results/2023'
data = []
teams = {"ROYAL CHALLENGERS BANGALORE": "RCB", "GUJARAT TITANS": "GT", "DELHI CAPITALS": "DC", "PUNJAB KINGS": "PBKS", "RAJASTHAN ROYALS": "RR",
         "SUNRISERS HYDERABAD": "SRH", "LUCKNOW SUPER GIANTS": "LSG", "CHENNAI SUPER KINGS": "CSK", "KOLKATA KNIGHT RIDERS": "KKR", "MUMBAI INDIANS": "MI"}

get_data(url1, 2022, data)
get_data(url2, 2023, data)


df = pd.DataFrame(data, columns=['match', 'venue', 'date', 'time', 'team1', 'team1_score', 'team1_wickets',
                  'team1_overs', 'team2', 'team2_score', 'team2_wickets', 'team2_overs', "winner", "year"])

df.to_csv('data\ipl_matches.csv', index=False)
