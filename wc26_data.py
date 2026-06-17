import requests
import json
import pandas as pd
import time

def get_wc26_data(matches): #list of matches
    dataframes = []
    estimated_time = len(matches)*6
    print(f"Approximate time of data pulling completion: {estimated_time} seconds.")
    
    for i in range (len(matches)):
        match_id = matches[i]
        #url1 = f"https://api.fifa.com/api/v3/live/football/{match_id}?language=en"
        url2 = f"https://api.fifa.com/api/v3/calendar/{match_id}?language=en"
        #url3 = f"https://api.fifa.com/api/v3/timelines/{match_id}?language=en"
    
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url2, headers=headers)


        if response.status_code == 200:
            try:
                match_info = response.json()
            except json.JSONDecodeError:
                print("Error: Could not decode JSON. Response text:") 
        else:
            print(f"Error: Request failed with status code {response.status_code}. Response text:")
            
        data_home = pd.DataFrame({
            "Date": [match_info['Date']],
            "Group": [match_info['GroupName'][0]['Description']],
            "Stage": [match_info['StageName'][0]['Description']],
            "TeamID": [match_info['Home']['IdTeam']],
            "TeamName": [match_info['Home']['ShortClubName']],
            "TeamAbbr": [match_info['Home']['Abbreviation']],
            "Formation": [match_info['Home']['Tactics']],
            "IdMatch": [match_info['IdMatch']],
            "GameNum": [match_info['MatchNumber']],
            "StatsId": [match_info['Properties']['IdIFES']]
        })

        data_away = pd.DataFrame({
            "Date": [match_info['Date']],
            "Group": [match_info['GroupName'][0]['Description']],
            "Stage": [match_info['StageName'][0]['Description']],
            "TeamID": [match_info['Away']['IdTeam']],
            "TeamName": [match_info['Away']['ShortClubName']],
            "TeamAbbr": [match_info['Away']['Abbreviation']],
            "Formation": [match_info['Away']['Tactics']],
            "IdMatch": [match_info['IdMatch']],
            "GameNum": [match_info['MatchNumber']],
            "StatsId": [match_info['Properties']['IdIFES']]
        })

        data_game = pd.concat([data_home,data_away]).reset_index()

        id_convert = match_info['Properties']['IdIFES']
        url = f"https://fdh-api.fifa.com/v1/stats/match/{id_convert}/teams.json"

        time.sleep(3)

        r = requests.get(url, headers=headers)
        data = r.json()

        formatted_dict = {
            team_id: {metric[0]: metric[1] for metric in metrics_list}
            for team_id, metrics_list in data.items()
        }

        stats_game = pd.DataFrame(formatted_dict).T.reset_index()
        full = pd.concat([data_game, stats_game], axis=1).drop(columns='index')
        dataframes.append(full)
        
        time.sleep(3)
        
    combined = pd.concat(dataframes, axis=0, ignore_index=True)
    print("Dataframe Complete")
    return combined

def get_country_rankings():
    url = "https://api.fifa.com/api/v3/fifarankings/rankings/live?gender=1&sportType=0&language=en"
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    results = data["Results"]

    rows = []

    for item in results:
        country_code = item.get("IdCountry")
        total_points = item.get("TotalPoints")
        region = item.get("ConfederationName")

        for t in item.get("TeamName", []):
            team_name = t.get("Description")

        rows.append({
            "TeamName": team_name,
            "IdCountry": country_code,
            "Confederation": region,
            "TotalPoints": total_points
            
        })

    df = pd.DataFrame(rows)
    print("Dataframe complete.")
    return df

def get_ids(file): #use full file name, not condensed path
    with open(f"{file}", "r", encoding="utf-8") as file:
        # 1. Read the entire file as a single string
        content = file.read()
        
        # 2. Split by commas and convert each item to an integer
        number_list = [int(num.strip()) for num in content.split(",") if num.strip()]

    return number_list
