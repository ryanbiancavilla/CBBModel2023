from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import numpy as np

# Define the find_team function here
def find_team(team_name):
    # Assuming 'kenpom' is a pandas DataFrame with team information
    team_info = kenpom[kenpom['Team'] == team_name]
    
    if not team_info.empty:
        return team_info
    else:
        # Return a default value or handle the case when the team is not found
        return pd.DataFrame()  # Empty DataFrame if not found


#Load the team name mapping from an Excel file
team_name_mapping = pd.read_excel('CBBTeamsDatabase.xlsx', header=None, names=['KenPom', 'Slate'])

url = 'https://kenpom.com/'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
r = requests.get(url, headers=header)

soup = BeautifulSoup(r.text, 'lxml')
table = soup.find('table', id='ratings-table')

desired_headers = ['Team', 'AdjO', 'AdjD', 'AdjT']

headers = table.find_all('th')
titles = []

for i in headers:
    title = i.text
    if title in desired_headers:
        titles.append(title)
        if len(titles) == 4:
            break

df = pd.DataFrame(columns=titles)

indices_to_extract = [1, 5, 7, 9]

rows = table.find_all('tr')
data_list = []

for row in rows[1:]:
    data = row.find_all('td')

    if len(data) >= max(indices_to_extract) + 1:
        row_data = [data[indices_to_extract[0]].text]
        for index in indices_to_extract[1:]:
            row_data.append(float(data[index].text))
        data_list.append(row_data)

kenpom = pd.DataFrame(data_list, columns=['Team', 'AdjO', 'AdjD', 'AdjT'])
#print(kenpom)
# League Averages
avg_adjO = kenpom['AdjO'].mean()
avg_adjD = kenpom['AdjD'].mean()
avg_adjT = kenpom['AdjT'].mean()

#Define the API URL for the Odds
api_url = 'https://www.oddsshark.com/api/ticker/ncaab?_format=json'

#Send a GET request to the API
r = requests.get(api_url)

#Parse the JSON data
data = r.json()

#Function to extract specific fields from a nested JSON structure and replace "None" with 0
def extract_fields_from_json(json_obj):
    matchups = []
    if isinstance(json_obj, dict):
        if "matches" in json_obj:
            for match in json_obj["matches"]:
                home_team = match.get("teams", {}).get("home", {})
                away_team = match.get("teams", {}).get("away", {})
                status = match.get("status") or ""
                tv_station = match.get("tvStation") or ""
                status_tv_station = f"{status} + {tv_station}"
                if away_team.get('name') is not None:
                    away_data = {
                        "Home/Away": "Away",
                        "Team": away_team.get('name'),
                        "Spread": away_team.get('odds') or 0,
                        "Total": match.get("total") or 0,
                        "Status/TV": status_tv_station,
                    }
                    matchups.append(away_data)
                if home_team.get('name') is not None:
                    home_data = {
                        "Home/Away": "Home",
                        "Team": home_team.get('name'),
                        "Spread": home_team.get('odds') or 0,
                        "Total": match.get("total") or 0,
                        "Status/TV": status_tv_station,
                    }
                    matchups.append(home_data)

        for key, value in json_obj.items():
            if isinstance(value, (dict, list)):
                matchups.extend(extract_fields_from_json(value))
    elif isinstance(json_obj, list):
        for item in json_obj:
            matchups.extend(extract_fields_from_json(item))
    return matchups

#Extract the specified fields for each matchup
matchups = extract_fields_from_json(data)

#Create a pandas DataFrame from the extracted fields
df = pd.DataFrame(matchups)

#Remove blank rows at the beginning
df = df[df['Team'] != '']

#Reset the DataFrame index
df.reset_index(drop=True, inplace=True)

#Replace "NaN" values in the "Status/TV" column with an empty string
df["Status/TV"] = df["Status/TV"].fillna("")

#Print the DataFrame with the specified format
slate = df
#print(slate)
# Check if the length of slate is odd
if len(slate) % 2 == 1:
    #Add a placeholder row to make it even
    slate = pd.concat([slate, pd.DataFrame([['', '', '', '', '']], columns=slate.columns)], ignore_index=True)

#Initialize the DataFrame to store projected scores and statistics
proj_scores = pd.DataFrame(columns=['Teams', 'Proj Score', 'Proj Win %', 'Proj Spread', 'Vegas Spread', 'Spread Edge',
                                   'Proj Cover %', 'Proj Total', 'Vegas Total', 'Total Edge', 'Proj O/U %'])

#Number of Monte Carlo Sims
num_simulations = 100000

