import pandas as pd

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
    df['TimeUTC']=pd.to_datetime(df['TimeUTC'])
    df=df.set_index('TimeUTC').sort_index()
    df=df[f"DayAheadPrice{currency}"]
    return df

def fetch_spot_price():
    pass