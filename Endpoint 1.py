import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv("weather.csv")

df.event_start = pd.to_datetime(df.event_start).dt.tz_localize(None)

df.belief_horizon_in_sec = pd.to_timedelta(df.belief_horizon_in_sec, unit='s')

df.belief_horizon_in_sec = df["event_start"] + df["belief_horizon_in_sec"]

datenow = "2020-11-02 10:00:00"
datethen = "2020-11-02 11:49:21"


def getForcasts(now, then, df):
    """
    eturn the three kinds of forecasts that are most relevant for "then", given the knowledge you can assume was available at "now"
    :param now: type datetime, only thing we can assume to have format '%Y/%m/%d %H:%M:%S', "2020/11/02 10:33:33"
    :param then: type datetime, only thing we want
    :param df: type dataframe pandas,
    :return: temp, irri, wind
    """
    # datenow = now
    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
    nowSlice = df.loc[(df.event_start <= now)]
    # nowSlice
    # datethen = then
    then = datetime.strptime(then, '%Y-%m-%d %H:%M:%S')
    thenSlice = nowSlice.loc[nowSlice.belief_horizon_in_sec == then]
    if thenSlice.empty:
        bufdate = timedelta(seconds=30)
        end = now + bufdate
        start = now - bufdate
        dates = pd.date_range(start, end, freq="S")
        thenSlice = nowSlice.loc[nowSlice.belief_horizon_in_sec.isin(dates)]
    output = [i[0] + ": " + str(i[1]) for i in zip(thenSlice.sensor, thenSlice.event_value)]
    return output


print(getForcasts(datenow, datethen, df))
