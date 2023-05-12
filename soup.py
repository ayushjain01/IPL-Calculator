import requests
from bs4 import BeautifulSoup
import time
url = 'https://www.iplt20.com/matches/fixtures'
response = requests.get(url)
time.sleep(4)
soup = BeautifulSoup(response.text, 'html.parser')

fixtures = []
# Find all the fixtures rows in the HTML table
fixture_rows = soup.find_all('li', {'class': "ng-scope"})
print(len(fixture_rows))
for row in fixture_rows:
    # Extract the data from each column of the row
    date = row.find('span', {'class': 'fixture__date'}).text.strip()
    month = row.find('span', {'class': 'fixture__month'}).text.strip()
    time = row.find('span', {'class': 'fixture__time'}).text.strip()
    venue = row.find('p', {'class': 'fixture__info'}).text.strip()
    match = row.find('h3', {'class': 'fixture__match'}).text.strip()
    team1 = row.find('p', {'class': 'fixture__team-name--abbrev'}).text.strip()
    team2 = row.find_all('p', {'class': 'fixture__team-name--abbrev'})[1].text.strip()

    # Add the data to the fixtures list
    fixtures.append({
        'date': date,
        'month': month,
        'time': time,
        'venue': venue,
        'match': match,
        'team1': team1,
        'team2': team2
    })

# Print the fixtures list
print(fixtures)
