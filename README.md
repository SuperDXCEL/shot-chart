# FEB SHOT CHART
Visualization of all FEB leagues shot attempts by each individual player for the 2025-26 season.
Using Plotly.js and Dash for Python, it renders the shot attempts by position, calculates the percentages and provides
two additional metrics, shot distribution and Points Per Shot Per Position

Install the required packages
```
pip install -r requirements.txt
```

Through the initial_scraping.py file, it scrapes the whole FEB website and gathers the attempts per league, group, team and player.

Run the obtained csv files through post_processing.py and render them by running app.py

```
cd scraping
python3 initial_scraping.py
python3 post_processing.py
cd ..
python3 app.py
```
## Tech stack
Python: Selenium, undetected_chromedriver, Dash

JavaScript: Plotly.js

Hosting: nginx
