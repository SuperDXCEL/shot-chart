import pandas as pd

def flip_shot(left, top, col):
    """
        If left value is > 50, left = 100 - left and top = 100 - top
    """
    if left > 50:
        left = 100 - left
        top = 100 - top
    if col == "left":
        return left
    else:
        return top

def modify_dataframe():
    """
        Keep only rows that have a certain team and a certain player from that team
        Flip the values that are over 50% left (this will have to be done for the original csv
        to avoid extra calculations at runtime)
    """
    df = pd.read_csv("../shots.csv")
    df["left"] = df["left"].str[:-1].astype(float)
    df["top"] = df["top"].str[:-1].astype(float)
    df["left"] = df.apply(lambda x: flip_shot(x["left"], x["top"], "left"), axis=1)
    df["top"] = df.apply(lambda x: flip_shot(x["left"], x["top"], "top"), axis=1)
    df["game_index"] = df["game_index"].astype(int)
    df.to_csv("../shots.csv", index=False)

if __name__ == "__main__":
    modify_dataframe()
