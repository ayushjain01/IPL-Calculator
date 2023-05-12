from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd


options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.headless = True
options.add_argument("--window-size=1920,1200")
DRIVER_PATH = "C:\webdriver\chromedriver.exe"
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
url = 'https://www.iplt20.com/matches/points-table'
driver.get(url)
time.sleep(4)
points_table = driver.find_element(By.ID,"pointsdata")
rows = points_table.find_elements(By.XPATH,".//tr")
data = []
teams = {"ROYAL CHALLENGERS BANGALORE":"RCB","GUJARAT TITANS":"GT","DELHI CAPITALS":"DC","PUNJAB KINGS":"PBKS","RAJASTHAN ROYALS":"RR","SUNRISERS HYDERABAD":"SRH","LUCKNOW SUPER GIANTS":"LSG","CHENNAI SUPER KINGS":"CSK","KOLKATA KNIGHT RIDERS":"KKR","MUMBAI INDIANS":"MI"}

table = []
for i in rows:
    data = []
    cols = []
    row_data = i.text.split("\n")[1:3]
    team = row_data[0]
    points = row_data[1].split(" ")
    #[P W L NR NRR PTS]
    data.append(team)
    data.append(int(points[0]))
    data.append(int(points[1]))
    data.append(int(points[2]))
    data.append(int(points[3]))
    data.append(float(points[4]))
    data.append(int(points[7]))
    table.append(data)
print(table)



# df = pd.DataFrame(data, columns=['match', 'venue', 'date', 'time', 'team1','team2',"year"])

# df.to_csv('points_table.csv', index=False)
