import pandas as pd
import requests
import json

class ParsingError(Exception):
    '''Raise when parsing cannot work due to incorrect user input'''

def parse_energi_payload(payload,currency='EUR'):
    '''
    Returns a pandas Series with time index in UTC and DayAheadPrice in given currency from energi filtered response.
    Inputs: payload -> **Filtered to 1 market** .json response from request to api.energidataservice.dk/dataset/DayAheadPrices
            currency -> column to be used: 'EUR' or 'DKK'
    Output: pandas Series with UTC timeindex, DayAheadPrice in given currency
    '''
    if currency not in ['DKK','EUR']:
        raise ParsingError(f"currency {currency} is not EUR or DKK")
    df=pd.DataFrame(payload['records'])
    if df.PriceArea.nunique()>1:
        raise ParsingError(f"Payload should be filtered by 1 pricing area")
    df['TimeUTC']=pd.to_datetime(df['TimeUTC'],utc=True)
    df=df.set_index('TimeUTC').sort_index()
    df=df[f"DayAheadPrice{currency}"]
    return df

def fetch_spot_price(area, start=None, end=None, currency='EUR'):
    """Function to return pandas DataFrame from given filters to query api.energidataservice.dk/dataset/DayAheadPrices"""
    r=requests.get("https://api.energidataservice.dk/dataset/DayAheadPrices", 
                   params={"filter":json.dumps({"PriceArea":area}), "start":start, "end":end}, timeout=30)
    r.raise_for_status()
    try:
        payload = r.json()
    except ValueError as err:
        raise ParsingError(
            f"Response from {r.url} was not JSON. First 200 chars: {r.text[:200]}"
        ) from err
    return parse_energi_payload(payload,currency=currency)