"""
Stage 4.4: Car controller module.
Translates score changes into physical car movements.
"""

import picar_4wd as fc
import time

# Calibration settings (from Stage 4.3)
POWER = 50
SECONDS_PER_POINT = 0.25  # 0.25 seconds = 1/3 foot per point

def move_for_score(home_delta, away_delta):
    """
    Moves the car based on scoring changes.
    
    Args:
        home_delta: Points scored by home team since last check
        away_delta: Points scored by away team since last check
    
    Returns:
        Dictionary describing what movement occurred
    """
    # Calculate net movement
    # Positive = home scored more (move forward)
    # Negative = away scored more (move backward)
    net_points = home_delta - away_delta
    
    if net_points == 0:
        return {'moved': False, 'direction': None, 'points': 0}
    
    # Calculate duration based on points
    duration = abs(net_points) * SECONDS_PER_POINT
    
    if net_points > 0:
        # Home team scored more - move forward
        direction = 'forward'
        fc.forward(POWER)
    else:
        # Away team scored more - move backward
        direction = 'backward'
        fc.backward(POWER)
    
    # Run motors for calculated duration
    time.sleep(duration)
    fc.stop()
    
    return {
        'moved': True,
        'direction': direction,
        'points': abs(net_points),
        'duration': duration
    }

def move_forward_points(points):
    """
    Move forward for a specific number of points.
    Useful for testing.
    """
    duration = points * SECONDS_PER_POINT
    print(f"Moving forward for {points} point(s) ({duration}s)...")
    fc.forward(POWER)
    time.sleep(duration)
    fc.stop()
    print("Done.")

def move_backward_points(points):
    """
    Move backward for a specific number of points.
    Useful for testing.
    """
    duration = points * SECONDS_PER_POINT
    print(f"Moving backward for {points} point(s) ({duration}s)...")
    fc.backward(POWER)
    time.sleep(duration)
    fc.stop()
    print("Done.")

def stop():
    """
    Emergency stop.
    """
    fc.stop()

def test_scoring_scenarios():
    """
    Test the car's response to different scoring scenarios.
    """
    print("=" * 60)
    print("CAR CONTROLLER TEST")
    print("=" * 60)
    print()
    print(f"Calibration: {SECONDS_PER_POINT}s per point = 1/3 foot")
    print()
    
    tests = [
        ("Home makes a free throw (1 pt)", 1, 0),
        ("Away makes a 2-pointer", 0, 2),
        ("Home makes a 3-pointer", 3, 0),
        ("Both score: Home 2, Away 2 (no movement)", 2, 2),
        ("Both score: Home 3, Away 1 (net +2 forward)", 3, 1),
    ]
    
    for description, home, away in tests:
        print(f"\nTest: {description}")
        print(f"  home_delta={home}, away_delta={away}")
        
        input("  Press Enter to execute (or Ctrl+C to skip)...")
        
        result = move_for_score(home, away)
        
        if result['moved']:
            print(f"  Result: Moved {result['direction']} for {result['points']} point(s)")
        else:
            print(f"  Result: No movement (scores cancelled out)")
        
        time.sleep(1)  # Pause between tests
    
    print("\n" + "=" * 60)
    print("All tests complete!")
    print("=" * 60)

# Main execution - run tests if called directly
if __name__ == "__main__":
    try:
        test_scoring_scenarios()
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
    finally:
        fc.stop()
        print("Motors stopped.")