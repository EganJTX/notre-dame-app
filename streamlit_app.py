import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import altair as alt

#--------------------Pull data from web for display--------------------

# Load the HTML page
url = 'http://alexanderbess.com/NDfootball_results2.php'  # <-- replace with your actual URL
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Try to find the first table
table = soup.find("table", id="gameListTable")
if not table:
    raise ValueError("No <table> found on the page.")

# Extract headers from <thead>
headers = []
thead = table.find('thead')
if thead:
    header_row = thead.find('tr')
    if header_row:
        headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
else:
    print("No <thead> found — will attempt to infer headers from first row in <tbody>.")

# Extract rows from <tbody> or all <tr> if <tbody> is missing
rows = []
tbody = table.find('tbody')
if tbody:
    row_tags = tbody.find_all('tr')
else:
    print("No <tbody> found — falling back to all <tr> in the table.")
    row_tags = table.find_all('tr')[1:]  # Skip header if present

for row in row_tags:
    cols = [td.get_text(strip=True) for td in row.find_all('td')]
    if cols:
        rows.append(cols)

# Use inferred headers if no <thead> was found
if not headers and rows:
    headers = [f"Column {i+1}" for i in range(len(rows[0]))]

# Create DataFrame
df = pd.DataFrame(rows, columns=headers)

# Display all rows
pd.set_option('display.max_rows', None)

# Update column headers
df.columns = ['Date', 'ND Rank', 'Result', 'Site', 'ND Coach', 'ND Score', 'Opp Score', 'Opponent', 'Opp Rank', 'Opp Final Rank', 'Opp Coach']


#---------------Massage Data for use-------------

import numpy as np

#create seasons for use in aggregate
df['Date'] = pd.to_datetime(df['Date'])
df['season'] = df['Date'].dt.year

# Update 'season'
df['season'] = np.where(df['Date'].dt.month == 1, df['season'] - 1, df['season'])

df['result_count_wins'] = np.where(df['Result'] == 'W', 1, 0)
df['result_count_losses'] = np.where(df['Result'] == 'L', 1, 0)

# Sort data to ensure correct counting order
df = df.sort_values(by=["ND Coach", "Date"])

# Add game_number column within each nd_coach group
df["game_number"] = df.groupby("ND Coach").cumcount() + 1

# Sort by nd_coach and game_number to maintain correct order
df = df.sort_values(by=["ND Coach", "game_number"])

# Add running sum for result_count_wins within each nd_coach group
df["running_wins"] = df.groupby("ND Coach")["result_count_wins"].cumsum()

df["running_win_perc"] = df["running_wins"]/df["game_number"]

# List of specific coaches who should be flagged as legends
legend_coaches = ["ROCKNE", "LEAHY","PARSEGHIAN","HOLTZ"]  # Replace with actual coach names

# Add the "is_legend" column to the dataframe
df["is_legend"] = df["ND Coach"].isin(legend_coaches)

#-----------App Display----------------

st.title("Notre Dame Football Analysis")
st.write(
    "Coming soon!"
)
