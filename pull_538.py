import requests
from bs4 import BeautifulSoup
import time


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


def get_538_nba_standings_html_table(url: str):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    standings_table = soup.find(id='standings-table')
    return standings_table


def get_538_nba_standings_list(url: str) -> list:
    html_table = get_538_nba_standings_html_table(url)
    html_table_body = html_table.find('tbody')
    rows = html_table_body.find_all('tr')
    
    return [get_nba_team_row(row) for row in rows]


def main():
    url = 'https://projects.fivethirtyeight.com/2023-nba-predictions/?ex_cid=rrpromo'

    standings = get_538_nba_standings_list(url)

    print(standings)


if __name__ == '__main__':
    main()
