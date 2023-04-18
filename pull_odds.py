import pandas as pd
import requests
import json
import arrow
import time
import gspread
from google.oauth2 import service_account


def get_odds_api_data(sporting_event: str, markets: str, bookmakers: list, odds_api_key: str) -> list:
    """
    Connects to 'The Odds API' and pulls the latest data (in JSON format) for a given sporting event/
    markets/bookmakers combination.  Will require an API key that can be acquired on their website.
    """

    base_url = f'https://api.the-odds-api.com/v4/sports/{sporting_event}/odds/'

    response = requests.get(base_url,
                            params={'markets': markets, 
                                    'bookmakers': bookmakers, 
                                    'apiKey': odds_api_key})

    return json.loads(response.content)


def parse_nba_championship_odds_json(input_json: list) -> list:
    """
    Function for extracting the NBA Playoffs outrights data from the full Odds API JSON response.
    This is a pretty specific function- could be better generalized.
    """

    fanduel_odds = [bookmaker for bookmaker in input_json[0]['bookmakers'] if bookmaker['key'] == 'fanduel'][0]
    fanduel_odds_markets = fanduel_odds['markets']
    fanduel_odds_outrights = [market for market in fanduel_odds_markets if market['key'] == 'outrights'][0]
    return fanduel_odds_outrights['outcomes']


def create_odds_outcome_dataframe(odds_outcome: list) -> pd.DataFrame:
    """
    Creates a Pandas dataframe from a nicely formatted outrights JSON.
    """
    return pd.DataFrame(odds_outcome) \
             .rename(columns={'name': 'team'}) \
             .assign(probability = lambda d: 1 / d.loc[:, 'price'],
                     updated_at = time.time())


def get_current_odds_outcome_dataframe(odds_api_key: str) -> pd.DataFrame:
    """
    Returns the latest Fanduel NBA Playoffs outrights odds in a Pandas dataframe.
    """

    event = 'basketball_nba_championship_winner'
    markets = ['outrights']
    bookmakers = ['fanduel']

    base_json = get_odds_api_data(event, markets, bookmakers, odds_api_key)
    parsed_json = parse_nba_championship_odds_json(base_json)
    df_odds = create_odds_outcome_dataframe(parsed_json)

    return df_odds


def create_gsheets_client(google_sheets_raw_creds: str) -> gspread.client.Client:
    """
    Creates a gspread client for accessing Google Sheets.
    """
    gsheet_credentials = service_account.Credentials.from_service_account_info(json.loads(google_sheets_raw_creds))
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    gsheet_credentials_with_scope = gsheet_credentials.with_scopes(scope)
    gspread_client = gspread.authorize(gsheet_credentials_with_scope)
    return gspread_client


def append_most_recent_fanduel_nba_playoffs_odds_to_gsheet(
    odds_api_key: str,
    google_sheets_raw_creds: str,
    spreadsheet_key: str, 
    worksheet_name: str
) -> None:

    """
    Given a Google sheet and a specified worksheet, this will append that spreadsheet with the latest Fanduel
    NBA Championship odds per team.
    """

    df_recent_odds = get_current_odds_outcome_dataframe(odds_api_key)

    gspread_client = create_gsheets_client(google_sheets_raw_creds)
    
    gspreadsheet = gspread_client.open_by_key(spreadsheet_key)
    gworksheet = gspreadsheet.worksheet(worksheet_name)

    gworksheet.append_rows(df_recent_odds.values.tolist())



def main():
    odds_api_key = odds_api_key_secret
    google_sheets_raw_creds = gsheet_creds_json_secret
    spreadsheet_key = spreadsheet_key_secret
    worksheet_name = 'Betting Odds'

    append_most_recent_fanduel_nba_playoffs_odds_to_gsheet(odds_api_key,
                                                           google_sheets_raw_creds,
                                                           spreadsheet_key,
                                                           worksheet_name)


if __name__ == '__main__':
    main()

