import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ==========================
# Load data
# ==========================
df = pd.read_csv("exp.csv")

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")
df = df.ffill()

# ==========================
# Relative humidity sensors
# ==========================
hum_cols = [
    "humidity_in",
    "humidity_out",
    "Hum18",
    "Hum133",
    "Hum110",
    "Hum126",
    "Hum141",
    "Hum41",
    "Hum27"
]

# Remove unrealistic values
for col in hum_cols:
    df.loc[(df[col] < 0) | (df[col] > 100), col] = np.nan

# ==========================
# Figure style
# ==========================
plt.rcParams["font.family"] = "Times New Roman"

fig, ax = plt.subplots(figsize=(30, 10))

# ==========================
# Plot
# ==========================
ax.plot(df["date"], df["humidity_in"], linewidth=1.2, label="Indoor air")
ax.plot(df["date"], df["humidity_out"], linewidth=1.2, label="Outdoor air")
ax.plot(df["date"], df["Hum18"], linewidth=1.2, label="Sensor 18")
ax.plot(df["date"], df["Hum133"], linewidth=1.2, label="Sensor 133")
ax.plot(df["date"], df["Hum110"], linewidth=1.2, label="Sensor 110")
ax.plot(df["date"], df["Hum126"], linewidth=1.2, label="Sensor 126")
ax.plot(df["date"], df["Hum141"], linewidth=1.2, label="Sensor 141")
ax.plot(df["date"], df["Hum41"], linewidth=1.2, label="Sensor 41")
ax.plot(df["date"], df["Hum27"], linewidth=1.2, label="Sensor 27")

# ==========================
# Title
# ==========================
ax.set_title(
    "Relative humidity evolution in the reference wall",
    fontsize=26,
    fontweight="bold"
)

ax.set_xlabel(
    "Date",
    fontsize=22,
    fontweight="bold"
)

ax.set_ylabel(
    "Relative humidity (%)",
    fontsize=22,
    fontweight="bold"
)

# ==========================
# Axis
# ==========================
ax.set_ylim(0, 100)
ax.set_yticks(np.arange(0, 101, 10))

ax.tick_params(axis="both", labelsize=18)

for tick in ax.get_xticklabels():
    tick.set_fontweight("bold")

for tick in ax.get_yticklabels():
    tick.set_fontweight("bold")

ax.xaxis.set_major_locator(mdates.DayLocator(interval=15))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.35)

# ==========================
# Legend BELOW graph
# ==========================
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.22, -0.2),
    ncol=5,
    fontsize=15,
    frameon=False,
    handlelength=1.3,
    handletextpad=0.4,
    columnspacing=1.2
)

plt.tight_layout()

# ==========================
# Save
# ==========================
plt.savefig(
    "Reference_wall_relative_humidity.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
