import pandas as pd
import numpy as np

def historical_var(pnl, alpha=0.95):
    "Returns a historical VaR number using previous n days of absolute returns data"
    #Inputs: alpha -> Confidence level: 0.95 means the 95th percentile when ordered from low to high in terms of loss. 
    #        PnL -> Array of historical returns.
    #Output: Returns the alpha VaR in terms of loss.
    if not 0<alpha<1:
        raise ValueError (f"alpha must be between 0 and 1, got {alpha}")
    min_obs = int(np.ceil(1 / (1 - alpha)))
    if len(pnl) < min_obs:
        raise ValueError(f"Need at least {min_obs} observations for {alpha:.0%} VaR, got {len(pnl)}")
    pnl = np.asarray(pnl, dtype=float) 
    pnl = pnl[~np.isnan(pnl)] 
    sortpnl=np.sort(pnl)
    k=int(np.ceil((1-alpha)*len(pnl))-1)
    return -(sortpnl[k])