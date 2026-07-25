import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# ==========================================================
# FILE PATH
# ==========================================================

possible_files = [
    Path("exp.csv"),
    Path("exp(3).csv")
]

file_path = next((p for p in possible_files if p.exists()), None)

if file_path is None:
    raise FileNotFoundError("Could not find exp.csv or exp(3).csv in the current folder.")

print(f"Using file: {file_path.resolve()}")

required_columns = [
    "date","temp_in","humidity_in","temp_out","humidity_out",
    "Temp42","Hum42","Temp43","Hum43",
    "Temp323","Hum323","Temp26","Hum26","Temp19","Hum19"
]

df = pd.read_csv(file_path,usecols=required_columns)
df["date"] = pd.to_datetime(df["date"],errors="coerce",utc=True)
df = df.dropna(subset=["date"]).sort_values("date").set_index("date")
df.index = df.index.tz_convert(None)

for col in required_columns[1:]:
    df[col] = pd.to_numeric(df[col],errors="coerce")

temperature_columns=["temp_in","temp_out","Temp42","Temp43","Temp323","Temp26","Temp19"]
humidity_columns=["humidity_in","humidity_out","Hum42","Hum43","Hum323","Hum26","Hum19"]

for col in temperature_columns:
    df.loc[(df[col] < -30) | (df[col] > 45), col] = np.nan
for col in humidity_columns:
    df.loc[(df[col] < 0) | (df[col] > 100), col] = np.nan

hourly = df.resample("1h").mean()
for col in temperature_columns + humidity_columns:
    hourly[col] = hourly[col].interpolate(method="time",limit=6,limit_direction="both",limit_area="inside")

sensor_pairs={
"Indoor":("temp_in","humidity_in"),
"Outdoor":("temp_out","humidity_out"),
"42":("Temp42","Hum42"),
"43":("Temp43","Hum43"),
"323":("Temp323","Hum323"),
"26":("Temp26","Hum26"),
"19":("Temp19","Hum19")
}

for s,(t,h) in sensor_pairs.items():
    valid = hourly[t].notna() & hourly[h].notna()
    hourly.loc[~valid,t]=np.nan
    hourly.loc[~valid,h]=np.nan

def saturation_vapour_pressure(T):
    T=T.astype(float)
    psat=pd.Series(np.nan,index=T.index,dtype=float)
    pos=T>=0
    neg=T<0
    psat.loc[pos]=610.5*np.exp((17.269*T.loc[pos])/(237.3+T.loc[pos]))
    psat.loc[neg]=610.5*np.exp((21.875*T.loc[neg])/(265.5+T.loc[neg]))
    return psat

for s,(t,h) in sensor_pairs.items():
    hourly[f"Psat_{s}"]=saturation_vapour_pressure(hourly[t])
    hourly[f"Pv_{s}"]=(hourly[h]/100.0)*hourly[f"Psat_{s}"]

events=[
{"name":"Drop 1 - December","start":"2025-12-12 12:00:00","end":"2025-12-18 06:00:00","filename":"Hemp_Drop1_VapourPressure.png"},
{"name":"Drop 2 - January","start":"2026-01-17 00:00:00","end":"2026-01-23 06:00:00","filename":"Hemp_Drop2_VapourPressure.png"},
{"name":"Drop 3 - February","start":"2026-02-10 00:00:00","end":"2026-02-13 06:00:00","filename":"Hemp_Drop3_VapourPressure.png"}]

plt.rcParams["font.family"]="Times New Roman"

plot_series=[
("Pv_Indoor","Indoor air"),
("Pv_Outdoor","Outdoor air"),
("Pv_42","Sensor 42"),
("Pv_43","Sensor 43"),
("Pv_323","Sensor 323"),
("Pv_26","Sensor 26"),
("Pv_19","Sensor 19")
]

def plot_event(event):

    event_data = hourly.loc[pd.Timestamp(event["start"]):pd.Timestamp(event["end"])].copy()

    if event_data.empty:
        print(f"Warning: no data found for {event['name']}")
        return

    fig, ax = plt.subplots(figsize=(18,8))

    for column,label in plot_series:
        ax.plot(event_data.index,event_data[column],linewidth=1.8,label=label)

    ax.set_title(f"Hemp wall – Water vapour pressure – {event['name']}",
                 fontsize=26,fontweight="bold")
    ax.set_xlabel("Date",fontsize=22,fontweight="bold")
    ax.set_ylabel("Water vapour pressure (Pa)",fontsize=22,fontweight="bold")

    ax.set_ylim(0,3200)
    ax.set_yticks(np.arange(0,3201,500))

    # Same date format for all three figures
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    ax.tick_params(axis="both",labelsize=24,width=1.5,length=8)

    plt.setp(ax.get_xticklabels(),rotation=30,ha="right",
             fontsize=24,fontweight="bold")
    plt.setp(ax.get_yticklabels(),fontsize=24,fontweight="bold")

    for spine in ax.spines.values():
        spine.set_linewidth(1.4)

    ax.grid(True,linestyle="--",linewidth=0.7,alpha=0.35)

    ax.legend(fontsize=15,
              loc="upper right",
              bbox_to_anchor=(0.98,0.98),
              ncol=2,
              frameon=False,
              handlelength=1.3,
              handletextpad=0.4,
              columnspacing=1.2,
              labelspacing=0.5)

    plt.tight_layout()
    plt.savefig(event["filename"],dpi=600,bbox_inches="tight")
    print(f"Saved: {event['filename']}")
    plt.show()

for event in events:
    plot_event(event)

print("\\nFinished. The three hemp-wall figures were created.")
