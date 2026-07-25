import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# READ THE DATA
# ==========================================================

df = pd.read_csv("exp.csv")

# Convert the date column
df["date"] = pd.to_datetime(df["date"])

# Sort by date
df = df.sort_values("date")

# Weather and sensor values are recorded on different rows
df = df.ffill()

# ==========================================================
# REMOVE UNREALISTIC TEMPERATURE VALUES
# ==========================================================

temperature_columns = [
    "temp_in",
    "temp_out",
    "Temp42",
    "Temp43",
    "Temp323",
    "Temp26",
    "Temp19"
]

for col in temperature_columns:
    df.loc[(df[col] < -30) | (df[col] > 45), col] = np.nan

# ==========================================================
# CLEAN SENSOR 323
# ==========================================================

jump323 = df["Temp323"].diff().abs()
df.loc[jump323 > 5, "Temp323"] = np.nan

same323 = df["Temp323"].diff().abs() < 1e-6
groups323 = same323.ne(same323.shift()).cumsum()
length323 = same323.groupby(groups323).transform("sum")
df.loc[(same323) & (length323 > 200), "Temp323"] = np.nan

# ==========================================================
# CLEAN SENSOR 26
# ==========================================================

jump26 = df["Temp26"].diff().abs()
df.loc[jump26 > 5, "Temp26"] = np.nan

same26 = df["Temp26"].diff().abs() < 1e-6
groups26 = same26.ne(same26.shift()).cumsum()
length26 = same26.groupby(groups26).transform("sum")
df.loc[(same26) & (length26 > 200), "Temp26"] = np.nan

df["Temp323"] = df["Temp323"].interpolate(method="linear",limit=50,limit_direction="both")
df["Temp26"] = df["Temp26"].interpolate(method="linear",limit=50,limit_direction="both")

plt.rcParams["font.family"]="Times New Roman"
fig,ax=plt.subplots(figsize=(18,8))

ax.plot(df["date"],df["temp_in"],linewidth=1.8,label="Indoor air")
ax.plot(df["date"],df["temp_out"],linewidth=1.8,label="Outdoor air")
ax.plot(df["date"],df["Temp42"],linewidth=1.8,label="Sensor 42")
ax.plot(df["date"],df["Temp43"],linewidth=1.8,label="Sensor 43")
ax.plot(df["date"],df["Temp323"],linewidth=1.8,label="Sensor 323")
ax.plot(df["date"],df["Temp26"],linewidth=1.8,label="Sensor 26")
ax.plot(df["date"],df["Temp19"],linewidth=1.8,label="Sensor 19")

ax.set_title("Temperature evolution in the hemp wall",fontsize=26,fontweight="bold")
ax.set_xlabel("Date",fontsize=22,fontweight="bold")
ax.set_ylabel("Temperature (°C)",fontsize=22,fontweight="bold")

ax.set_ylim(-30,40)
ax.set_yticks(np.arange(-30,41,10))

ax.tick_params(axis="both",labelsize=18,width=1.5,length=8)

plt.setp(ax.get_xticklabels(),rotation=30,ha="right",fontsize=18,fontweight="bold")
plt.setp(ax.get_yticklabels(),fontsize=18,fontweight="bold")

for spine in ax.spines.values():
    spine.set_linewidth(1.4)

ax.grid(True,linestyle="--",linewidth=0.7,alpha=0.35)

ax.legend(fontsize=14,loc="center left",bbox_to_anchor=(1.02,0.5),frameon=True)

plt.tight_layout(rect=[0,0,0.82,1])
plt.savefig("Temperature_Hemp_Wall.png",dpi=600,bbox_inches="tight")
plt.show()
