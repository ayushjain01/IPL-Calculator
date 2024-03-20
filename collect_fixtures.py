from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import time
import pandas as pd


options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.headless = True
options.add_argument("--window-size=1920,1200")
DRIVER_PATH = "webdriver\chromedriver.exe"
service = Service(executable_path=DRIVER_PATH)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
url = 'https://www.iplt20.com/matches/fixtures'
driver.get(url)
time.sleep(4)
fixture_table = driver.find_element(By.ID, "team_archive")
fixture_rows = fixture_table.find_elements(By.XPATH, ".//li")
data = []
teams = {"ROYAL CHALLENGERS BENGALURU": "RCB", "GUJARAT TITANS": "GT", "DELHI CAPITALS": "DC", "PUNJAB KINGS": "PBKS", "RAJASTHAN ROYALS": "RR",
         "SUNRISERS HYDERABAD": "SRH", "LUCKNOW SUPER GIANTS": "LSG", "CHENNAI SUPER KINGS": "CSK", "KOLKATA KNIGHT RIDERS": "KKR", "MUMBAI INDIANS": "MI", "ROYAL CHALLENGERS BANGALORE":"RCB"}

for i in fixture_rows:
    cols = []
    match_data = i.text.split("\n")[:8]
    match_data.pop(7)
    match_data.pop(5)
    cols.append(match_data[0])
    cols.append(match_data[1])
    cols.append(match_data[2])
    cols.append(match_data[3])
    if match_data[4] == "TBD":
        break
    cols.append(teams[match_data[4]])
    cols.append(teams[match_data[5]])
    cols.append(2023)
    data.append(cols)


df = pd.DataFrame(
    data, columns=['match', 'venue', 'date', 'time', 'team1', 'team2', "year"])

df.to_csv('data\ipl_fixtures.csv', index=False)
# for i in fixture_rows:
#     print(i.text)
# driver.get('https://google.com')
# search = driver.find_element(By.CLASS_NAME,"gLFyf")
# search.send_keys("IPL")
# search.send_keys(Keys.RETURN)
# table = driver.find_element(By.CLASS_NAME,"ofy7ae")
# table.click()
# pyautogui.click(x=100, y=400)
# time.sleep(1)
# pyautogui.scroll(-10000)
# time.sleep(1)
# pyautogui.scroll(100000)
# time.sleep(1)
# pyautogui.scroll(-10000)
# time.sleep(1)
# pyautogui.scroll(100000)
# time.sleep(1)
# matches = driver.find_elements(By.CLASS_NAME,"imspo_mt__lg-st-co")
# dates = driver.find_elements(By.CLASS_NAME,"imspo_mt__cmd")

# new = []
# matchdata = []
# for k in matches:
#     match = k.find_element(By.XPATH,".//*")
#     matchdata.append(match)
# for j in dates:
#     date =  j.find_element(By.XPATH,".//*")
#     new.append(date)
# new.pop()
# new.pop()
# new.pop()
# dates2 = driver.find_elements(By.CLASS_NAME,"imspo_mt__ns-pm-s")
# for j in dates2:
#     date =  j.find_element(By.XPATH,".//*")
#     new.append(date)
# for i in new:
#     if i.text=="\n" or i.text == "" or i.text == " ":
#         new.remove(i)
# for i in matchdata:
#     if i.text=="\n" or i.text == "" or i.text == " ":
#         matchdata.remove(i)
# matchdata.pop()
# matchdata.pop()
# for a,b in zip(matchdata,new):
#     print(a.text, "         ", b.text)
#     print()

# teams_left = []
# teams_right = []

# lst = driver.find_elements(By.CLASS_NAME,"ellipsisize")
# print(len(lst))
# lst = lst[3:]
# for j in range(len(new)*2):
#     r = lst[j].text.split("\n")
#     if j%2 ==0:
#         teams_left.append(r[1])
#     else:
#         teams_right.append(r[1])
# print(teams_left, teams_right)
# driver.quit()
