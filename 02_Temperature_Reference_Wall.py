import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# READ THE DATA
# ==========================================================

df = pd.read_csv("exp.csv")

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

# Weather and sensors are on different rows
df = df.ffill()

# ==========================================================
# REMOVE UNREALISTIC TEMPERATURES
# ==========================================================

temperature_columns = [
    "temp_in",
    "temp_out",
    "Temp18",
    "Temp133",
    "Temp110",
    "Temp126",
    "Temp141",
    "Temp41",
    "Temp27"
]

for col in temperature_columns:
    df.loc[(df[col] < -30) | (df[col] > 45), col] = np.nan

# ==========================================================
# FIGURE
# ==========================================================

plt.rcParams["font.family"] = "Times New Roman"

fig, ax = plt.subplots(figsize=(18,8))

ax.plot(df["date"], df["temp_in"], linewidth=1.2, label="Indoor air")
ax.plot(df["date"], df["temp_out"], linewidth=1.2, label="Outdoor air")
ax.plot(df["date"], df["Temp18"], linewidth=1.2, label="Sensor 18")
ax.plot(df["date"], df["Temp133"], linewidth=1.2, label="Sensor 133")
ax.plot(df["date"], df["Temp110"], linewidth=1.2, label="Sensor 110")
ax.plot(df["date"], df["Temp126"], linewidth=1.2, label="Sensor 126")
ax.plot(df["date"], df["Temp141"], linewidth=1.2, label="Sensor 141")
ax.plot(df["date"], df["Temp41"], linewidth=1.2, label="Sensor 41")
ax.plot(df["date"], df["Temp27"], linewidth=1.2, label="Sensor 27")

# ==========================================================
# TITLES
# ==========================================================

ax.set_title(
    "Temperature evolution in the reference wall",
    fontsize=26,
    fontweight="bold"
)

ax.set_xlabel(
    "Date",
    fontsize=22,
    fontweight="bold"
)

ax.set_ylabel(
    "Temperature (°C)",
    fontsize=22,
    fontweight="bold"
)

# ==========================================================
# AXES
# ==========================================================

ax.set_ylim(-30,40)
ax.set_yticks(np.arange(-30,41,10))

ax.tick_params(
    axis="both",
    labelsize=18,
    width=1.5,
    length=8
)

plt.setp(
    ax.get_xticklabels(),
    rotation=30,
    ha="right",
    fontsize=18,
    fontweight="bold"
)

plt.setp(
    ax.get_yticklabels(),
    fontsize=18,
    fontweight="bold"
)

for spine in ax.spines.values():
    spine.set_linewidth(1.4)

# ==========================================================
# GRID
# ==========================================================

ax.grid(
    True,
    linestyle="--",
    linewidth=0.7,
    alpha=0.35
)

# ==========================================================
# LEGEND
# ==========================================================

ax.legend(
    fontsize=12,
    ncol=2,
    frameon=True,
    loc="upper right"
)

# ==========================================================
# SAVE
# ==========================================================

plt.tight_layout()

plt.savefig(
    "Temperature_Reference_Wall.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
