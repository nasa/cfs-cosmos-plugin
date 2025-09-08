"""
Examples showing how to use the CommandSender class for sending commands
and tracking command history in COSMOS tests.

This file demonstrates real-world usage of the CommandSender class.
"""

# Try to import from COSMOS first
try:
    from openc3.script import cmd, tlm
    using_real_cosmos = True
    print("Using real COSMOS functions")
except ImportError:
    using_real_cosmos = False
    print("Using mock COSMOS functions")

from cosmos_test_utils import CommandSender
from cosmos_test_utils import RequirementTracker

def main():
    # Initialize a command sender
    if using_real_cosmos:
        sender = CommandSender()
    else:
        sender = mock_command_sender()
    
    print("EXAMPLE: Basic send_command Usage")
    print("================================")
    
    print("\n1. Simple command")
    sender.send_command("TARGET NOOP")
    
    print("\n2. Command with parameters in string")
    sender.send_command("TARGET SET_PARAMETER with ID 123, VALUE 'hello'")
    
    print("\n3. Command with f-string formatting")
    value1 = 42
    value2 = "test"
    sender.send_command(f"TARGET SET_VALUES with VALUE1 {value1}, VALUE2 '{value2}'")
    
    print("\nVerifying command was stored in history:")
    last_cmd = sender.get_command_history(1)[0]
    print(f"Command sent: {last_cmd['command']}")
    print(f"Time sent: {last_cmd['timestamp']}")
    
    print("\n\nEXAMPLE: send_cmd_multiple_times Usage")
    print("==================================")
    
    print("\n1. Simple command repeated 3 times")
    sender.send_cmd_multiple_times("TARGET NOOP", count=3)
    
    print("\n2. Command with parameters, repeated twice with delay")
    sender.send_cmd_multiple_times(
        "TARGET SET_PARAMETER with ID 123, VALUE 'hello'", 
        count=2, 
        delay=1.5
    )
    
    print("\n3. Checking history after multiple commands")
    history = sender.get_command_history(5)  # Get last 5 commands
    print(f"Number of commands in history: {len(history)}")
    for i, cmd_record in enumerate(history[-2:]):  # Show just the last 2
        print(f"Command {i+1} sent: {cmd_record['command']}")
    
    print("\n\nEXAMPLE: Response Checking")
    print("=========================")
    
    print("\n1. Basic response check")
    success = sender.send_cmd_with_response_check(
        "TARGET SET_MODE with MODE 'SCIENCE'",
        "TARGET", "HK_TLM", "MODE", "==", "SCIENCE",
        tlm_timeout=10.0
    )
    # Get the command details from history
    cmd_info = sender.get_command_history(1)[0]
    print(f"Response check result: {success}")
    if 'response' in cmd_info:
        print(f"Response time: {cmd_info['response']['time']:.2f} seconds")
        print(f"Final value: {cmd_info['response']['value']}")
    
    print("\n2. Response check with custom comparison")
    success = sender.send_cmd_with_response_check(
        "TARGET INCREASE_VALUE with DELTA 5",
        "TARGET", "HK_TLM", "VALUE", ">=", 10
    )
    cmd_info = sender.get_command_history(1)[0]
    print(f"Response check result: {success}")
    if 'response' in cmd_info:
        print(f"Response time: {cmd_info['response']['time']:.2f} seconds")
    
    print("\n\nEXAMPLE: Requirement Verification")
    print("==============================")
    
    # Create a requirement tracker
    req_tracker = RequirementTracker()
    sender.set_req_tracker(req_tracker)
    
    print("\n1. Basic requirement verification")
    success = sender.send_cmd_with_requirement(
        "TARGET SET_MODE with MODE 'SCIENCE'",
        "TARGET", "HK_TLM", "MODE", "==", "SCIENCE",
        "REQ-123"
    )
    cmd_info = sender.get_command_history(1)[0]
    print(f"Requirement verification result: {success}")
    
    print("\n2. Timing requirement verification")
    success = sender.send_cmd_with_timing_requirement(
        "TARGET SET_MODE with MODE 'SAFE'",
        "TARGET", "HK_TLM", "MODE", "==", "SAFE",
        "REQ-456",
        min_time=1.0,
        max_time=5.0
    )
    cmd_info = sender.get_command_history(1)[0]
    print(f"Timing requirement verification result: {success}")
    
    print("\n3. Multiple commands with requirements")
    all_success = sender.send_cmd_multiple_times_with_requirement(
        "TARGET SEND_DATA", 3,
        "TARGET", "HK_TLM", "DATA_COUNT", "==", 1,
        "REQ-789",
        cmd_delay=1.0
    )
    print(f"All requirements passed: {all_success}")
    
    print("\n\nEXAMPLE: Checking Command History")
    print("================================")
    
    print("\nCommand history at different detail levels:")
    
    print("\nBasic history (detail_level=0):")
    sender.print_command_history(detail_level=0, max_entries=2)
    
    print("\nStandard history (detail_level=1):")
    sender.print_command_history(detail_level=1, max_entries=2)
    
    print("\nVerbose history (detail_level=2):")
    sender.print_command_history(detail_level=2, max_entries=1)
    
    print("\nManually accessing history:")
    history = sender.get_command_history(3)  # Last 3 commands
    for i, entry in enumerate(history):
        print(f"\nCommand {i+1}:")
        print(f"  Sent command: {entry['command']}")
        if 'response' in entry:
            print(f"  Success: {entry['response'].get('success', 'N/A')}")
        if 'requirement' in entry:
            print(f"  Requirement: {entry['requirement']['id']}")
    
    print("\n\nExample complete!")

# Helper function to create a CommandSender with mock functions for example purposes
def mock_command_sender():
    """Create a CommandSender with mock functions for demonstration."""
    from cosmos_test_utils import CommandSender
    
    # Mock cmd function that simulates sending a command
    def mock_cmd(command_string, **kwargs):
        print(f"MOCK: Sending command '{command_string}'")
        return None  # cmd() returns None in COSMOS
    
    # Mock tlm function that simulates getting telemetry
    def mock_tlm(telemetry_string):
        print(f"MOCK: Getting telemetry for '{telemetry_string}'")
        
        # For demonstration, we'll parse the string and return appropriate values
        if "MODE" in telemetry_string:
            # For our examples, always return the expected mode
            return "SCIENCE" if "SCIENCE" in telemetry_string else "SAFE"
        elif "VALUE" in telemetry_string:
            return 15  # Simulated value above threshold
        elif "THRESHOLD" in telemetry_string:
            return 75  # Match the threshold we set
        elif "DATA_COUNT" in telemetry_string:
            return 1  # Simulating successful data count
        else:
            return "MOCK_VALUE"
    
    # Create a sender and replace its functions with our mocks
    sender = CommandSender()
    sender.cmd = mock_cmd
    sender.tlm = mock_tlm
    
    return sender

if __name__ == "__main__":
    main()