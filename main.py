"""
NBA Score-Controlled PiCar-4WD
==============================
Main program that integrates score tracking with car movement.

When the home team scores: car moves FORWARD
When the away team scores: car moves BACKWARD
Distance is proportional to points scored.

Usage:
    python main.py

Controls:
    Ctrl+C to stop the program safely
"""

from nba_api.live.nba.endpoints import scoreboard
import picar_4wd as fc
import time
from datetime import datetime

# =============================================================================
# CONFIGURATION - Adjust these values as needed
# =============================================================================

POLL_INTERVAL_SECONDS = 15      # How often to check scores (don't go below 10)
POWER = 50                      # Motor power (0-100)
SECONDS_PER_POINT = 0.25        # Calibrated: 0.25s = 1/3 foot per point

# =============================================================================
# NBA API FUNCTIONS
# =============================================================================

def fetch_all_games():
    """Fetches today's scoreboard and returns the list of games."""
    board = scoreboard.ScoreBoard()
    data = board.get_dict()
    return data['scoreboard']['games']

def find_game_by_id(games, game_id):
    """Finds a specific game from the games list by its ID."""
    for game in games:
        if game['gameId'] == game_id:
            return game
    return None

def get_game_info(game):
    """Extracts relevant information from a game dictionary."""
    return {
        'home_team': game['homeTeam']['teamName'],
        'away_team': game['awayTeam']['teamName'],
        'home_score': game['homeTeam']['score'],
        'away_score': game['awayTeam']['score'],
        'status': game['gameStatusText'],
        'game_id': game['gameId']
    }

# =============================================================================
# CAR CONTROL FUNCTIONS
# =============================================================================

def move_car(direction, points):
    """
    Move the car based on scoring.
    
    Args:
        direction: 'forward' or 'backward'
        points: number of points (determines distance)
    """
    duration = points * SECONDS_PER_POINT
    
    if direction == 'forward':
        fc.forward(POWER)
    else:
        fc.backward(POWER)
    
    time.sleep(duration)
    fc.stop()

def handle_score_change(home_delta, away_delta, home_team, away_team):
    """
    Process a score change and move the car accordingly.
    
    Returns a string describing what happened.
    """
    # Calculate net movement
    net_points = home_delta - away_delta
    
    if net_points == 0:
        # Both teams scored equally - no net movement
        if home_delta > 0:
            return f"Both teams scored {home_delta} - no net movement"
        return None  # No scoring at all
    
    if net_points > 0:
        # Home team has net positive - move forward
        move_car('forward', abs(net_points))
        return f"FORWARD {abs(net_points)} point(s) - {home_team} scoring!"
    else:
        # Away team has net positive - move backward
        move_car('backward', abs(net_points))
        return f"BACKWARD {abs(net_points)} point(s) - {away_team} scoring!"

# =============================================================================
# GAME SELECTION
# =============================================================================

