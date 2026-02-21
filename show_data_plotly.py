"""
    Need to add total shot attempts and makes, alongside percentage
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import math

def get_specific_player_shots(player_number, team, lower_bound, upper_bound):
    """
        Return dataframe with specific player shots
    """
    df = pd.read_csv("shots.csv")
    df = df[df['player_number'] == player_number]
    df = df[df['team'] == team]
    df = df[(df['game_index'] >= lower_bound) & (df['game_index'] <= upper_bound)]
    print(df.head())
    return df

def draw_court(player_number, team, lower_bound, upper_bound):
    """
        Draw the court, and draw the points, between certain boundaries make hot zones
    """
    # Court measurements
    court_width = 14 # Half-court
    court_height = 15
    corner_three_left = {"x": 0, "y": 0.9} # Extends for 2.99 meters
    corner_three_right = {"x": 0, "y": (court_height - 0.9)} # Extends for 2.99 meters
    rim_from_baseline = 1.575
    three_point_arc_radius = 6.75
    center_for_arc = (rim_from_baseline, 7.5) # Draw arc from here for 6.75 - 1.575

    # Plot player's shot
    player_shot_df = get_specific_player_shots(player_number=player_number, team=team, lower_bound=lower_bound, upper_bound=upper_bound)
    x_factor = 50 / court_width
    y_factor = 100 / court_height
    player_shot_df["left"] = player_shot_df['left'] / x_factor
    player_shot_df["top"] = player_shot_df['top'] / y_factor
    np_shot_array = player_shot_df[["left", "top", "success"]].values

    # Separate between makes and misses
    makes = player_shot_df[player_shot_df["success"] == True]
    misses = player_shot_df[player_shot_df["success"] == False]
    #ax.plot(makes["left"], makes["top"], 'o', "b")
    fig = px.scatter(player_shot_df, x="left", y="top", color='success', template="plotly_dark", labels={"left": "x(m)", "top": "y(m)"})
    #ax.plot(misses["left"], misses["top"], 'o', "r")

    # Show percentages
    corner = find_corner_percentage(np_shot_array)
    wing = find_wing_percentage(np_shot_array)
    center = find_center_percentage(np_shot_array)
    paint = find_paint_percentage(np_shot_array)
    print("CORNER DICT: ", corner)
    print("WING DICT: ", wing)
    print("CENTER DICT: ", center)  
    print("PAINT DICT: ", paint)
    draw_hotzone_spots(fig, corner, wing, center, paint)


    # Plot court
    # ax.set_facecolor("white")
    draw_arc_between_two_points((2.99, corner_three_right["y"]), (2.99, corner_three_left["y"]), center_for_arc, fig, three_point_arc_radius)
    #ax.hlines(corner_three_left["y"], corner_three_left["x"], 2.99, 'black')
    fig.add_shape(type="line", y0=14.1, y1=14.1, x0=0, x1=2.99)
    #ax.hlines(corner_three_right["y"], corner_three_right["x"], 2.99, 'black')
    fig.add_shape(type="line", y0=0.9, y1=0.9, x0=0, x1=2.99)
    
    # Draw restricted area
    # left_vert_line = {"x": 0, "y": 7.5 + 2.45}
    # right_vert_line = {"x": 0, "y": 7.5 - 2.45}
    # ax.hlines(left_vert_line["y"], left_vert_line["x"], 5.8, 'black')
    # ax.hlines(right_vert_line["y"], right_vert_line["x"], 5.8, 'black')
    fig.add_shape(type="rect", x0=0, x1=5.8, y0=5.05, y1=9.95)
    
    # Free throw oval
    draw_arc_between_two_points((5.8, 7.5 + 1.83), (5.8, 7.5 - 1.83), (5.8, 7.5), fig, 1.83)
    #ax.vlines(5.8, 7.5-2.45, 7.5+2.45, 'black')
    
    # Semicircle
    draw_arc_between_two_points((1.25, 9), (1.25, 6), center_for_arc, fig, 1.25)
    
    fig.update_xaxes(
        range=[0, 15],
        autorange=False,
        visible=True
    )

    fig.update_yaxes(
        range=[0, 16],
        autorange=False,
        scaleanchor="x",
        scaleratio=1,
        visible=True
    )

    # Rim
    return fig

def draw_arc_between_two_points(point, point_two, center, fig, radius):
    """
        Use the ax returned by ax.gca() to render the arc between two points
    """
    # Angles where the arc meets the straight line are not -90 and 90, they are a bit smaller than that
    # Calculate the angle at x=0.9 y=1.575 and x=14.1 and y=1.575 relative to the x-axis where the arc intersects
    # Calculate angles
    theta2 = math.atan2(point[1] - center[1], point[0] - center[0])
    theta1 = math.atan2(point_two[1] - center[1], point_two[0] - center[0])

    # Ensure correct direction (counter-clockwise)
    if theta2 < theta1:
        theta2 += 2 * math.pi

    # Generate arc points
    theta = np.linspace(theta1, theta2, 200)

    arc_x = center[0] + radius * np.cos(theta)
    arc_y = center[1] + radius * np.sin(theta)

    # Add to plotly figure
    fig.add_trace(go.Scatter(
        x=arc_x,
        y=arc_y,
        mode='lines',
        line=dict(color='white'),
        showlegend=False
    ))

def draw_hotzone_spots(fig, corner=None, wing=None, center=None, paint=None):
    """
        Draw hotzones, 5 spots for threes, 5 spots for midrange, 1 spot for restricted area(layups) and one spot for midrange/floaters in the paint
    """
    text_positions = {
        "c3_right": (1, 14.75),
        "c3_left": (1, 0.65),
        "c2_left": (1, 2.5),
        "c2_right": (1, 12),
        "w_left": [(8, 3), (4, 3)],
        "w_right": [(8, 12), (4, 12)],
        "paint_near": (1.75, 7.5),
        "paint_outside": (4, 7.5),
        "center": [(6.5, 7.5), (10, 7.5)]
    }

    # Corner threes
    fig.add_shape(type="line", x0=2.99, x1=2.99, y0=0, y1=5.05)
    fig.add_shape(type="line", x0=2.99, x1=2.99, y0=9.95, y1=15)
    
    # 45 and middle separation
    fig.add_shape(type="line", x0=5.8, x1=14, y0=5.05, y1=5.05)
    fig.add_shape(type="line", x0=5.8, x1=14, y0=9.95, y1=9.95)
    
    # Add percentages
    for key in list(corner.keys()):
        makes = corner[key]["make"]
        misses = corner[key]["miss"]
        corner[key]["total_shots"] = makes + misses
        total_shots = corner[key]["total_shots"]
        percentage = 0
        if total_shots > 0:
            percentage = (makes / total_shots) * 100
        fig.add_annotation(x=text_positions[key][0], y=text_positions[key][1], text=str(int(percentage)) + "%", showarrow=False)
        fig.add_annotation(x=text_positions[key][0], y=text_positions[key][1] - 0.4, text=f"{makes} / {total_shots}", showarrow=False)
    
    # Paint
    makes = paint["makes"]
    misses = paint["makes"]
    restr_makes = paint["restricted_area_makes"]
    restr_misses = paint["restricted_area_misses"]
    paint["total_shots"] = makes + misses
    total_shots = paint["total_shots"]
    paint["total_restr_shots"] = restr_makes + restr_misses
    total_restr_shots = paint["total_restr_shots"] 
    percentage = 0
    restr_percentage = 0
    if total_shots > 0:
        percentage = (makes / total_shots) * 100
    if total_restr_shots > 0:
        restr_percentage = (restr_makes / total_restr_shots) * 100
    fig.add_annotation(x=text_positions["paint_outside"][0], y=text_positions["paint_outside"][1], text=str(int(percentage)) + "%", showarrow=False)
    fig.add_annotation(x=text_positions["paint_near"][0], y=text_positions["paint_near"][1], text=str(int(restr_percentage)) + "%", showarrow=False)
    fig.add_annotation(x=text_positions["paint_outside"][0], y=text_positions["paint_outside"][1] - 0.4, text=f"{makes} / {total_shots}", showarrow=False)
    fig.add_annotation(x=text_positions["paint_near"][0], y=text_positions["paint_near"][1] - 0.4, text=f"{restr_makes} / {total_restr_shots}", showarrow=False)

    for key in list(wing.keys()):
        print(key)
        th_makes = wing[key]["3_make"]
        th_misses = wing[key]["3_miss"]
        tw_makes = wing[key]["2_make"]
        tw_misses = wing[key]["2_miss"]
        total_3_shots = th_makes + th_misses
        total_2_shots = tw_makes + tw_misses
        th_percentage = 0
        tw_percentage = 0
        if total_3_shots > 0:
            th_percentage = (th_makes / (th_makes + th_misses)) * 100
        if total_2_shots > 0:
            tw_percentage = (tw_makes / (tw_makes + tw_misses)) * 100
        fig.add_annotation(x=text_positions[key][0][0], y=text_positions[key][0][1], text=str(int(th_percentage)) + "%", showarrow=False)
        fig.add_annotation(x=text_positions[key][0][0], y=text_positions[key][0][1]-0.4, text=f"{th_makes} / {total_3_shots}", showarrow=False)
        fig.add_annotation(x=text_positions[key][1][0], y=text_positions[key][1][1], text=str(int(tw_percentage)) + "%", showarrow=False)
        fig.add_annotation(x=text_positions[key][1][0], y=text_positions[key][1][1]-0.4, text=f"{tw_makes} / {total_2_shots}", showarrow=False)
    
    th_makes = center["3_make"]
    th_misses = center["3_miss"]
    tw_makes = center["2_make"]
    tw_misses = center["2_miss"]
    total_3_shots = th_makes + th_misses
    total_2_shots = tw_makes + tw_misses
    th_percentage = 0
    tw_percentage = 0
    if total_3_shots > 0:
        th_percentage = (th_makes / (th_makes + th_misses)) * 100
    if total_2_shots > 0:
        tw_percentage = (tw_makes / (tw_makes + tw_misses)) * 100
    fig.add_annotation(x=text_positions["center"][0][0], y=text_positions["center"][0][1], text=str(int(th_percentage)) + "%", showarrow=False)
    fig.add_annotation(x=text_positions["center"][0][0], y=text_positions["center"][0][1]-0.4, text=f"{th_makes} / {total_3_shots}", showarrow=False)
    fig.add_annotation(x=text_positions["center"][1][0], y=text_positions["center"][1][1], text=str(int(tw_percentage)) + "%", showarrow=False)
    fig.add_annotation(x=text_positions["center"][1][0], y=text_positions["center"][1][1]-0.4, text=f"{tw_makes} / {total_2_shots}", showarrow=False)

    return corner, wing, center, paint

def draw_shot_distribution_pie_chart(player, team, lower, upper):
    """
        Shot distribution percentages, has to be called after draw_hotzone_spots because of paint["total_shots"]
        and paint["total_restr_shots"]
    """
    player_shot_df = get_specific_player_shots(player_number=player, team=team, lower_bound=lower, upper_bound=upper)
    x_factor = 50 / 14
    y_factor = 100 / 15
    player_shot_df["left"] = player_shot_df['left'] / x_factor
    player_shot_df["top"] = player_shot_df['top'] / y_factor
    fig = px.scatter(player_shot_df, x="left", y="top")
    if fig:
        print("NOT HERE BUDDY", fig)
    np_shot_array = player_shot_df[["left", "top", "success"]].values

    corner = find_corner_percentage(np_shot_array)
    wing = find_wing_percentage(np_shot_array)
    center = find_center_percentage(np_shot_array)
    paint = find_paint_percentage(np_shot_array)
    corner, wing, center, paint = draw_hotzone_spots(fig, corner, wing, center, paint)
    shot_distribution_percentages = {}
    if corner and wing and center and paint:
        shot_distribution_percentages = {
            "threes": corner["c3_right"]["make"] + corner["c3_right"]["miss"] + corner["c3_left"]["make"] + corner["c3_left"]["miss"] + wing["w_left"]["3_make"] + wing["w_left"]["3_miss"] + wing["w_right"]["3_make"] + wing["w_right"]["3_miss"] + center["3_make"] + center["3_miss"],
            "midrange": corner["c2_right"]["make"] + corner["c2_right"]["miss"] + corner["c2_left"]["make"] + corner["c2_left"]["miss"] + wing["w_left"]["2_make"] + wing["w_left"]["2_miss"] + wing["w_right"]["2_make"] + wing["w_right"]["2_miss"] + center["2_make"] + center["2_miss"],
            "floaters/close_midrange": paint["total_shots"],
            "layups": paint["total_restr_shots"] 
    }
    labels = list(shot_distribution_percentages.keys())
    values = list(shot_distribution_percentages.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    fig.update_layout(title="Shot Distribution")
    return fig

def shot_in_area(shot):
    """
        Helper function for grouping wing and center shots
    """
    x_range = [2.99, 14]
    y_range = [0, 5.05]

def find_corner_percentage(shot_array):
    print("SHOT ARRAY: ", len(shot_array))
    data = {
        "c3_left": {
            "x_range": [0, 2.99],
            "y_range": [0, 0.9],
            "make": 0,
            "miss": 0,
            "color": "gray"
        },
        "c3_right": {
            "x_range": [0, 2.99],
            "y_range": [14.1, 15],
            "make": 0,
            "miss": 0,
            "color": "gray"
        },
        "c2_left": {
            "x_range": [0, 2.99],
            "y_range": [0.9, 5.05],
            "make": 0,
            "miss": 0,
            "color": "gray"
        },
        "c2_right": {
            "x_range": [0, 2.99],
            "y_range": [9.95, 14.1],
            "make": 0,
            "miss": 0,
            "color": "gray"
        },
    }
    keys = list(data.keys())
    # If any shot has x and y coordinates in the zones range, we count the makes and the misses
    # c3_left x = [0,0.01,...,2.99] y = [0, 0.01, ..., 0.9]
    for key in keys:
        for i in range(len(shot_array)):
            shot = shot_array[i]
            x_range = data[key]["x_range"]
            y_range = data[key]["y_range"]
            #if shot["left"] in x_range and shot["top"] in y_range:
            if shot[0] >= x_range[0] and shot[0] <= x_range[1] and shot[1] >= y_range[0] and shot[1] <= y_range[1]:
                #if shot["success"]:
                if shot[2]:
                    data[key]["make"] += 1
                else:
                    data[key]["miss"] += 1
    for key in list(data.keys()):
        if (data[key]["miss"] + data[key]["make"]) > 0:
            print(key, data[key]["make"] / (data[key]["miss"] + data[key]["make"]))
    return data

def find_paint_percentage(shot_array):
    """
        Needs refactor down the line, merge center, wing and paint percentage
        calculation functions if possible as they all share the same dictionary
        keys and all have a distance float to calculate
    """
    paint = {
        "x_range": [0, 5.8],
        "y_range": [5.05, 9.95],
        "restricted_area_makes": 0,
        "restricted_area_misses": 0,
        "makes": 0,
        "misses": 0,
        "color": "gray"
    }
    for i in range(len(shot_array)):
        shot = shot_array[i]
        x_range = paint["x_range"]
        y_range = paint["y_range"]
        if shot[0] < x_range[1] and shot[0] > x_range[0] and shot[1] < y_range[1] and shot[1] > y_range[0]:
            if distance(shot) <= 1.25:
                if shot[2]:
                   paint["restricted_area_makes"] += 1
                else:
                   paint["restricted_area_misses"] += 1
            else:
                if shot[2]:
                   paint["makes"] += 1
                else:
                   paint["misses"] += 1
    return paint
        
def find_wing_percentage(shot_array):
    """
        Need a different function as the wing needs more if conditions to know
        if a shot is a two or a three.
    """
    data = {
        "w_left": {
            "x_range": [2.99, 14],
            "y_range": [0, 5.05],
            "3_make": 0,
            "2_make": 0,
            "3_miss": 0,
            "2_miss": 0,
            "color": "gray"
        },
        "w_right": {
            "x_range": [2.99, 14],
            "y_range": [9.95, 15],
            "3_make": 0,
            "2_make": 0,
            "3_miss": 0,
            "2_miss": 0,
            "color": "gray"
        }
    }
    keys = list(data.keys())
    for key in keys:
        for i in range(len(shot_array)):
            shot = shot_array[i]
            x_range = data[key]["x_range"]
            y_range = data[key]["y_range"]
            if shot[0] >= x_range[0] and shot[0] <= x_range[1] and shot[1] >= y_range[0] and shot[1] <= y_range[1]:
                if shot[2]:
                    if distance(shot) >= 6.75:
                        data[key]["3_make"] += 1
                    else:
                        data[key]["2_make"] += 1
                else:
                    if distance(shot) >= 6.75:
                        data[key]["3_miss"] += 1
                    else:
                        data[key]["2_miss"] += 1
    for key in list(data.keys()):
        for subkey in list(data[key].keys()):
            print(key, subkey, data[key][subkey])
    return data

def find_center_percentage(shot_array):
    data = {
        "x_range": [5.8, 14],
        "y_range": [5.05, 9.95],
        "3_make": 0,
        "2_make": 0,
        "3_miss": 0,
        "2_miss": 0,
        "color": "gray"
    } 
    for i in range(len(shot_array)):
        shot = shot_array[i]
        x_range = data["x_range"]
        y_range = data["y_range"]
        if shot[0] >= x_range[0] and shot[0] <= x_range[1] and shot[1] >= y_range[0] and shot[1] <= y_range[1]:
            if shot[2]:
                if distance(shot) >= 6.75:
                    data["3_make"] += 1
                else:
                    data["2_make"] += 1
            else:
                if distance(shot) >= 6.75:
                    data["3_miss"] += 1
                else:
                    data["2_miss"] += 1
    return data 

def distance(shot):
    """
        Calculate the shot distance sqrt((x2 - x1)² + (y2 - y1)²)
    """
    hoop_location = [1.575, 7.5]
    distance = math.sqrt((shot[0] - hoop_location[0])**2 + (shot[1] - hoop_location[1])**2)
    print("DISTANCE: ", distance)
    return distance

t = "EL VENTERO CBV"
p = 0
l = 1
u = 18
