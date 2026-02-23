"""
    Utilities module
"""

def get_player_number_from_name(player, team, df):
    """
        Self-explanatory
    """
    try:
        subset = df[df["player_name"] == player] 
        player_number = subset[subset["team"] == team]["player_number"]
        # Get the most common number
        player_number = player_number.mode()
        print("PLAYER MODE NUMBERRRRR: ", player_number)
        player_number = int(player_number.mode().iloc[0])
        print("PLAYER NUMBERRRRR: ", player_number)
        return player_number
    except Exception as e:
        print("EXCEPTION AT GET PLAYER NUMBER FROM NAME:", e)
