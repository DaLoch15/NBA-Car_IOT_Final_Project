from nba_api.live.nba.endpoints import scoreboard
import json

# fetches today's nba games from the api
def fetch_todays_games():
    board = scoreboard.ScoreBoard()
    data = board.get_dict()
    return data

# displays game information in a readable format
def display_games(data):
    games = data['scoreboard']['games']
    
    if not games:
        print("No games scheduled for today.")
        return
    
    print(f"Found {len(games)} game(s) today:\n")
    print("-" * 60)
    
    for game in games:
        home_team = game['homeTeam']
        away_team = game['awayTeam']
        
        home_score = home_team['score']
        away_score = away_team['score']
        
        home_name = home_team['teamName']
        away_name = away_team['teamName']
        
        game_status = game['gameStatusText']
        game_id = game['gameId']
        
        print(f"Game ID: {game_id}")
        print(f"{away_name}: {away_score}  @  {home_name}: {home_score}")
        print(f"Status: {game_status}")
        print("-" * 60)

# saves the raw api response to a json file
def save_raw_data(data, filename="raw_scoreboard_data.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nRaw data saved to {filename}")

if __name__ == "__main__":
    print("Fetching NBA scoreboard data...\n")
    
    try:
        data = fetch_todays_games()
        display_games(data)
        save_raw_data(data)
        
    except Exception as e:
        print(f"Error fetching data: {e}")