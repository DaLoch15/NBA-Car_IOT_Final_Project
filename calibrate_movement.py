import picar_4wd as fc
import time

# Configuration - ADJUST THESE VALUES
POWER = 50              # Motor power (0-100). Keep consistent for predictable results.
TEST_DURATION = 0.5     # Starting guess: seconds to run motors

def move_forward(duration, power=POWER):
    """
    Move the car forward for a specified duration.
    """
    print(f"Moving FORWARD at power {power} for {duration} seconds...")
    fc.forward(power)
    time.sleep(duration)
    fc.stop()
    print("Stopped.")

def move_backward(duration, power=POWER):
    """
    Move the car backward for a specified duration.
    """
    print(f"Moving BACKWARD at power {power} for {duration} seconds...")
    fc.backward(power)
    time.sleep(duration)
    fc.stop()
    print("Stopped.")

def run_calibration_test():
    """
    Interactive calibration mode.
    """
    print("=" * 60)
    print("PICAR MOVEMENT CALIBRATION")
    print("=" * 60)
    print()
    print("Commands:")
    print("  f <seconds>  - Move forward (e.g., 'f 0.5')")
    print("  b <seconds>  - Move backward (e.g., 'b 0.5')")
    print("  t            - Test current duration forward then backward")
    print("  s            - Stop motors (emergency)")
    print("  q            - Quit")
    print()
    print(f"Default duration: {TEST_DURATION} seconds")
    print(f"Motor power: {POWER}")
    print()
    print("TIP: Mark the car's starting position with tape,")
    print("     then measure how far it travels.")
    print()
    print("-" * 60)
    
    current_duration = TEST_DURATION
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'q':
                print("Exiting calibration.")
                break
            
            elif command == 's':
                fc.stop()
                print("Motors stopped.")
            
            elif command == 't':
                # Test forward and backward with current duration
                print(f"\nTesting with duration = {current_duration}s")
                print("Moving forward...")
                move_forward(current_duration)
                time.sleep(1)  # Pause between movements
                print("Moving backward (returning to start)...")
                move_backward(current_duration)
                print("Test complete. Did the car return to its starting position?")
            
            elif command.startswith('f'):
                # Parse duration from command like "f 0.5"
                parts = command.split()
                if len(parts) == 2:
                    try:
                        duration = float(parts[1])
                        current_duration = duration
                        move_forward(duration)
                        print(f"\nMeasure the distance traveled!")
                        print(f"If it was ~0.5 feet, this duration ({duration}s) is good for 1 point.")
                        print(f"If too short, try a larger number. If too far, try smaller.")
                    except ValueError:
                        print("Invalid duration. Use format: f 0.5")
                else:
                    # No duration specified, use current
                    move_forward(current_duration)
            
            elif command.startswith('b'):
                # Parse duration from command like "b 0.5"
                parts = command.split()
                if len(parts) == 2:
                    try:
                        duration = float(parts[1])
                        current_duration = duration
                        move_backward(duration)
                    except ValueError:
                        print("Invalid duration. Use format: b 0.5")
                else:
                    move_backward(current_duration)
            
            else:
                print("Unknown command. Use f, b, t, s, or q.")
                
        except KeyboardInterrupt:
            fc.stop()
            print("\n\nEmergency stop! Motors stopped.")
            break
        except Exception as e:
            fc.stop()
            print(f"\nError: {e}")
            print("Motors stopped for safety.")

def quick_test():
    """
    A simple one-shot test: move forward, pause, move backward.
    Useful for verifying the car works at all.
    """
    print("Quick test: Forward 0.5s, pause, backward 0.5s")
    print("Starting in 2 seconds...")
    time.sleep(2)
    
    move_forward(0.5)
    time.sleep(1)
    move_backward(0.5)
    
    print("\nQuick test complete!")

# Main execution
if __name__ == "__main__":
    print()
    print("What would you like to do?")
    print("  1. Quick test (forward then backward)")
    print("  2. Interactive calibration mode")
    print()
    
    choice = input("Enter 1 or 2: ").strip()
    
    if choice == '1':
        quick_test()
    elif choice == '2':
        run_calibration_test()
    else:
        print("Invalid choice. Running quick test by default.")
        quick_test()
    
    # Always ensure motors are stopped when script ends
    fc.stop()
    print("\nMotors stopped. Script ended.")