import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv("weather.csv")

df.event_start = pd.to_datetime(df.event_start).dt.tz_localize(None)

df.belief_horizon_in_sec = pd.to_timedelta(df.belief_horizon_in_sec, unit='s')

df.belief_horizon_in_sec = df["event_start"] + df["belief_horizon_in_sec"]

datenow = "2021-07-01 20:00:00"

def getTomorrow(now, df):
    """
    :param now: string in this format '%Y-%m-%d %H:%M:%S'
    :param df: dateset given
    :return: a list of three values or printing no information for tomorrow try again warm, sunny, windy
    """
    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
    nowSlice = df.loc[(df.event_start <= now)]
    oneDay = timedelta(days=1)
    tomor = now + oneDay
    tomorSlice = nowSlice.loc[nowSlice.belief_horizon_in_sec.dt.date == tomor.date()]
    if tomorSlice.empty:
        print("For the date given we do not have information please try another date")
    dfIr = tomorSlice.loc[df["sensor"] == "irradiance"]
    dfTem = tomorSlice.loc[df["sensor"] == "temperature"]
    dfWind = tomorSlice.loc[df["sensor"] == "wind speed"]
    warm = True if dfTem.event_value.mean() >= 20 else False
    sunny = True if dfIr.event_value.max() > 100 else False
    windy = True if dfWind.event_value.mean() >= 11 else False
    return warm, sunny, windy

warm, sunny, windy = getTomorrow(datenow, df)
print("warm:", warm, "\nsunny:", sunny, "\nwindy:", windy)