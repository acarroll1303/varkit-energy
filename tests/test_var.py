from varkit.var import *
import requests
import json
import pandas as pd
import pytest


def test_historical_var_hand_calculated():
    """80% VaR of a 10-observation series is the 2nd worst loss."""
    pnl = [-8, 3, -2, 5, -15, 1, -4, 7, -1, 2]

    result = historical_var(pnl, alpha=0.80)

    assert result == 8.0


def test_alpha_monotonocity():
    """A 80% VaR cannot be greater than a 95% VaR for the same data"""
    pnl = [-10,-14,-10,20,4,5,2,18,2,3,1,-8,9,14,11,10,9,18,11,3]

    r1=historical_var(pnl, alpha=0.80)
    r2=historical_var(pnl, alpha=0.95)

    assert r1<=r2

def test_market_entry():
    """API request must filter to 1 pricing area"""
    r=requests.get("https://api.energidataservice.dk/dataset/DayAheadPrices", params={"filter":json.dumps({"PriceArea":["DK1","DK2"]})}, timeout=30)
    payload=r.json()
    with pytest.raises(ParsingError,match='area'):
        parse_energi_payload(payload,'DKK')

def test_currency():
    """API request must filter to either DKK or EURO"""
    r=requests.get("https://api.energidataservice.dk/dataset/DayAheadPrices", params={"filter":json.dumps({"PriceArea":["DK1"]})}, timeout=30)
    payload=r.json()
    with pytest.raises(ParsingError,match='currency'):
        parse_energi_payload(payload,currency='USD')
