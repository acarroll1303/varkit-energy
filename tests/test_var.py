from varkit.var import historical_var


def test_historical_var_hand_calculated():
    """80% VaR of a 10-observation series is the 2nd worst loss."""
    pnl = [-8, 3, -2, 5, -15, 1, -4, 7, -1, 2]

    result = historical_var(pnl, alpha=0.80)

    assert result == 8.0


def test_alpha_monotonocity():
    """A 80% VaR cannot be worse than a 95% VaR for the same data"""
    pnl = [-10,-14,-10,20,4,5,2,18,2,3,1,-8,9,14,11,10,9,18,11,3]

    r1=historical_var(pnl, alpha=0.80)
    r2=historical_var(pnl, alpha=0.95)

    assert r1>=r2