def display_games_and_select():
    """Shows available games and lets user pick one to track."""
    print("\nFetching today's games...\n")
    
    try:
        games = fetch_all_games()
    except Exception as e:
        print(f"Error fetching games: {e}")
        return None
    
    if not games:
        print("No games available today.")
        print("The NBA doesn't play every day. Try again on a game day!")
        return None
    
    # Filter to show only live or upcoming games (not final)
    live_games = [g for g in games if get_game_info(g)['status'] != 'Final']
    final_games = [g for g in games if get_game_info(g)['status'] == 'Final']
    
    print("=" * 60)
    print("AVAILABLE GAMES")
    print("=" * 60)
    
    all_games = live_games + final_games  # Show live games first
    
    for i, game in enumerate(all_games):
        info = get_game_info(game)
        status_marker = "🟢 LIVE" if info['status'] not in ['Final', 'PPD'] and info['status'].startswith('Q') else ""
        if info['status'] == 'Final':
            status_marker = "⚫ FINAL"
        elif not status_marker:
            status_marker = "⏳ " + info['status']
        
        print(f"\n[{i + 1}] {info['away_team']} @ {info['home_team']}")
        print(f"    Score: {info['away_score']} - {info['home_score']}")
        print(f"    Status: {status_marker}")
    
    print("\n" + "=" * 60)
    
    # Get user selection
    while True:
        try:
            choice = input("\nEnter game number to track (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(all_games):
                selected = all_games[index]
                info = get_game_info(selected)
                
                # Warn if game is final
                if info['status'] == 'Final':
                    print(f"\nNote: This game has ended. The program will exit immediately.")
                    confirm = input("Continue anyway? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                
                return selected['gameId']
            else:
                print(f"Please enter a number between 1 and {len(all_games)}")
        except ValueError:
            print("Please enter a valid number")

# =============================================================================
# MAIN TRACKING LOOP
# =============================================================================

def run_tracker(game_id):
    """
    Main loop: polls the game and moves the car on score changes.
    """
    print("\n" + "=" * 60)
    print("STARTING NBA CAR TRACKER")
    print("=" * 60)
    print(f"\nGame ID: {game_id}")
    print(f"Poll interval: {POLL_INTERVAL_SECONDS} seconds")
    print(f"Movement: {SECONDS_PER_POINT}s per point = ~1/3 foot")
    print("\nPress Ctrl+C to stop safely")
    print("\n" + "-" * 60)
    
    # State tracking
    previous_home_score = None
    previous_away_score = None
    home_team = None
    away_team = None
    
    # Stats tracking
    total_forward = 0
    total_backward = 0
    
    while True:
        try:
            # Fetch current game data
            games = fetch_all_games()
            game = find_game_by_id(games, game_id)
            
            if game is None:
                print("\nGame not found! It may have been removed from the API.")
                break
            
            info = get_game_info(game)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Store team names on first run
            if home_team is None:
                home_team = info['home_team']
                away_team = info['away_team']
                print(f"\nTracking: {away_team} @ {home_team}")
                print("-" * 60)
            
            # First iteration - establish baseline
            if previous_home_score is None:
                previous_home_score = info['home_score']
                previous_away_score = info['away_score']
                print(f"[{timestamp}] Initial score: {away_team} {info['away_score']} - {home_team} {info['home_score']}")
                print(f"[{timestamp}] Status: {info['status']}")
                print(f"[{timestamp}] Car is ready. Waiting for scoring plays...")
                print("-" * 60)
            else:
                # Calculate deltas
                home_delta = info['home_score'] - previous_home_score
                away_delta = info['away_score'] - previous_away_score
                
                # Check for scoring
                if home_delta > 0 or away_delta > 0:
                    print(f"\n[{timestamp}] SCORING DETECTED!")
                    
                    if home_delta > 0:
                        print(f"    {home_team} (HOME) +{home_delta}")
                    if away_delta > 0:
                        print(f"    {away_team} (AWAY) +{away_delta}")
                    
                    # Move the car
                    result = handle_score_change(home_delta, away_delta, home_team, away_team)
                    
                    if result:
                        print(f"    CAR: {result}")
                        
                        # Update stats
                        net = home_delta - away_delta
                        if net > 0:
                            total_forward += net
                        else:
                            total_backward += abs(net)
                    
                    print(f"    New score: {away_team} {info['away_score']} - {home_team} {info['home_score']}")
                    print(f"    Car position: +{total_forward} / -{total_backward} points from start")
                    print("-" * 60)
                else:
                    # No scoring - just show status
                    print(f"[{timestamp}] {away_team} {info['away_score']} - {home_team} {info['home_score']} | {info['status']}")
                
                # Update previous scores
                previous_home_score = info['home_score']
                previous_away_score = info['away_score']
            
            # Check if game ended
            if info['status'] == 'Final':
                print("\n" + "=" * 60)
                print("GAME OVER!")
                print("=" * 60)
                print(f"Final: {away_team} {info['away_score']} - {home_team} {info['home_score']}")
                print(f"\nCar movement summary:")
                print(f"  Total forward:  {total_forward} points")
                print(f"  Total backward: {total_backward} points")
                print(f"  Net position:   {total_forward - total_backward:+d} points from start")
                break
            
            # Wait for next poll
            time.sleep(POLL_INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("STOPPED BY USER")
            print("=" * 60)
            print(f"\nCar movement summary:")
            print(f"  Total forward:  {total_forward} points")
            print(f"  Total backward: {total_backward} points")
            print(f"  Net position:   {total_forward - total_backward:+d} points from start")
            break
            
        except Exception as e:
            print(f"\n[{timestamp}] ERROR: {e}")
            print("Retrying in 30 seconds...")
            time.sleep(30)

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("   NBA SCORE-CONTROLLED PICAR-4WD")
    print("=" * 60)
    print()
    print("Home team scores → Car moves FORWARD")
    print("Away team scores → Car moves BACKWARD")
    print()
    
    try:
        # Let user select a game
        game_id = display_games_and_select()
        
        if game_id:
            run_tracker(game_id)
        else:
            print("\nNo game selected. Exiting.")
    
    finally:
        # Always stop motors when program ends
        fc.stop()
        print("\nMotors stopped. Goodbye!")