from varkit.data import fetch_spot_price, daily_peak_mean
from varkit.var import historical_var
import pandas as pd
import argparse 

#argparser for running in terminal
parser = argparse.ArgumentParser()
parser.add_argument("ndays", type=int, help="Number of days to be included in calculation")
parser.add_argument("area", help="Area to fetch prices for")
parser.add_argument("--alpha", type=float, default=0.95, help="VaR confidence level")
args = parser.parse_args()

end=(pd.Timestamp.now().date())
start=end-pd.Timedelta(days=(args.ndays+1))

prices=fetch_spot_price(area=args.area, start=start, end=end)
daily=daily_peak_mean(prices)
pnl=daily.diff().dropna()

his_var=historical_var(pnl, alpha=args.alpha)
print(f"{args.alpha:.0%} historical VaR as of today is €{his_var:.2f} ({len(pnl)} observations over the past {args.ndays} days)")

if start<pd.Timestamp("2025-10-01").date():
    print(f"Fewer observations than {args.ndays} available as data before 01/10/2025 is unavailable in current implementation.")