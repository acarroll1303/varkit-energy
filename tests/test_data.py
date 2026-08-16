from varkit.data import ParsingError, parse_energi_payload, daily_peak_mean
import pytest
import pandas as pd

def make_payload(rows):
    """rows: list of (time, area, price_eur) tuples."""
    return {"records": [
        {"TimeUTC": t, "PriceArea": a,
         "DayAheadPriceEUR": p, "DayAheadPriceDKK": p * 7.45}
        for t, a, p in rows
    ]}

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
            ("2026-08-01T12:00:00", "DK1", 20.0),
            ("2026-08-01T18:00:00", "DK1", 200.0)
        ])
    s=parse_energi_payload(payload, currency='EUR')
    assert daily_peak_mean(s).iloc[0]==15.0

def test_groupsby_day():
    """Daily peak means' indexes should be spaced evenly"""
    payload = make_payload([
                ("2026-08-01T10:00:00", "DK1", 120.0),
                ("2026-08-01T13:00:00", "DK1", 10.0),
                ("2026-08-01T16:00:00", "DK1", 20.0),
                ("2026-08-02T10:00:00", "DK1", 90.0),
                ("2026-08-02T11:00:00", "DK1", 10.0),
                ("2026-08-02T12:00:00", "DK1", 20.0),
                ("2026-09-03T10:00:00", "DK1", 60.0),
                ("2026-09-03T13:00:00", "DK1", 10.0),
                ("2026-09-03T16:00:00", "DK1", 20.0)
            ])
    s=parse_energi_payload(payload, currency='EUR')
    s=daily_peak_mean(s)
    assert s.index[1]-s.index[0]==pd.Timedelta(days=1)
    assert s.iloc[0] == 50.0
    assert s.iloc[1] == 40.0
    assert s.iloc[-1] == 30.0
    assert len(s)==33
    assert s.iloc[2:-1].isna().all()
