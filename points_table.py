import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import pandas as pd


async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://www.iplt20.com/points-table/men/2024')
    await page.waitFor(3000)
    html = await page.content()
    await browser.close()
    print("SCRAPPED ALL DATA")
    return html

html_response = asyncio.get_event_loop().run_until_complete(main())
soup = BeautifulSoup(html_response, "html.parser")
points_table = soup.find('tbody', {"id": "pointsdata"})
rows = points_table.findChildren("tr", recursive=False)

data = []
teams = {"ROYAL CHALLENGERS BENGALURU": "RCB", "GUJARAT TITANS": "GT", "DELHI CAPITALS": "DC", "PUNJAB KINGS": "PBKS", "RAJASTHAN ROYALS": "RR",
         "SUNRISERS HYDERABAD": "SRH", "LUCKNOW SUPER GIANTS": "LSG", "CHENNAI SUPER KINGS": "CSK", "KOLKATA KNIGHT RIDERS": "KKR", "MUMBAI INDIANS": "MI", "ROYAL CHALLENGERS BANGALORE":"RCB"}
table = []
for i in rows:
    qualified = i.find('span', {"class":"standings_qualified ng-scope"})
    data = []
    row_data = i.text.split(" ")
    record = [x for x in row_data if x != ""]
    # [POS TEAM P W L NR NRR PTS]
    data.append(record[1])
    data.append(record[2])
    data.append(record[3])
    data.append(record[4])
    data.append(record[5])
    data.append(record[6])
    data.append(record[7])
    data.append(record[8])
    data.append(record[9])
    if qualified != None:
        data.append("Yes")
    else:
        data.append("No")
    print(data)
    table.append(data)
df = pd.DataFrame(table, columns=['TEAM', 'P', 'W', 'L', 'NR', "NRR","FOR","AGAINST", "PTS","QUALIFIED"])
df.to_csv('data\points.csv', index=False)

# df = pd.DataFrame(data, columns=['match', 'venue', 'date', 'time', 'team1','team2',"year"])

# df.to_csv('points_table.csv', index=False)
