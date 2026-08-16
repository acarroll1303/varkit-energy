from varkit.var import historical_var
from varkit.data import ParsingError, parse_energi_payload, daily_peak_mean
import requests
import json
import pandas as pd
import pytest

def make_payload(rows):
    """rows: list of (time, area, price_eur) tuples."""
    return {"records": [
        {"TimeUTC": t, "PriceArea": a,
         "DayAheadPriceEUR": p, "DayAheadPriceDKK": p * 7.45}
        for t, a, p in rows
    ]}

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
    payload=make_payload([("2026-08-01T00:00:00", "DK1",1),                    
              ("2026-08-01T00:00:00", "DK2",1)])
    with pytest.raises(ParsingError,match='area'):
        parse_energi_payload(payload,'DKK')

def test_currency():
    """API request must filter to either DKK or EURO"""
    payload=make_payload([("2026-08-01T00:00:00", "DK1",1)])                 
    with pytest.raises(ParsingError,match='currency'):
        parse_energi_payload(payload,currency='USD')

def test_sort():
    """Sorting by time index should also move rows"""
    payload = make_payload([
        ("2026-08-01T02:00:00", "DK1", 30.0),
        ("2026-08-01T00:00:00", "DK1", 10.0),
        ("2026-08-01T01:00:00", "DK1", 20.0)
    ])
    s=parse_energi_payload(payload, currency='EUR')

    assert s.iloc[0]==10
    assert s.iloc[1]==20
    assert s.iloc[2]==30

def test_mean_hours_included():
    """Getting the Daily Peak Averages should only use the average of the peak hours"""
    payload = make_payload([
            ("2026-08-01T05:45:00", "DK1", 100.0),
            ("2026-08-01T10:00:00", "DK1", 10.0),
            ("2026-08-01T11:00:00", "DK1", 20.0)
        ])
    s=parse_energi_payload(payload, currency='EUR')
    assert daily_peak_mean(s).iloc[0]==15

def test_groupsby_day():
    """Daily peak means' indexes should be spaced evenly"""
    payload = make_payload([
                ("2026-08-01T10:00:00", "DK1", 120.0),
                ("2026-08-01T13:00:00", "DK1", 10.0),
                ("2026-08-01T16:00:00", "DK1", 20.0),
                ("2026-08-02T10:00:00", "DK1", 90.0),
                ("2026-08-02T11:00:00", "DK1", 10.0),
                ("2026-08-02T12:00:00", "DK1", 20.0),
                ("2026-08-03T10:00:00", "DK1", 60.0),
                ("2026-08-03T13:00:00", "DK1", 10.0),
                ("2026-08-03T16:00:00", "DK1", 20.0)
            ])
    s=parse_energi_payload(payload, currency='EUR')
    s=daily_peak_mean(s)
    assert s.index[1]-s.index[0]==s.index[2]-s.index[1]
    assert len(s)==3
    assert list(s)==[50.0,40.0,30.0]
