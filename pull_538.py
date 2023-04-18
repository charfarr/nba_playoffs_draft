import requests
from bs4 import BeautifulSoup
import time


url = 'https://projects.fivethirtyeight.com/2023-nba-predictions/?ex_cid=rrpromo'
page = requests.get(url)

soup = BeautifulSoup(page.content, 'html.parser')
standings_table = soup.find(id='standings-table')
standings_table_body = standings_table.find('tbody')
rows = standings_table_body.find_all('tr')


def get_nba_team_row(html_row) -> list:
    team_name = html_row['data-team']

    win_probability_str = html_row.find('td', {'data-col': 'win_finals'}) \
                                  .get_text() \
                                  .replace('%', '')
    
    try:
        win_probability = float(win_probability_str) / 100.
    except:
        win_probability = None

    current_time = time.time()

    return [team_name, win_probability, current_time]


data = [get_nba_team_row(row) for row in rows]
