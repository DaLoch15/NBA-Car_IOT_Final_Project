
from nba_api.live.nba.endpoints import scoreboard
import json

def fetch_todays_games():
    """
    Fetches the scoreboard for today's NBA games.
    Returns the raw data as a Python dictionary.
    """
    # Create a ScoreBoard object - this makes the API call
    board = scoreboard.ScoreBoard()
    
    # Get the data as a Python dictionary
    data = board.get_dict()
    
    return data

def display_games(data):
    """
    Parses and displays game information in a readable format.
    """
    # The scoreboard data is nested - games are inside 'scoreboard' -> 'games'
    games = data['scoreboard']['games']
    
    if not games:
        print("No games scheduled for today.")
        print("\nThis is normal - the NBA doesn't play every day.")
        print("Try running this script on a game day to see live data.")
        return
    
    print(f"Found {len(games)} game(s) today:\n")
    print("-" * 60)
    
    for game in games:
        # Extract team information
        home_team = game['homeTeam']
        away_team = game['awayTeam']
        
        # Extract scores (will be 0 if game hasn't started)
        home_score = home_team['score']
        away_score = away_team['score']
        
        # Extract team names
        home_name = home_team['teamName']
        away_name = away_team['teamName']
        
        # Extract game status
        game_status = game['gameStatusText']
        game_id = game['gameId']
        
        # Display the information
        print(f"Game ID: {game_id}")
        print(f"{away_name}: {away_score}  @  {home_name}: {home_score}")
        print(f"Status: {game_status}")
        print("-" * 60)

def save_raw_data(data, filename="raw_scoreboard_data.json"):
    """
    Saves the complete raw API response to a file.
    This lets you explore the full data structure.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nRaw data saved to {filename}")
    print("Open this file to explore all available fields.")

# Main execution
if __name__ == "__main__":
    print("Fetching NBA scoreboard data...\n")
    
    try:
        data = fetch_todays_games()
        display_games(data)
        save_raw_data(data)
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("\nPossible causes:")
        print("- No internet connection on the Pi")
        print("- NBA.com API is temporarily unavailable")
        print("- nba_api package needs updating")