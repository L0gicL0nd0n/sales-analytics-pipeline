"""Generate a SYNTHETIC raw sales file for a small creative business.

The data is randomly generated (fixed seed) and deliberately messy so the
pipeline has real cleaning work to do. It does not contain real client data.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 1200

services = {
    "Haircut": (8, 20, 0.50),          # (min price, max price, share of sales)
    "Custom Clothing": (25, 90, 0.20),
    "Art Commission": (30, 150, 0.15),
    "Beard Trim": (5, 12, 0.15),
}
names = list(services)
probs = [services[s][2] for s in names]

service = rng.choice(names, size=N, p=probs)
price = [round(rng.uniform(services[s][0], services[s][1]), 2) for s in service]

# Seasonal growth: more sales in later months
days = pd.date_range("2025-01-01", "2025-12-31")
weights = np.linspace(1, 2.2, len(days))
date = rng.choice(days, size=N, p=weights / weights.sum())

channel = rng.choice(["Instagram", "Walk-in", "Referral", "WhatsApp"], size=N, p=[0.35, 0.25, 0.25, 0.15])
client_id = rng.integers(1, 901, size=N)
payment = rng.choice(["cash", "card", "mobile money"], size=N, p=[0.5, 0.2, 0.3])

df = pd.DataFrame({
    "sale_id": np.arange(1, N + 1), "sale_date": pd.to_datetime(date).strftime("%Y-%m-%d"),
    "client_id": client_id, "service": service, "price": price,
    "channel": channel, "payment_method": payment,
})

# Inject realistic mess
df.loc[rng.choice(N, 25, replace=False), "price"] = np.nan
df.loc[rng.choice(N, 40, replace=False), "service"] = df["service"].str.upper()
df.loc[rng.choice(N, 30, replace=False), "channel"] = df["channel"].str.lower() + " "
df = pd.concat([df, df.sample(15, random_state=1)], ignore_index=True)   # duplicates
df.to_csv("data/raw/transactions.csv", index=False)
print(f"Wrote {len(df)} raw rows to data/raw/transactions.csv")
