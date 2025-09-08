# examples/event_examples.py
"""
Examples showing how to use the event utilities for finding and printing
event messages in COSMOS tests.

Note: This example uses mock functions since it can't connect to a real COSMOS system.
"""

from cosmos_test_utils import (
    open_event_log_for_search, 
    open_event_log_for_script_logging,
    find_events,
    print_events_to_log,
    test_print,
    start_background_event_logging,       # Add these new imports
    stop_background_event_logging,
    is_background_event_logging_running
)

def main():
    print("EXAMPLE: Working with Events")
    print("==========================")
    
    # Set up mock functions since we can't connect to COSMOS
    setup_mock_functions()
    
    print("\n1. Basic event searching")
    # Normally you would just call this directly
    open_event_log_for_search()
    
    # Now search for events (this is using mock data)
    print("Searching for INFO event with ID 2...")
    success, count = find_events("CFE_APP", 2, "INFO", "Command executed") # type: ignore
    print(f"Found: {count} events, Expected match: {success}")
    
    print("\n2. Multiple searches in sequence")
    # Reset the search point to look for different events
    open_event_log_for_search()
    
    print("Searching for ERROR event with ID 5...")
    success, count = find_events("CFE_APP", 5, "ERROR", "Command failed") # type: ignore
    print(f"Found: {count} events, Expected match: {success}")
    
    print("\n3. Script logging setup")
    # Set up event logging for the script
    open_event_log_for_script_logging()
    
    print("\n4. Manual event printing")
    # This will print any events since the last call
    print("Printing events (if any):")
    print_events_to_log()
    
    print("\n5. Using test_print for automatic event logging")
    # This will print events first, then the message
    test_print("This message appears after any events")
    
    print("\n6. Background event logging")  # Add this new section
    demonstrate_background_logging()
    
    print("\nExample complete!")

def demonstrate_background_logging():
    """Show how to use background event logging"""
    import time
    
    print("Starting background event logging to console...")
    start_background_event_logging()
    
    print(f"Is logging active? {is_background_event_logging_running()}")
    
    # Simulate some test operations
    print("Simulating test operations for 2 seconds...")
    print("(In a real test, this is where you'd send commands)")
    time.sleep(2)
    
    print("Stopping background event logging...")
    stop_background_event_logging()
    
    print(f"Is logging still active? {is_background_event_logging_running()}")
    
    # Example with file logging
    print("\nStarting background event logging to file...")
    start_background_event_logging("example_test_events.log")
    print("Simulating more test operations...")
    time.sleep(1)
    print("Stopping file-based background logging...")
    stop_background_event_logging()
    
    # Show that starting a new one stops the old one automatically
    print("\nDemonstrating automatic cleanup...")
    start_background_event_logging("first_log.log")
    print("First logger started")
    
    start_background_event_logging("second_log.log")  # This will stop the first one
    print("Second logger started (first one automatically stopped)")
    
    stop_background_event_logging()
    print("All background logging stopped")

def setup_mock_functions():
    """Set up mock functions for this example."""
    import sys
    from unittest.mock import MagicMock
    
    # Capture the real functions before mocking
    real_open_search = open_event_log_for_search
    real_open_logging = open_event_log_for_script_logging
    real_find_events = find_events
    real_print_events = print_events_to_log
    
    # Create mock functions
    mock_subscribe = MagicMock(return_value=123)
    mock_get_packets = MagicMock(side_effect=lambda id, **kwargs: (
        id, 
        [
            {"APP": "CFE_APP", "EID": 2, "EVENTTYPE": 2, "EVMSG": "Command executed successfully", 
             "SCID": 42, "PROCID": 1, "PACKET_TIMEFORMATTED": "2023-01-01 12:00:00.000"},
            {"APP": "CFE_APP", "EID": 5, "EVENTTYPE": 3, "EVMSG": "Command failed validation", 
             "SCID": 42, "PROCID": 1, "PACKET_TIMEFORMATTED": "2023-01-01 12:00:01.000"}
        ]
    ))
    
    # Mock the background logging functions for demonstration
    mock_script_run = MagicMock(return_value=456)
    mock_running_script_stop = MagicMock()
    mock_stash_set = MagicMock()
    mock_stash_get = MagicMock(side_effect=lambda key: 456 if key == 'background_event_log_id' else None)
    
    # Create patched versions that use these mocks
    def patched_open_search(*args, **kwargs):
        kwargs['subscribe_packets_func'] = mock_subscribe
        return real_open_search(*args, **kwargs)
    
    def patched_open_logging(*args, **kwargs):
        kwargs['subscribe_packets_func'] = mock_subscribe
        return real_open_logging(*args, **kwargs)
    
    def patched_find_events(*args, **kwargs):
        kwargs['get_packets_func'] = mock_get_packets
        return real_find_events(*args, **kwargs)
    
    def patched_print_events(*args, **kwargs):
        kwargs['get_packets_func'] = mock_get_packets
        return real_print_events(*args, **kwargs)
    
    # Apply the patches
    import cosmos_test_utils.event_utils as eu
    eu.open_event_log_for_search = patched_open_search
    eu.open_event_log_for_script_logging = patched_open_logging
    eu.find_events = patched_find_events
    eu.print_events_to_log = patched_print_events
    
    # Mock the background logging functions to avoid actual script execution
    def mock_start_background(*args, **kwargs):
        filename = args[0] if args else "console"
        print(f"[MOCK] Background event logging started to: {filename}")
        
    def mock_stop_background():
        print("[MOCK] Background event logging stopped")
        
    def mock_is_running():
        return True  # For demonstration purposes
    
    # Replace the background logging functions with mocks
    import cosmos_test_utils as ctu
    ctu.start_background_event_logging = mock_start_background
    ctu.stop_background_event_logging = mock_stop_background
    ctu.is_background_event_logging_running = mock_is_running

if __name__ == "__main__":
    main()