import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup

async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://www.iplt20.com/points-table/men/2023')
    await page.waitFor(3000) 

    ## Get HTML
    html = await page.content()
    await browser.close()
    return html

html_response = asyncio.get_event_loop().run_until_complete(main())

## Load HTML Response Into BeautifulSoup
soup = BeautifulSoup(html_response, "html.parser")
points_table = soup.find('tbody',{ "id" : "pointsdata" })
rows = points_table.findChildren("tr" , recursive=False)

data = []
teams = {"ROYAL CHALLENGERS BANGALORE":"RCB","GUJARAT TITANS":"GT","DELHI CAPITALS":"DC","PUNJAB KINGS":"PBKS","RAJASTHAN ROYALS":"RR","SUNRISERS HYDERABAD":"SRH","LUCKNOW SUPER GIANTS":"LSG","CHENNAI SUPER KINGS":"CSK","KOLKATA KNIGHT RIDERS":"KKR","MUMBAI INDIANS":"MI"}
table = []
for i in rows:
    data = []
    row_data = i.text.split(" ")
    record = [x for x in row_data if x != ""]
    #[POS TEAM P W L NR NRR PTS]
    data.append(record[0])
    data.append(record[1])
    data.append(record[2])
    data.append(record[3])
    data.append(record[4])
    data.append(record[5])
    data.append(record[6])
    data.append(record[9])
    table.append(data)
print(table)
