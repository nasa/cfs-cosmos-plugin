# examples/timing_examples.py
"""
Examples showing how to use the timing utilities for measuring and verifying
timing requirements in COSMOS tests.
"""

from cosmos_test_utils import (
    TimingTracker,
    measure_command_response_time
)

def main():
    print("EXAMPLE: Timing Utilities")
    print("=======================")
    
    print("\n1. Basic timing tracking")
    timer = TimingTracker()
    
    # Start timing an event
    print("Starting timer for 'startup'...")
    timer.start("startup")
    
    # Simulate some work
    print("Performing startup operations...")
    import time
    time.sleep(1.0)  # Simulate 1 second of work
    
    # Stop timing and print result
    elapsed = timer.stop("startup")
    print(f"Startup completed in {elapsed:.3f} seconds")
    
    print("\n2. Multiple timing events")
    print("Starting multiple timers...")
    timer.start("operation1")
    time.sleep(0.5)
    
    timer.start("operation2")
    time.sleep(0.7)
    
    # Stop timers
    timer.stop("operation2")
    timer.stop("operation1")
    
    # Print timing report
    timer.report()
    
    print("\n3. Verify timing against requirements")
    print("Starting operation with timing requirements...")
    timer.start("critical_operation")
    time.sleep(1.2)
    elapsed = timer.stop("critical_operation")
    
    # Verify timing against requirements
    success, elapsed, message = timer.verify_timing("critical_operation", min_time=1.0, max_time=2.0)
    print(message)
    
    print("\n4. Command response timing")
    print("Measuring command response time...")
    
    def send_command():
        print("  Sending command...")
        time.sleep(0.1)  # Simulate command transmission
    
    def check_response():
        print("  Checking for response...")
        time.sleep(0.8)  # Simulate response delay
        return True
    
    success, response_time = measure_command_response_time(
        send_command, 
        check_response,
        timeout=5.0
    )
    
    print(f"Command response received: {'Yes' if success else 'No'}")
    print(f"Response time: {response_time:.3f} seconds")
    
    print("\n5. Telemetry timing with requirement verification")
    print("Waiting for telemetry with requirement...")
    

if __name__ == "__main__":
    main()