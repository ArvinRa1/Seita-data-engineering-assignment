import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv("weather.csv")
df.event_start = pd.to_datetime(df.event_start).dt.tz_localize(None)
df.belief_horizon_in_sec = pd.to_timedelta(df.belief_horizon_in_sec, unit='s')
df.belief_horizon_in_sec = df["event_start"] + df["belief_horizon_in_sec"]


def getForcasts(df, now, then):
    """
    eturn the three kinds of forecasts that are most relevant for "then", given the knowledge you can assume was available at "now"
    :param now: type datetime, only thing we can assume to have format '%Y/%m/%d %H:%M:%S', "2020-11-02 10:33:33"
    :param then: type datetime, only thing we want
    :param df: type dataframe pandas,
    :return: temp, irri, wind
    """
    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
    nowSlice = df.loc[(df.event_start <= now)]
    then = datetime.strptime(then, '%Y-%m-%d %H:%M:%S')
    thenSlice = nowSlice.loc[nowSlice.belief_horizon_in_sec == then]
    ## If the time we put as then has no information we search within 30 seconds of it to see if we have any data
    if thenSlice.empty:
        bufdate = timedelta(seconds=30)
        end = now + bufdate
        start = now - bufdate
        dates = pd.date_range(start, end, freq="S")
        thenSlice = nowSlice.loc[nowSlice.belief_horizon_in_sec.isin(dates)]

    output = [i[0] + ": " + str(i[1]) for i in zip(thenSlice.sensor, thenSlice.event_value)]
    return output


def getTomorrow(df, now):
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
        return "For the date given we do not have information for tomorrow please try another date"
    else:
        dfIr = tomorSlice.loc[df["sensor"] == "irradiance"]
        dfTem = tomorSlice.loc[df["sensor"] == "temperature"]
        dfWind = tomorSlice.loc[df["sensor"] == "wind speed"]
        warm = True if dfTem.event_value.mean() >= 20 else False
        sunny = True if dfIr.event_value.max() > 100 else False
        windy = True if dfWind.event_value.mean() >= 11 else False
        return f"warm: {str(warm)}", f"sunny: {str(sunny)}", f"windy: {str(windy)}"


def main():
    print("In here we can test the functions with custom dates.")
    print("Which method do you want to test put 1 for get forecasts and 2 for get Tomorrow.")
    meth = int(input("Here: ") or 2)
    if meth == 1:
        print("We are testing get forecasts")
        print("Please put dates in the format '%Y-%m-%d %H:%M:%S' or press enter for default value")
        print("For example 2020-11-02 10:00:00")
        now = input("Please put date now: ") or "2020-11-02 10:00:00"
        print("Example: 2020-11-02 11:49:21")
        then = input("Please put date then: ") or "2020-11-02 11:49:21"
        print(getForcasts(df, now, then))
    if meth == 2:
        print("We are testing get Tomorrow")
        print("Please put dates in the format '%Y-%m-%d %H:%M:%S' or press enter for default value")
        print("For example 2021-07-01 20:00:00")
        now = (input("Please put date now: ") or "2021-07-01 20:00:00")
        print(getTomorrow(df, now))


if __name__ == "__main__":
    main()
