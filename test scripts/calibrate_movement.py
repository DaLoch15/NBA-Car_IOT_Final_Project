import picar_4wd as fc
import time

POWER = 50
TEST_DURATION = 0.5

# moves the car forward for a given duration
def move_forward(duration, power=POWER):
    fc.forward(power)
    time.sleep(duration)
    fc.stop()

# moves the car backward for a given duration
def move_backward(duration, power=POWER):
    fc.backward(power)
    time.sleep(duration)
    fc.stop()

# interactive calibration mode for testing car movement
def run_calibration_test():
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
                print(f"\nTesting with duration = {current_duration}s")
                move_forward(current_duration)
                time.sleep(1)
                move_backward(current_duration)
                print("Test complete.")
            
            elif command.startswith('f'):
                parts = command.split()
                if len(parts) == 2:
                    try:
                        duration = float(parts[1])
                        current_duration = duration
                        move_forward(duration)
                    except ValueError:
                        print("Invalid duration. Use format: f 0.5")
                else:
                    move_forward(current_duration)
            
            elif command.startswith('b'):
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

# quick test that moves forward then backward
def quick_test():
    print("Quick test: Forward 0.5s, pause, backward 0.5s")
    print("Starting in 2 seconds...")
    time.sleep(2)
    
    move_forward(0.5)
    time.sleep(1)
    move_backward(0.5)
    
    print("\nQuick test complete!")

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
    
    fc.stop()
    print("\nMotors stopped. Script ended.")