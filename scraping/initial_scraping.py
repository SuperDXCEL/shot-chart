from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import undetected_chromedriver as uc
import time
import pandas as pd

MISSED_GAMES = 0

class FEBBot():
    def __init__(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        #options.add_argument('--user-data-dir="/home/nodev/snap/chromium/common/chromium/Default"')
        #options.add_argument('--profile-directory=Profile 1')
        self.driver = uc.Chrome(
                options=options,
                version_main=144
        )

    def accept_cookies(self):
        self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Aceptar')]").click()

    def get_data(self, index, team_name="EL VENTERO CBV", jersey_number=0):
        """
            Get shot chart for one game for the jersey number
        """
        # Move to game_index
        self.driver.find_element(By.XPATH, f"//option[contains(text(), 'Jornada {index}')]").click()
        # Get team <a> element, its parent's sibling contains the link to the game stats in an <a> element
        team_element = self.driver.find_elements(By.XPATH, "//a[text() = 'EL VENTERO CBV']")
        # Little workaround
        for i in range(0, len(team_element)):
            team_element = self.driver.find_elements(By.XPATH, "//a[text() = 'EL VENTERO CBV']")
            # Refetch because of stale elements
            if team_element[i].text == '':
                continue
            else:
                try:
                    parent_element = team_element[i].find_element(By.XPATH, "..")
                    parent_sibling = parent_element.find_element(By.XPATH, "following-sibling::*")
                    self.driver.execute_script("arguments[0].scrollIntoView(true)", parent_sibling)
                    parent_sibling.click()
                    break
                except Exception as e:
                    continue
        grafico_de_tiro_link = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Gráfico')]"))
        )
        grafico_de_tiro_link.click()
        # Deselect both teams
        t0_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@class = 'team-check t0']"))
        )
        t1_element = self.driver.find_element(By.XPATH, "//input[@class = 'team-check t1']")
        t0_element.click()
        t1_element.click()
        # Find out if the player on the team we are interested in is home or away on this game
        t0_team_name = t0_element.find_element(By.XPATH, "..").text
        home = False
        if t0_team_name == team_name:
            home = True
        # Select correct player
        player_check_divs = []
        if home:
            # Get number from home players
            player_check_divs = self.driver.find_elements(By.XPATH, "//div[@class = 'player-check-name t0']")
        else:
            player_check_divs = self.driver.find_elements(By.XPATH, "//div[@class = 'player-check-name t1']")
        player_div = None
        for i in range(0, len(player_check_divs)):
            if player_check_divs[i].text[0] == str(jersey_number):
                player_div = player_check_divs[i]
                break
        return player_div

    def get_data_from_game(self, game_index):
        """
            Change approach, instead of singular players we will
            go into each game, find out who the home team is and
            who the away team is and scrape all the shots in a row
            with their success, the player who shot that
            shot, the game index, against who it was, win or loss and the team the player is on.
            When this function is called we need to be in the specific game's shot chart.
        """
        try:
            home_team_shots = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'shoot t0')]"))
            )
            away_team_shots = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'shoot t1')]")
            home_team_parent = self.driver.find_element(By.XPATH, "//div[contains(@class, 'Team0')]")
            home_team = home_team_parent.find_element(By.XPATH, ".//div").text
            away_team_parent = self.driver.find_element(By.XPATH, "//div[contains(@class, 'Team1')]")
            away_team = away_team_parent.find_element(By.XPATH, ".//div").text
            shot_list = []
            home_team_players = [element.text for element in self.driver.find_elements(By.XPATH, "//div[contains(@class, 'player-check-name t0')]")]
            away_team_players = [element.text for element in self.driver.find_elements(By.XPATH, "//div[contains(@class, 'player-check-name t1')]")]
            for i in range(0, len(home_team_shots)):
                shot_class = home_team_shots[i].get_attribute("class").split(" ")
                player_number = int(shot_class[2][2:])
                player_name = ""
                for player_text in home_team_players:
                    if str(player_number) in player_text:
                        player_name = player_text.split('-', 1)[1]
                shot_success = bool(int(shot_class[3][-1]))
                shot_style = home_team_shots[i].get_attribute("style").split(";")
                left = shot_style[1].split(" ")[2]
                top = shot_style[0].split(" ")[1]
                shot = {"team": home_team, "player_number": player_number, "player_name": player_name, "left": left, "top": top, "success": shot_success, "game_index": game_index, "rival": away_team, "home": True}
                shot_list.append(shot)
            for i in range(0, len(away_team_shots)):
                shot_class = away_team_shots[i].get_attribute("class").split(" ")
                player_number = int(shot_class[2][2:])
                player_name = ""
                for player_text in home_team_players:
                    if str(player_number) in player_text:
                        player_name = player_text[3:]
                shot_success = bool(int(shot_class[3][-1]))
                shot_style = away_team_shots[i].get_attribute("style").split(";")
                left = shot_style[1].split(" ")[2]
                top = shot_style[0].split(" ")[1]
                shot = {"team": away_team, "player_number": player_number, "player_name": player_name, "left": left, "top": top, "success": shot_success, "game_index": game_index, "rival": home_team, "home": False}
                shot_list.append(shot)
            dataframe = pd.DataFrame(shot_list)
            return dataframe
        except Exception as e:
            print("EXCEPTION AT GET_DATA_FROM_GAME:", e)
            global MISSED_GAMES
            MISSED_GAMES += 1
            return pd.DataFrame({})

    def get_to_graphical_chart(self):
        grafico_de_tiro_link = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Gráfico')]"))
        )
        grafico_de_tiro_link.click()

    def get_games(self, game_index):
        """
            When the game index is chosen and clicked we call this function
        """
        game_links = self.driver.find_elements(By.XPATH, "//a[contains(@id, 'resultado')]")
        full_df = pd.DataFrame({})
        for i in range(0, len(game_links)):
            if i == 0: continue
            try:
                # Refetch stale elements
                game_links = self.driver.find_elements(By.XPATH, "//a[contains(@id, 'resultado')]")
                # Make sure game link is in view and click it
                self.driver.execute_script("arguments[0].scrollIntoView(true)", game_links[i])
                game_links[i].click()
                self.get_to_graphical_chart()
                df = self.get_data_from_game(game_index)
                full_df = pd.concat([full_df, df])
                print(df.head())
                self.driver.back()
            except Exception as e:
                continue
        return full_df

    def click_game_index(self, index):
        """
        """
        try:
            current_game_index_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//option[contains(text(), 'Jornada {index}')]"))
            )
            current_game_index_button.click()
        except Exception as e:
            print("EXCEPTION AT CLICK_GAME_INDEX:", e)

    def run(self):
        i = 1 
        full_df = pd.DataFrame({})
        while i < 20:
            self.click_game_index(i)
            df = self.get_games(i)
            full_df = pd.concat([full_df, df])
            i += 1
        df = None
        try:
            df = pd.read_csv("shots.csv")
            print("Length of rows before concatenating: ", len(full_df))
            full_df = pd.concat([df, full_df])
            print("Length of rows after concatenating (with possible duplicates): ", len(full_df))
            full_df.drop_duplicates()
            print("Length of rows after concatenating: ", len(full_df))
            global MISSED_GAMES
            full_df.to_csv("shots.csv")
            print("MISSED GAMES: ", MISSED_GAMES)
        except Exception as e:
            print("Could not open shots.csv as a dataframe", e)
            print("Writing to a new file called shots.csv in the current directory...")
            full_df.to_csv("shots.csv", index=False)

d = FEBBot()
d.driver.get("https://baloncestoenvivo.feb.es/resultados/tercerafeb/3/2025")
group_element = d.driver.find_element(By.XPATH, "//select[contains(@id, 'grupos')]")
group_element.click()
group_element.find_element(By.XPATH, "//option[contains(text(), 'B-A')]").click()
time.sleep(1.5)
d.run()
