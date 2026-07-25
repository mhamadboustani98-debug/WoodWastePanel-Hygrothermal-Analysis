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
    raise FileNotFoundError(
        "Could not find exp.csv or exp(3).csv in the current folder."
    )

print(f"Using file: {file_path.resolve()}")

# ==========================================================
# REQUIRED COLUMNS — REFERENCE WALL
# ==========================================================

required_columns = [
    "date","temp_in","humidity_in","temp_out","humidity_out",
    "Temp18","Hum18","Temp133","Hum133","Temp110","Hum110",
    "Temp126","Hum126","Temp141","Hum141","Temp41","Hum41",
    "Temp27","Hum27"
]

df = pd.read_csv(file_path, usecols=required_columns)
df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
df = df.dropna(subset=["date"]).sort_values("date").set_index("date")
df.index = df.index.tz_convert(None)

for col in required_columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

temperature_columns=["temp_in","temp_out","Temp18","Temp133","Temp110","Temp126","Temp141","Temp41","Temp27"]
humidity_columns=["humidity_in","humidity_out","Hum18","Hum133","Hum110","Hum126","Hum141","Hum41","Hum27"]

for col in temperature_columns:
    df.loc[(df[col]<-30)|(df[col]>45),col]=np.nan
for col in humidity_columns:
    df.loc[(df[col]<0)|(df[col]>100),col]=np.nan

hourly=df.resample("1h").mean()
for col in temperature_columns+humidity_columns:
    hourly[col]=hourly[col].interpolate(method="time",limit=6,limit_direction="both",limit_area="inside")

sensor_pairs={
"Indoor":("temp_in","humidity_in"),
"Outdoor":("temp_out","humidity_out"),
"18":("Temp18","Hum18"),
"133":("Temp133","Hum133"),
"110":("Temp110","Hum110"),
"126":("Temp126","Hum126"),
"141":("Temp141","Hum141"),
"41":("Temp41","Hum41"),
"27":("Temp27","Hum27")
}

for s,(t,h) in sensor_pairs.items():
    v=hourly[t].notna() & hourly[h].notna()
    hourly.loc[~v,[t,h]]=np.nan

def saturation_vapour_pressure(T):
    T=T.astype(float)
    ps=pd.Series(np.nan,index=T.index,dtype=float)
    pos=T>=0
    neg=T<0
    ps.loc[pos]=610.5*np.exp((17.269*T.loc[pos])/(237.3+T.loc[pos]))
    ps.loc[neg]=610.5*np.exp((21.875*T.loc[neg])/(265.5+T.loc[neg]))
    return ps

for s,(t,h) in sensor_pairs.items():
    hourly[f"Psat_{s}"]=saturation_vapour_pressure(hourly[t])
    hourly[f"Pv_{s}"]=(hourly[h]/100.0)*hourly[f"Psat_{s}"]

events=[
{"name":"Drop 1 - December","start":"2025-12-12 12:00:00","end":"2025-12-18 06:00:00","filename":"Reference_Drop1_VapourPressure.png"},
{"name":"Drop 2 - January","start":"2026-01-17 00:00:00","end":"2026-01-23 06:00:00","filename":"Reference_Drop2_VapourPressure.png"},
{"name":"Drop 3 - February","start":"2026-02-10 00:00:00","end":"2026-02-13 06:00:00","filename":"Reference_Drop3_VapourPressure.png"}]

plt.rcParams["font.family"]="Times New Roman"
plot_series=[("Pv_Indoor","Indoor air"),("Pv_Outdoor","Outdoor air"),("Pv_18","Sensor 18"),("Pv_133","Sensor 133"),("Pv_110","Sensor 110"),("Pv_126","Sensor 126"),("Pv_141","Sensor 141"),("Pv_41","Sensor 41"),("Pv_27","Sensor 27")]

def plot_event(event):
    event_data=hourly.loc[pd.Timestamp(event["start"]):pd.Timestamp(event["end"])].copy()
    if event_data.empty:
        return
    fig,ax=plt.subplots(figsize=(18,8))
    for c,l in plot_series:
        ax.plot(event_data.index,event_data[c],linewidth=1.8,label=l)
    ax.set_title(f"Reference wall – Water vapour pressure – {event['name']}",fontsize=26,fontweight="bold")
    ax.set_xlabel("Date",fontsize=22,fontweight="bold")
    ax.set_ylabel("Water vapour pressure (Pa)",fontsize=22,fontweight="bold")
    ax.set_ylim(0,2600)
    ax.set_yticks(np.arange(0,3000,100))
    if len(event_data)<=100:
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    else:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.tick_params(axis="both",labelsize=18,width=1.5,length=8)
    plt.setp(ax.get_xticklabels(),rotation=30,ha="right",fontsize=18,fontweight="bold")
    plt.setp(ax.get_yticklabels(),fontsize=18,fontweight="bold")
    for sp in ax.spines.values():
        sp.set_linewidth(1.4)
    ax.grid(True,linestyle="--",linewidth=0.7,alpha=0.35)
    ax.legend(fontsize=20,loc="upper right",bbox_to_anchor=(0.98,0.98),ncol=3,frameon=False,handlelength=1.3,handletextpad=0.4,columnspacing=1.2,labelspacing=0.5)
    plt.tight_layout()
    plt.savefig(event["filename"],dpi=600,bbox_inches="tight")
    plt.show()

for e in events:
    plot_event(e)

print("Finished. The three reference-wall figures were created.")
