# import pandas as pd  # (version 1.0.0)
import dash  # (version 1.9.1) pip install dash==1.9.1
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime, timedelta

app = dash.Dash(__name__)

# -------------------------------------------------------------------------------
categories = ["observation_time", "temperature", "wind_speed", "precip", "humidity",
              "cloudcover", "feelslike", "uv_index", "visibility"]


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
    if thenSlice.empty:
        return "For the date given we do not have information for tomorrow please try another date"
    output = [i[0] + ": " + str(i[1]) + "\n" for i in zip(thenSlice.sensor, thenSlice.event_value)]
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
        return f"Warm: {str(warm)} \n", f"Sunny: {str(sunny)} \n", f"Windy: {str(windy)} \n"


# -------------------------------------------------------------------------------
app.layout = html.Div([
    html.Div(
        children=[
            html.H2(
                id="banner-title",
                children=[
                    html.A(
                        "Seita data engineering assignment",
                        style={
                            "text-decoration": "none",
                            "color": "inherit",
                        },
                    )
                ],
            ),
            html.A(),
        ],
        style={"text-align": "center", "padding": "20px 0px"}
    ),

    html.Div([
        dcc.Markdown('''We are testing get forecasts'''),
        dcc.Markdown('''Please put dates in the format '%Y-%m-%d %H:%M:%S' or press enter for default value'''),
        dcc.Input(id="input1", type="text", value="2020-11-02 10:00:00",
                  style={'marginRight': '10px'}),
        dcc.Input(id="input2", type="text", value="2020-11-02 11:49:21",
                  debounce=True),
        html.Div(id="output1"),

    ]),

    html.Div(children=[
        dcc.Markdown('''We are testing get Tomorrow'''),
        dcc.Markdown('''Please put dates in the format '%Y-%m-%d %H:%M:%S' or press enter for default value'''),
        dcc.Input(id="input3", type="text", value="2021-07-01 20:00:00", debounce=True),
        html.Div(id="output2"),

    ]),

])


###=========================================================================================

@app.callback(

    Output(component_id="output1", component_property="children"),
    [Input(component_id='input1', component_property='value'),
     Input(component_id='input2', component_property='value'),
     ])
def forecasts(input1, input2):
    return getForcasts(df, input1, input2)


###=========================================================================================
@app.callback(
    Output(component_id='output2', component_property='children'),
    Input(component_id='input3', component_property='value')
)
def tomorrow(input3):
    return getTomorrow(df, input3)


# -------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
