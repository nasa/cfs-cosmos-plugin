"""Enhanced printing utilities for test reports."""

from typing import Optional
from .event_utils import print_events_to_log


def test_print(
    text_to_print: str,
    event_log_id: Optional[int] = None,
    use_group_print_for_events: bool = False  # Default to regular print for events
) -> None:
    
    """Print text to the test log, after logging any events.
    
    This function:
    1. Prints all received event messages since last call
    2. Then prints the provided text using print or Group.print if use_group_print_for_events == True
    
    Args:
        text_to_print: Text to print to the test log
        event_log_id: Optional event subscription ID 
                     (if None, uses module-level ID from open_event_log_for_script_logging)
        use_group_print_for_events: If True, use Group.print for events and text_to_print;
                                    If False, use built-in print(default: False - uses regular print)
                     
    Examples:
        # Basic usage
        open_event_log_for_script_logging()
        test_print("Command sent")
        
        # With specific event log ID
        log_id = open_event_log_for_script_logging()
        test_print("Message with specific log", event_log_id=log_id)
        
        # Using Group.print for events as well
        test_print("Message", use_group_print_for_events=True)
    """
    
    try:
        # Print events - using the log ID and print type preference
        print_events_to_log(event_log_id, use_group_print=use_group_print_for_events)
    except RuntimeError as e:
        # Add context to the original error message
        enhanced_message = (
            f"test_print() failed: {str(e)}\n\n"
            f"Note: This error occurred because test_print() automatically tries to print "
            f"events before printing your message. If you don't need event logging, "
            f"you can use regular Group.print() or print() instead of test_print()."
        )
        raise RuntimeError(enhanced_message) from e
    
    # Determine print function
    if use_group_print_for_events:
        from openc3.script.suite import Group
        Group.print(text_to_print)
    else:
        print(text_to_print)


def print_command_history(
    command_sender,
    detail_level: int = 1
) -> None:
    """Print a command history in a formatted, readable way.
    
    This function delegates to the CommandSender's print_command_history method.
    It provides a functional interface to the command history printing capability.
    
    All commands are printed with responses and requirements included.
    
    Args:
        command_sender: A CommandSender instance with command history
        detail_level: Level of detail to print
                     0 = Basic (command strings only)
                     1 = Standard (commands, timestamps, basic results)
                     2 = Detailed (all information including responses)
        
    Examples:
        # Create and use a command sender
        sender = CommandSender()
        sender.send_command("TARGET COMMAND")
        
        # Print its history using the functional interface
        from cosmos_test_utils import print_command_history
        print_command_history(sender)
        
        # Print detailed history
        print_command_history(sender, detail_level=2)
    """
    # Delegate to the CommandSender's method with fixed parameters
    command_sender.print_command_history(
        detail_level=detail_level,
        include_responses=True,        # Always include responses with this call
        include_requirements=True,     # Always include requirements with this call
        max_entries=None,              # Always print all commands with this call
        print_func=test_print          # Use test_print from this module with this call
    )