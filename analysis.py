"""Run SQL analysis on the warehouse and save charts + a summary CSV."""
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BLUE = "#1B75B5"
con = sqlite3.connect("data/warehouse.db")
q = lambda sql: pd.read_sql(sql, con)

monthly = q("SELECT month, SUM(price) AS revenue FROM sales GROUP BY month ORDER BY month")
service = q("SELECT service, SUM(price) AS revenue, AVG(price) AS avg_ticket FROM sales GROUP BY service ORDER BY revenue DESC")
channel = q("SELECT channel, COUNT(*) AS sales, SUM(price) AS revenue FROM sales GROUP BY channel ORDER BY revenue DESC")
repeat = q("SELECT 100.0*SUM(visits>1)/COUNT(*) AS pct FROM clients").iloc[0, 0]

def style(ax, title, ylabel):
    ax.set_title(title, fontweight="bold", loc="left"); ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(monthly["month"], monthly["revenue"], marker="o", color=BLUE, linewidth=2.5)
style(ax, "Monthly revenue (synthetic data)", "Revenue ($)"); plt.xticks(rotation=45); plt.tight_layout()
fig.savefig("outputs/monthly_revenue.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.barh(service["service"][::-1], service["revenue"][::-1], color=BLUE)
style(ax, "Revenue by service (synthetic data)", ""); ax.set_xlabel("Revenue ($)"); plt.tight_layout()
fig.savefig("outputs/revenue_by_service.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(channel["channel"], channel["revenue"], color=BLUE)
style(ax, "Revenue by acquisition channel (synthetic data)", "Revenue ($)"); plt.tight_layout()
fig.savefig("outputs/revenue_by_channel.png", dpi=150); plt.close(fig)

summary = pd.DataFrame({
    "metric": ["total_revenue", "total_sales", "avg_ticket", "repeat_client_pct", "best_service", "best_channel", "best_month"],
    "value": [round(monthly.revenue.sum(), 2), int(channel.sales.sum()), round(monthly.revenue.sum()/channel.sales.sum(), 2),
              round(repeat, 1), service.service[0], channel.channel[0], monthly.sort_values("revenue").month.iloc[-1]]})
summary.to_csv("outputs/summary.csv", index=False)
print(summary.to_string(index=False))
