from nba_api.live.nba.endpoints import scoreboard
import picar_4wd as fc
import time
from datetime import datetime

POLL_INTERVAL_SECONDS = 15
POWER = 50
SECONDS_PER_POINT = 0.25

# fetches all games from the nba api
def fetch_all_games():
    board = scoreboard.ScoreBoard()
    data = board.get_dict()
    return data['scoreboard']['games']

# finds a specific game by its id from the games list
def find_game_by_id(games, game_id):
    for game in games:
        if game['gameId'] == game_id:
            return game
    return None

# extracts game information into a dictionary
def get_game_info(game):
    return {
        'home_team': game['homeTeam']['teamName'],
        'away_team': game['awayTeam']['teamName'],
        'home_score': game['homeTeam']['score'],
        'away_score': game['awayTeam']['score'],
        'status': game['gameStatusText'],
        'game_id': game['gameId']
    }

# moves the car in a given direction for a number of points
def move_car(direction, points):
    duration = points * SECONDS_PER_POINT
    
    if direction == 'forward':
        fc.forward(POWER)
    else:
        fc.backward(POWER)
    
    time.sleep(duration)
    fc.stop()

# processes score changes and moves the car accordingly
def handle_score_change(home_delta, away_delta, home_team, away_team):
    net_points = home_delta - away_delta
    
    if net_points == 0:
        if home_delta > 0:
            return f"Both teams scored {home_delta} - no net movement"
        return None
    
    if net_points > 0:
        move_car('forward', abs(net_points))
        return f"FORWARD {abs(net_points)} point(s) - {home_team} scoring!"
    else:
        move_car('backward', abs(net_points))
        return f"BACKWARD {abs(net_points)} point(s) - {away_team} scoring!"

# displays available games and lets user select one to track
def display_games_and_select():
    print("\nFetching today's games...\n")
    
    try:
        games = fetch_all_games()
    except Exception as e:
        print(f"Error fetching games: {e}")
        return None
    
    if not games:
        print("No games available today.")
        return None
    
    live_games = [g for g in games if get_game_info(g)['status'] != 'Final']
    final_games = [g for g in games if get_game_info(g)['status'] == 'Final']
    
    print("=" * 60)
    print("AVAILABLE GAMES")
    print("=" * 60)
    
    all_games = live_games + final_games
    
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
    
    while True:
        try:
            choice = input("\nEnter game number to track (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(all_games):
                selected = all_games[index]
                info = get_game_info(selected)
                
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

# main tracking loop that polls the game and moves the car on score changes
def run_tracker(game_id):
    print("\n" + "=" * 60)
    print("STARTING NBA CAR TRACKER")
    print("=" * 60)
    print(f"\nGame ID: {game_id}")
    print(f"Poll interval: {POLL_INTERVAL_SECONDS} seconds")
    print("\nPress Ctrl+C to stop safely")
    print("\n" + "-" * 60)
    
    previous_home_score = None
    previous_away_score = None
    home_team = None
    away_team = None
    
    total_forward = 0
    total_backward = 0
    
    while True:
        try:
            games = fetch_all_games()
            game = find_game_by_id(games, game_id)
            
            if game is None:
                print("\nGame not found! It may have been removed from the API.")
                break
            
            info = get_game_info(game)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if home_team is None:
                home_team = info['home_team']
                away_team = info['away_team']
                print(f"\nTracking: {away_team} @ {home_team}")
                print("-" * 60)
            
            if previous_home_score is None:
                previous_home_score = info['home_score']
                previous_away_score = info['away_score']
                print(f"[{timestamp}] Initial score: {away_team} {info['away_score']} - {home_team} {info['home_score']}")
                print(f"[{timestamp}] Status: {info['status']}")
                print("-" * 60)
            else:
                home_delta = info['home_score'] - previous_home_score
                away_delta = info['away_score'] - previous_away_score
                
                if home_delta > 0 or away_delta > 0:
                    print(f"\n[{timestamp}] SCORING DETECTED!")
                    
                    if home_delta > 0:
                        print(f"    {home_team} (HOME) +{home_delta}")
                    if away_delta > 0:
                        print(f"    {away_team} (AWAY) +{away_delta}")
                    
                    result = handle_score_change(home_delta, away_delta, home_team, away_team)
                    
                    if result:
                        print(f"    CAR: {result}")
                        
                        net = home_delta - away_delta
                        if net > 0:
                            total_forward += net
                        else:
                            total_backward += abs(net)
                    
                    print(f"    New score: {away_team} {info['away_score']} - {home_team} {info['home_score']}")
                    print(f"    Car position: +{total_forward} / -{total_backward} points from start")
                    print("-" * 60)
                else:
                    print(f"[{timestamp}] {away_team} {info['away_score']} - {home_team} {info['home_score']} | {info['status']}")
                
                previous_home_score = info['home_score']
                previous_away_score = info['away_score']
            
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
        game_id = display_games_and_select()
        
        if game_id:
            run_tracker(game_id)
        else:
            print("\nNo game selected. Exiting.")
    
    finally:
        fc.stop()
        print("\nMotors stopped. Goodbye!")