#Iterate through each matchup in slate
for index in range(0, len(slate), 2):
    away_team_name = slate.iloc[index]['Team']  #Get the current row's team name as the away team
    home_team_name = slate.iloc[index + 1]['Team']  #Get the next row's team name as the home team

    #Extract odds and totals from slate
    away_odds = slate.iloc[index]['Spread']
    away_total = slate.iloc[index]['Total']
    home_odds = slate.iloc[index + 1]['Spread']
    home_total = slate.iloc[index + 1]['Total']

    home_team = find_team(home_team_name)
    away_team = find_team(away_team_name)

    if not home_team.empty and not away_team.empty:
        #Calculate adjusted statistics for the away team
        AD = away_team['AdjD'].values[0]
        HD = home_team['AdjD'].values[0]

        #Calculate adjusted statistics for the home team
        AO = away_team['AdjO'].values[0]
        HO = home_team['AdjO'].values[0]

        AT = away_team['AdjT'].values[0]
        HT = home_team['AdjT'].values[0]

        #Calculate expected statistics
        Exp_OE_away = avg_adjO + (AO - avg_adjO) + (HD - avg_adjO)
        Exp_DE_away = avg_adjD + (HO - avg_adjD) + (AD - avg_adjD)
        Exp_T_away = avg_adjT + (AT - avg_adjT) + (HT - avg_adjT)

        Exp_OE_home = avg_adjO + (HO - avg_adjO) + (AD - avg_adjO)
        Exp_DE_home = avg_adjD + (AO - avg_adjD) + (HD - avg_adjD)
        Exp_T_home = avg_adjT + (AT - avg_adjT) + (HT - avg_adjT)

        #Calculate projected scores
        HCA = 1.75
        Home_projected_score = round((Exp_OE_home / 100 * Exp_T_home) + HCA, 2)
        Away_projected_score = round((Exp_OE_away / 100 * Exp_T_away) - HCA, 2)

        #Calculate spreads
        Home_spread = round(Away_projected_score - Home_projected_score, 2)
        Away_spread = round(Home_projected_score - Away_projected_score, 2)

        #Calculate over/under
        over_under = round(Home_projected_score + Away_projected_score, 2)

        #Calculate edge from projected spread and Vegas spread for each team
        Away_spread_edge = round(away_odds - Away_spread, 2)
        Home_spread_edge = round(home_odds - Home_spread, 2)

        #Calculate edge from projected total and Vegas total for each team
        Away_total_edge = round(over_under - away_total, 2)
        Home_total_edge = round(over_under - home_total, 2)

        #Initialize variables to count wins, covers, and over/unders
        home_win_count = 0
        away_win_count = 0
        home_cover_count = 0
        away_cover_count = 0
        over_count = 0

        for _ in range(num_simulations):
            #Simulate a game
            home_score_sim = np.random.normal(Home_projected_score, 10)  # Simulate home team's score
            away_score_sim = np.random.normal(Away_projected_score, 10)  # Simulate away team's score

            #Compare scores and count wins
            if home_score_sim > away_score_sim:
                home_win_count += 1
            else:
                away_win_count += 1

            #Compare scores and count covers
            if home_score_sim - away_score_sim > home_odds:
                home_cover_count += 1
            elif away_score_sim - home_score_sim > away_odds:
                away_cover_count += 1

            #Check if the total score is over the Vegas total
            if home_score_sim + away_score_sim > home_total:
                over_count += 1

        home_win_percentage = home_win_count / num_simulations * 100
        away_win_percentage = away_win_count / num_simulations * 100

        home_cover_percentage = home_cover_count / num_simulations * 100
        away_cover_percentage = away_cover_count / num_simulations * 100

        over_percentage = over_count / num_simulations * 100

        #Append the matchup's data to the proj_scores DataFrame
        data = {
            'Teams': [away_team_name, home_team_name],
            'Proj Score': [Away_projected_score, Home_projected_score],
            'Proj Win %': [away_win_percentage, home_win_percentage],
            'Proj Spread': [Away_spread, Home_spread],
            'Vegas Spread': [away_odds, home_odds],
            'Spread Edge': [Away_spread_edge, Home_spread_edge],
            'Proj Cover %': [away_cover_percentage, home_cover_percentage],
            'Proj Total': [over_under, over_under],
            'Vegas Total': [away_total, home_total],
            'Total Edge': [Away_total_edge, Home_total_edge],
            'Proj O/U %': [over_percentage, over_percentage],
        }

        proj_scores = pd.concat([proj_scores, pd.DataFrame(data)], ignore_index=True)

#Print the proj_scores DataFrame
print(proj_scores)