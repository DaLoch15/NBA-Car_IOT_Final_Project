import picar_4wd as fc
import time

POWER = 50
SECONDS_PER_POINT = 0.25

# moves the car based on score changes between home and away teams
def move_for_score(home_delta, away_delta):
    net_points = home_delta - away_delta
    
    if net_points == 0:
        return {'moved': False, 'direction': None, 'points': 0}
    
    duration = abs(net_points) * SECONDS_PER_POINT
    
    if net_points > 0:
        direction = 'forward'
        fc.forward(POWER)
    else:
        direction = 'backward'
        fc.backward(POWER)
    
    time.sleep(duration)
    fc.stop()
    
    return {
        'moved': True,
        'direction': direction,
        'points': abs(net_points),
        'duration': duration
    }

# moves the car forward for a given number of points
def move_forward_points(points):
    duration = points * SECONDS_PER_POINT
    fc.forward(POWER)
    time.sleep(duration)
    fc.stop()

# moves the car backward for a given number of points
def move_backward_points(points):
    duration = points * SECONDS_PER_POINT
    fc.backward(POWER)
    time.sleep(duration)
    fc.stop()

# stops the car motors
def stop():
    fc.stop()

# runs test scenarios to verify car movement logic
def test_scoring_scenarios():
    print("=" * 60)
    print("CAR CONTROLLER TEST")
    print("=" * 60)
    
    tests = [
        ("Home makes a free throw (1 pt)", 1, 0),
        ("Away makes a 2-pointer", 0, 2),
        ("Home makes a 3-pointer", 3, 0),
        ("Both score: Home 2, Away 2 (no movement)", 2, 2),
        ("Both score: Home 3, Away 1 (net +2 forward)", 3, 1),
    ]
    
    for description, home, away in tests:
        print(f"\nTest: {description}")
        input("  Press Enter to execute (or Ctrl+C to skip)...")
        
        result = move_for_score(home, away)
        
        if result['moved']:
            print(f"  Result: Moved {result['direction']} for {result['points']} point(s)")
        else:
            print(f"  Result: No movement (scores cancelled out)")
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("All tests complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_scoring_scenarios()
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
    finally:
        fc.stop()
        print("Motors stopped.")