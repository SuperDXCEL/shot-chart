from dash import Dash, html, dcc, Input, Output  # pip install dash
import dash_bootstrap_components as dbc   # pip install dash-bootstrap-components
import pandas as pd     # pip install pandas
import show_data_plotly

df = pd.read_csv("shots.csv")

TEAM_VALUES = df['team'].unique()
MIN = df["game_index"].min()
MAX = df["game_index"].max()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    html.H1("SHOT CHART TERCERA FEB GRUPO B-A 2025-26", style={'textAlign':'center', "color": "white", "fontFamily": "Helvetica", "fontWeight": "bold"}),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='team_category',
                value="team",
                clearable=False,
                options=TEAM_VALUES,
                placeholder='SELECT TEAM')
        ], width=2),
        dbc.Col([
            dcc.Dropdown(
                id='player_category',
                value=None,
                clearable=True,
                placeholder='SELECT PLAYER')
        ], width=2),
        dbc.Col([
            dcc.Dropdown(
                id='lower_bound',
                value="index",
                clearable=False,
                options=list(range(MIN, MAX)),
                placeholder="SELECT FIRST GAME")
        ], width=2),
        dbc.Col([
            dcc.Dropdown(
                id='upper_bound',
                value="index",
                clearable=False,
                options=list(range(MIN, MAX)),
                placeholder="SELECT LAST GAME")
        ], width=2)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='graph', figure={}, style={"height": "85vh", "width": "90vw"})
        ], width=20, md=6),
    ], className='mt-4'),
    ],
    style={
        "backgroundColor": "black",
        "minHeight": "100vh",
        "minWidth": "100vw",
    })

# Create interactivity between dropdown component and graph
@app.callback(
    Output('graph', 'figure'),
    Input('player_category', 'value'),
    Input('team_category', 'value'),
    Input('lower_bound', 'value'),
    Input('upper_bound', 'value')
)
def plot_data(player, team, lower, upper):

    # Build the Plotly figure
    fig = show_data_plotly.draw_court(player, team, lower, upper)
    return fig

# Select players available from team
@app.callback(
    Output("player_category", 'options'),
    Input("team_category", 'value')
)
def select_players(team):
    player_list = df[df["team"] == team]["player_number"].unique()
    int_list = [int(x) for x in player_list]
    int_list.sort()
    return int_list

if __name__ == '__main__':
    app.run(debug=False, port=8002)
