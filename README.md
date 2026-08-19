# varkit
A python toolkit to get historical Value at Risk for Nordic power market electricity prices.

Fetches historical prices from https://www.energidataservice.dk API (Day Ahead Prices dataset) for a given market and finds the historical VaR from a rolling window of average daily peak-hours prices.

## How to Run
Navigate to folder in terminal and run below:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python run_var.py 319 DK1
```

Optional: `--alpha 0.99` for a different confidence level.

Run the tests with `python -m pytest`.

### Analysis notebook

`varanalysis.ipynb` compares the historical estimate against a fitted normal
distribution and shows where the normal fit breaks down in the tails.

```bash
pip install -e ".[dev,notebook]"
jupyter notebook varanalysis.ipynb
```

## Method 
Electricity prices for a single market for the previous n(user input integer) days is fetched from the energi data service API's DayAheadPrices dataset, which covers Nordic electricity prices from the 1st October 2025 (the date the Danish power market switched to 15 minute interval prices).  Data is then filtered from 08:00 to 20:00 Copenhagen local time (peak electricity usage times) and averaged to get the average daily price at peak hours. The daily peak hour price series is then differenced to get the daily profit and loss series. Since power prices can go negative, the log differences cannot be taken as the logarithm for negative prices are undefined, and using percentage returns would also mean the tails would be dominated by moves where the previous day's price is near 0.  Additionally, absolute changes allow for a simple interpretation of the output being in the form of €/MWh. Value at Risk is then calculated by finding the kth largest loss, where k=ceil(n*(1-alpha)), alpha = confidence level, n= series length. This is an order statistic rather than an interpolated value, so the output is an actual loss from a day in the dataset rather than calculated between adjacent observations, and represents the loss for a 1 MWh position.

## Results
**Taken on the rolling window from 1st October 2025 to 19th August 2026.**

Comparison Table for Historical VaR Estimates vs. a Normal Distribution.
| alpha | Historical Estimate| Fitted Normal Estimate |
| --- | --- | --- |
| 95.0% | €57.01 | €64.23 |
| 99.0% | €104.54 | €90.88 |
| 99.5% | €129.61 | €100.64 |


The standard normal approach clearly and heavily underestimates the extreme tail probabilities in the table above, making a historical VaR approach clearer. 

## Limitations and Next Steps
There are limitations to the estimates given from the historical VaR approach.

Firstly, the values at the tails can differ by almost €10/MWh, and since this is an order-statistic and given a small enough sample size(N=321), 1 extra observation can move the estimated Value at Risk significantly. 

Historical VaR gives no information about what's inside the tail. We know that there's roughly (/alpha)% probability that the loss will be less than the estimate, but nothing about how the probability of losses exceeding our estimate behaves. 

This method also assumes volatility in the power markets is stable and deviations are drawn from the same distribution, which is false given the known heteroskedasticity of these markets. 

Some of the next steps we can take to solve some of these include applying out of sample validation, calculating expected shortfall and GARCH modelling for volatility. 

   
