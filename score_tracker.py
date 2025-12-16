
from nba_api.live.nba.endpoints import scoreboard
import time
from datetime import datetime


POLL_INTERVAL_SECONDS = 15  
TARGET_GAME_ID = None     

def fetch_all_games():
    """
    Fetches today's scoreboard and returns the list of games.
    """
    board = scoreboard.ScoreBoard()
    data = board.get_dict()
    return data['scoreboard']['games']

def find_game_by_id(games, game_id):
    """
    Finds a specific game from the games list by its ID.
    Returns None if not found.
    """
    for game in games:
        if game['gameId'] == game_id:
            return game
    return None

def get_game_scores(game):
    """
    Extracts score information from a game dictionary.
    Returns a dictionary with all relevant info.
    """
    return {
        'home_team': game['homeTeam']['teamName'],
        'away_team': game['awayTeam']['teamName'],
        'home_score': game['homeTeam']['score'],
        'away_score': game['awayTeam']['score'],
        'status': game['gameStatusText'],
        'game_id': game['gameId']
    }

def display_available_games():
    """
    Shows all available games and lets user pick one.
    Returns the selected game ID.
    """
    print("Fetching today's games...\n")
    games = fetch_all_games()
    
    if not games:
        print("No games available today.")
        return None
    
    print("Available games:")
    print("-" * 50)
    
    for i, game in enumerate(games):
        info = get_game_scores(game)
        print(f"[{i + 1}] {info['away_team']} @ {info['home_team']}")
        print(f"    Score: {info['away_score']} - {info['home_score']}")
        print(f"    Status: {info['status']}")
        print(f"    Game ID: {info['game_id']}")
        print()
    
    # Get user selection
    while True:
        try:
            choice = input("Enter game number to track (or 'q' to quit): ")
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(games):
                selected_game = games[index]
                return selected_game['gameId']
            else:
                print(f"Please enter a number between 1 and {len(games)}")
        except ValueError:
            print("Please enter a valid number")

def track_game(game_id):
    """
    Main tracking loop. Polls the specified game and detects score changes.
    """
    print(f"\nStarting to track game {game_id}")
    print(f"Polling every {POLL_INTERVAL_SECONDS} seconds")
    print("Press Ctrl+C to stop\n")
    print("=" * 60)
    
    # State variables to track previous scores
    previous_home_score = None
    previous_away_score = None
    home_team_name = None
    away_team_name = None
    
    while True:
        try:
            # Fetch current data
            games = fetch_all_games()
            game = find_game_by_id(games, game_id)
            
            if game is None:
                print(f"Game {game_id} not found. It may have ended.")
                break
            
            # Extract current scores
            info = get_game_scores(game)
            current_home_score = info['home_score']
            current_away_score = info['away_score']
            
            # Store team names on first fetch
            if home_team_name is None:
                home_team_name = info['home_team']
                away_team_name = info['away_team']
            
            # Get current timestamp for logging
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # First iteration: establish baseline
            if previous_home_score is None:
                print(f"[{timestamp}] Initial score: {away_team_name} {current_away_score} - {home_team_name} {current_home_score}")
                print(f"[{timestamp}] Game status: {info['status']}")
                print("-" * 60)
            else:
                # Calculate score changes
                home_delta = current_home_score - previous_home_score
                away_delta = current_away_score - previous_away_score
                
                # Report any scoring
                if home_delta > 0:
                    print(f"[{timestamp}] >>> {home_team_name} (HOME) scored {home_delta} point(s)!")
                    print(f"           New score: {away_team_name} {current_away_score} - {home_team_name} {current_home_score}")
                    print("-" * 60)
                
                if away_delta > 0:
                    print(f"[{timestamp}] >>> {away_team_name} (AWAY) scored {away_delta} point(s)!")
                    print(f"           New score: {away_team_name} {current_away_score} - {home_team_name} {current_home_score}")
                    print("-" * 60)
                
                # If no change, just show a heartbeat every poll (optional, can comment out)
                if home_delta == 0 and away_delta == 0:
                    print(f"[{timestamp}] No change. Score: {away_team_name} {current_away_score} - {home_team_name} {current_home_score} | Status: {info['status']}")
            
            # Update previous scores for next iteration
            previous_home_score = current_home_score
            previous_away_score = current_away_score
            
            # Check if game has ended
            if info['status'] == 'Final':
                print(f"\n[{timestamp}] Game has ended!")
                print(f"Final score: {away_team_name} {current_away_score} - {home_team_name} {current_home_score}")
                break
            
            # Wait before next poll
            time.sleep(POLL_INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            print("\n\nTracking stopped by user.")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print("Retrying in 30 seconds...")
            time.sleep(30)

# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("NBA SCORE TRACKER")
    print("=" * 60)
    print()
    
    # Let user select a game
    game_id = display_available_games()
    
    if game_id:
        track_game(game_id)
    else:
        print("No game selected. Exiting.")