from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

# Setup Selenium options

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.headless = True
options.add_argument("--window-size=1920,1200")
DRIVER_PATH = "webdriver\chromedriver.exe"
service = Service(executable_path=DRIVER_PATH)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

# Visit the IPL points table page
driver.get('https://www.iplt20.com/points-table/men/')
time.sleep(4)  # Wait for JS to load the table

# Get page source and parse with BeautifulSoup
html_response = driver.page_source
driver.quit()
print("SCRAPED ALL DATA")

soup = BeautifulSoup(html_response, "html.parser")
points_table = soup.find('tbody', {"id": "pointsdata"})
print(points_table)
rows = points_table.find_all("tr", recursive=False)

teams = {"ROYAL CHALLENGERS BENGALURU": "RCB", "GUJARAT TITANS": "GT", "DELHI CAPITALS": "DC", "PUNJAB KINGS": "PBKS", "RAJASTHAN ROYALS": "RR",
         "SUNRISERS HYDERABAD": "SRH", "LUCKNOW SUPER GIANTS": "LSG", "CHENNAI SUPER KINGS": "CSK", "KOLKATA KNIGHT RIDERS": "KKR", "MUMBAI INDIANS": "MI", "ROYAL CHALLENGERS BANGALORE":"RCB"}

table = []
for row in rows:
    qualified = row.find('span', {"class": "standings_qualified ng-scope"})
    data = []
    record = [x for x in row.text.split(" ") if x.strip()]
    # Expected structure: [POS TEAM P W L NR NRR FOR AGAINST PTS]
    try:
        data.append(record[1])  # TEAM
        data.append(record[2])  # P
        data.append(record[3])  # W
        data.append(record[4])  # L
        data.append(record[5])  # NR
        data.append(record[6])  # NRR
        data.append(record[7])  # FOR
        data.append(record[8])  # AGAINST
        data.append(record[9])  # PTS
        data.append("Yes" if qualified else "No")  # QUALIFIED
        print(data)
        table.append(data)
    except IndexError:
        print("Skipping row due to structure mismatch:", record)

# Save to CSV
df = pd.DataFrame(table, columns=['TEAM', 'P', 'W', 'L', 'NR', "NRR", "FOR", "AGAINST", "PTS", "QUALIFIED"])
df.to_csv('data\\points.csv', index=False)
