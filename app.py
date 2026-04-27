from dash import Dash, html, dcc, Input, Output  # pip install dash
import dash_bootstrap_components as dbc   # pip install dash-bootstrap-components
import pandas as pd     # pip install pandas
import show_data_plotly
import utilities

df = pd.read_csv("scraping/LF ENDESA_shots.csv")

LEAGUE_VALUES = ["LF ENDESA", "PRIMERA FEB", "SEGUNDA FEB", "TERCERA FEB", "LIGA U", "COPA ESPAÑA"]
TEAM_VALUES = None

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
dbc.Row([
    dbc.Col(html.Img(src="assets/feb_logo.png", style={"height": "60px", "width": "auto"}), width="auto"),
    dbc.Col(html.H1("SHOT CHART FEB", style={"color": "white", "fontFamily": "Helvetica", "fontWeight": "bold"}), align="center"),
], className="mb-3", align="center", style={
    "padding": "2vh 2vw",
}),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="league_category",
                value="LF ENDESA",
                clearable=False,
                options=LEAGUE_VALUES,
                placeholder='SELECT LEAGUE'
            )
        ], width=2),
        dbc.Col([
            dcc.Dropdown(
                id="group_category",
                value="group",
                clearable=False,
                placeholder='SELECT GROUP'
            )
        ], width=2),
        dbc.Col([
            dcc.Dropdown(
                id='team_category',
                value="team",
                clearable=True,
                placeholder='SELECT TEAM')
        ], width=2),
        dbc.Col([
            dcc.Dropdown(
                id='player_category',
                value=None,
                clearable=True,
                placeholder='SELECT PLAYER')
        ], width=2),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='graph', figure={}, style={"height": "85vh", "width": "99vw"})
        ], width=12, md=6),
    ], className='mt-4'),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='shot_distribution_pie_chart', figure={}, style={"height": "85vh", })
        ], width=6, md=6),
        dbc.Col([
            dcc.Graph(id='points_per_position_pie_chart', figure={}, style={"height": "85vh",})
        ], width=6, md=6),
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
    Input('league_category', 'value'),
    Input('group_category', 'value'),
    Input('team_category', 'value'),
    Input('player_category', 'value'),
)
def plot_data(league, group, team, player):
    player_number = utilities.get_player_number_from_name(player, team, group, df)
    print("CURRENT PLAYER NUMBER: ", player_number)
    fig = show_data_plotly.draw_court(player_number, team, group, league)
    return fig

@app.callback(
    Output('shot_distribution_pie_chart', 'figure'),
    Input('league_category', 'value'),
    Input('group_category', 'value'),
    Input('team_category', 'value'),
    Input('player_category', 'value'),
)
def show_shot_distribution_pie_chart(league, group, team, player):
    player_number = utilities.get_player_number_from_name(player, team, group, df)
    print("CURRENT PLAYER NUMBER: ", player_number)
    fig = show_data_plotly.draw_shot_distribution_pie_chart(player_number, team, group, currentLeagueName=league)
    return fig
    
@app.callback(
    Output('points_per_position_pie_chart', 'figure'),
    Input('league_category', 'value'),
    Input('group_category', 'value'),
    Input('team_category', 'value'),
    Input('player_category', 'value'),
)
def show_points_per_position_pie_chart(league, group, team, player):
    player_number = utilities.get_player_number_from_name(player, team, group, df)
    print("CURRENT PLAYER NUMBER: ", player_number)
    fig = show_data_plotly.draw_points_per_position_bar_chart(player_number, team, group, currentLeagueName=league)
    return fig

# Select available groups
@app.callback(
    Output("group_category", "options"),
    Input("league_category", "value")
)
def select_groups(league):
    global df
    df = pd.read_csv(f"scraping/{league}_shots.csv")
    return df["group"].unique()

# Select available teams
@app.callback(
    Output("team_category", "options"),
    Input("group_category", "value")
)
def select_teams(group):
    relevant_subset = df[df["group"] == group]
    team_list = relevant_subset["team"].unique()
    return team_list

# Select players available from team
@app.callback(
    Output("player_category", 'options'),
    Input('group_category', 'value'),
    Input("team_category", 'value')
)
def select_players(group, team):
    relevant_subset = df[df["group"] == group]
    relevant_subset = relevant_subset[relevant_subset["team"] == team]
    relevant_subset = relevant_subset[relevant_subset["home"] == True]
    player_list = relevant_subset["player_name"].unique()
    print("PLAYER LIST:", player_list)
    return player_list

if __name__ == '__main__':
    app.run(debug=False, port=8002)