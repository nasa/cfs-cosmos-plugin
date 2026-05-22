# NASA Docket No. GSC-19606-1, and identified as Test Utilities Python
# package to facilitate testing software with the open source COSMOS
# ground system”
#
# Copyright (c) 2025 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for waiting for specific telemetry conditions in COSMOS tests."""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from .system_config import DEFAULT_WAIT_TIMEOUT, DEFAULT_POLL_INTERVAL, COMMON_PACKET_SEQUENCE_COUNT_FIELD

COMPARISON_OPERATORS = {
    "==": lambda x, y: x == y,
    "!=": lambda x, y: x != y,
    "<": lambda x, y: x < y,
    "<=": lambda x, y: x <= y,
    ">": lambda x, y: x > y,
    ">=": lambda x, y: x >= y,
    "contains": lambda x, y: y in x if hasattr(x, '__contains__') else False,
    "does_not_contain": lambda x, y: y not in x if hasattr(x, '__contains__') else True
}

def wait_for_telemetry_value(
    target: str,
    packet: str,
    item: str,
    comparison: str,
    comparison_value: Any,
    timeout: float = DEFAULT_WAIT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    return_timing: bool = False,
    requirement_ids: Optional[Union[str, List[str]]] = None,
    req_tracker: Optional[Any] = None,
    print_func: Optional[Callable] = None
) -> Union[bool, Tuple[bool, float]]:
    """
    Wait for a telemetry item to meet a given comparison criteria
    
    Args:
        target: The COSMOS target name
        packet: The COSMOS telemetry packet name
        item: The specific COSMOS telemetry item name
        comparison: Comparison operator to use ("==", "!=", "<", "<=", ">", ">=", "contains", "does_not_contain")
        comparison_value: The value to compare against
        timeout: Maximum wait time in seconds (default from system_config)
        poll_interval: Time between checks in seconds (default from system_config)
        print_func: Function to use for printing status/debug info (default: test_print)
        return_timing: If True, return (success, elapsed_time) tuple instead of just success
        requirement_ids: Optional comma-separated string or list of requirement IDs to update based on the result
        req_tracker: RequirementTracker instance to use (required if requirement_ids provided)
        
    Returns:
        bool or Tuple[bool, float]: 
            - If return_timing=False: True if item met the comparison before timeout, False if timeout occurred
            - If return_timing=True: (success, elapsed_time) where elapsed_time is in seconds
        
    Examples:
        # Basic usage
        success = wait_for_telemetry_value("SPACECRAFT", "HEALTH_TLM", "BATTERY", "==", 100)
        
        # With timing information
        success, elapsed_time = wait_for_telemetry_value(
            "SPACECRAFT", "HEALTH_TLM", "BATTERY", "==", 100, 
            return_timing=True
        )
        
        # With requirement tracking
        tracker = RequirementTracker()
        success = wait_for_telemetry_value(
            "SPACECRAFT", "HEALTH_TLM", "BATTERY", "==", 100,
            requirement_ids="REQ-123", req_tracker=tracker
        )
        
        # With both timing and requirement tracking
        success, elapsed_time = wait_for_telemetry_value(
            "SPACECRAFT", "HEALTH_TLM", "BATTERY", "==", 100,
            return_timing=True, requirement_ids="REQ-456, REQ-457", req_tracker=tracker
        )
    """
    # Use test_print as the default print function if none provided
    if print_func is None:
        from .print_utils import test_print
        print_func = test_print
    
    # Use the COSMOS tlm function
    from openc3.script import tlm
    
    # Validate the comparison operator
    if comparison not in COMPARISON_OPERATORS:
        valid_ops = ", ".join(COMPARISON_OPERATORS.keys())
        raise ValueError(f"Invalid comparison operator '{comparison}'. Must be one of: {valid_ops}")
    
    # Function to perform the comparison
    compare = COMPARISON_OPERATORS[comparison]
    
    # Track start time using high precision timer
    start_time = time.perf_counter()
    end_time = start_time + timeout
    
    # Initialize current_value for timeout reporting
    current_value = None
    
    # Main waiting loop
    while time.perf_counter() < end_time:
        # Get current value
        try:
            current_value = tlm(f"{target} {packet} {item}")
            
            # Only check condition if we received telemetry
            if current_value is not None:
                # Check for the expected condition
                if compare(current_value, comparison_value):
                    # Condition met - calculate response time
                    response_time = time.perf_counter() - start_time
                    
                    # Update requirement if tracking
                    if requirement_ids is not None and req_tracker is not None:
                        req_message = f"Telemetry condition met: {target} {packet} {item} {comparison} {comparison_value} in {response_time:.6f}s"
                        req_tracker.set_multiple_requirements(requirement_ids, "P", req_message)
                    elif requirement_ids is not None:
                        print_func("Warning: requirement_ids provided but no req_tracker. Cannot update requirement status.")
                    
                    # Return based on return_timing flag
                    if return_timing:
                        return True, response_time
                    else:
                        return True
                
        except Exception as e:
            # Handle errors that might occur when getting telemetry
            print_func(f"Error getting telemetry {target} {packet} {item}: {str(e)}")
            
        # Wait before checking again
        time.sleep(poll_interval)
    
    # If we get here, we timed out
    timeout_message = (
        f"Timeout waiting for {target} {packet} {item} {comparison} {comparison_value}. "
        f"Current value is {current_value}."
    )
    
    # Print timeout message
    print_func(timeout_message)
    
    # Update requirement if tracking (failure case)
    if requirement_ids is not None and req_tracker is not None:
        req_tracker.set_multiple_requirements(requirement_ids, "F", timeout_message)
    elif requirement_ids is not None:
        print_func("Warning: requirement_ids provided but no req_tracker. Cannot update requirement status.")
    
    # Return based on return_timing flag (timeout case)
    if return_timing:
        return False, timeout
    else:
        return False


def wait_for_telemetry_expression(
    expression: str,
    timeout: float = DEFAULT_WAIT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    print_func: Optional[Callable] = None
) -> bool:
    """
    Wait for a telemetry expression to evaluate to True.
    
    This is a wrapper around the COSMOS wait() function that adds better error handling
    and feedback.
    
    Args:
        expression: String expression to evaluate (e.g., "TARGET PACKET ITEM == 10")
        timeout: Maximum wait time in seconds (default from system_config)
        poll_interval: Time between checks in seconds (default from system_config)  
        print_func: Function to use for printing status/debug info (default: test_print)
        
    Returns:
        bool: True if expression evaluated to True, False if timeout occurred
        
    Example:
        wait_for_telemetry_expression("TARGET HK_TLM_PK BATTERY == 100")
    """
    
    # Use test_print as the default print function if none provided
    if print_func is None:
        from .print_utils import test_print
        print_func = test_print
    
    # Use the COSMOS wait function directly
    from openc3.script import wait
    
    try:
        # Call the COSMOS wait function
        # Setting the polling interval and the overall timeout
        result = wait(expression, timeout, poll_interval)
        return result
    except Exception as e:
        print_func(f"Error waiting for expression '{expression}': {str(e)}")
        return False


def wait_for_telemetry_change(
    target: str,
    packet: str,
    item: str,
    timeout: float = DEFAULT_WAIT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    print_func: Optional[Callable] = None
) -> bool:
    """
    Wait for a telemetry value to change from its initial value.
    
    Args:
        target: The COSMOS target name
        packet: The COSMOS telemetry packet name
        item: The specific COSMOS telemetry item name
        timeout: Maximum wait time in seconds (default from system_config)
        poll_interval: Time between checks in seconds (default from system_config)
        print_func: Function to use for printing status/debug info (default: test_print)
        
    Returns:
        bool: True if the value changed, False if timeout occurred
        
    Example:
        wait_for_telemetry_change("TARGET", "HK_TLM_PK", "SEQUENCE_COUNT")
    """
    
    # Use test_print as the default print function if none provided
    if print_func is None:
        from .print_utils import test_print
        print_func = test_print

    # Use the COSMOS tlm function directly
    from openc3.script import tlm
    
    # Get the initial value
    try:
        initial_value = tlm(f"{target} {packet} {item}")
    except Exception as e:
        print_func(f"Error getting initial telemetry value for {target} {packet} {item}: {str(e)}")
        return False
    
    # Track start time
    start_time = time.perf_counter()
    end_time = start_time + timeout
    
    # Initialize current_value for timeout reporting
    current_value = None
    
    # Main waiting loop
    while time.perf_counter() < end_time:
        # Get current value
        try:
            current_value = tlm(f"{target} {packet} {item}")
            
            # Only check for change if we received telemetry
            if current_value is not None:
                # Check if the value has changed
                if current_value != initial_value:
                    print_func(f"{target} {packet} {item} changed from {initial_value} to {current_value}")
                    return True
                
        except Exception as e:
            # Handle errors that might occur when getting telemetry
            print_func(f"Error getting telemetry {target} {packet} {item}: {str(e)}")
            
        # Wait before checking again
        time.sleep(poll_interval)
    
    # If we get here, we timed out
    print_func(
        f"Timeout waiting for {target} {packet} {item} to change from {initial_value}. "
        f"Value did not change within {timeout} seconds."
    )
    return False


def wait_for_sequence_count_change(
    target: str,
    packet: str,
    count: int = 1,
    timeout: float = DEFAULT_WAIT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    sequence_item: str = COMMON_PACKET_SEQUENCE_COUNT_FIELD,
    print_func: Optional[Callable] = None
) -> bool:
    """
    Wait for a packet's sequence counter to increment by the specified amount.
    
    Args:
        target: The COSMOS target name
        packet: The COSMOS telemetry packet name
        count: Number of sequence count increases to wait for
        timeout: Maximum wait time in seconds (default from system_config)
        poll_interval: Time between checks in seconds (default from system_config)
        sequence_item: Name of the sequence counter item (default: from system_config.COMMON_PACKET_SEQUENCE_COUNT_FIELD)
        print_func: Function to use for printing status/debug info (default: test_print)
        
    Returns:
        bool: True if the sequence count changed by the specified amount, False if timeout occurred
        
    Example:
        wait_for_sequence_count_change("TARGET", "HK_TLM_PK")  # Wait for 1 new packet
        wait_for_sequence_count_change("TARGET", "HK_TLM_PK", 5)  # Wait for 5 new packets
    """
    
    # Use test_print as the default print function if none provided
    if print_func is None:
        from .print_utils import test_print
        print_func = test_print
    
    # Use the COSMOS tlm function directly
    from openc3.script import tlm
    
    # Get the initial sequence count
    try:
        initial_count = tlm(f"{target} {packet} {sequence_item}")
    except Exception as e:
        print_func(f"Error getting initial sequence count for {target} {packet}: {str(e)}")
        return False
    
    # Calculate the target sequence count
    # If initial_count is None, any packet (count >= 0) is a change
    if initial_count is None:
        target_count = 0
    else:
        target_count = (initial_count + count) % 65536
    
    # Track start time
    start_time = time.perf_counter()
    end_time = start_time + timeout
    
    # Initialize current_count for timeout reporting
    current_count = None
    
    # Main waiting loop
    while time.perf_counter() < end_time:
        # Get current sequence count
        try:
            current_count = tlm(f"{target} {packet} {sequence_item}")
            
            # Only check conditions if we received telemetry
            if current_count is not None:
                # If initial was None, any non-None value is success
                if initial_count is None:
                    print_func(f"{target} {packet} sequence count increased from None to {current_count}")
                    return True
                
                # Check if we've reached or passed the target count
                # Need to handle sequence counter rollover
                if initial_count <= target_count:
                    # No rollover case
                    if current_count >= target_count:
                        print_func(f"{target} {packet} sequence count increased from {initial_count} to {current_count}")
                        return True
                else:
                    # Rollover case
                    if current_count >= target_count and current_count < initial_count:
                        print_func(f"{target} {packet} sequence count increased from {initial_count} to {current_count} (with rollover)")
                        return True
                
        except Exception as e:
            # Handle errors that might occur when getting telemetry
            print_func(f"Error getting sequence count for {target} {packet}: {str(e)}")
            
        # Wait before checking again
        time.sleep(poll_interval)
    
    # If we get here, we timed out
    if current_count is None:
        print_func(
            f"Timeout waiting for {target} {packet} sequence count to reach >= {target_count}. "
            f"Current count is None, initial was {initial_count}."
        )
    else:
        print_func(
            f"Timeout waiting for {target} {packet} sequence count to reach >= {target_count}. "
            f"Current count is {current_count}, initial was {initial_count}."
        )
        
    return False


def wait_check_telemetry(
    target: str,
    packet: str,
    item: str,
    comparison: str,
    comparison_value: Any,
    timeout: float = DEFAULT_WAIT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    print_func: Optional[Callable] = None
) -> Tuple[bool, Any]:
    """
    Wait for a telemetry value to meet a given comparison criteria
    
    This is similar to wait_for_telemetry_value but also returns the final value.
    
    Args:
        target: The COSMOS target name
        packet: The COSMOS telemetry packet name
        item: The specific COSMOS telemetry item name
        comparison: Comparison operator to use ("==", "!=", "<", "<=", ">", ">=")
        comparison_value: The value to compare against
        timeout: Maximum wait time in seconds (default from system_config)
        poll_interval: Time between checks in seconds (default from system_config)
        print_func: Function to use for printing status/debug info (default: test_print)
        
    Returns:
        Tuple[bool, Any]: (success, current_value) where success is True if the check passed
        
    Example:
        success, value = wait_check_telemetry("TARGET", "HK_TLM_PK", "MODE", "==", "SAFE")
        if success:
            print(f"TARGET is in {value} mode as expected")
        else:
            print(f"Failed: TARGET is in {value} mode instead of SAFE")
    """
    
    if print_func is None:
        from .print_utils import test_print
        print_func = test_print
    
    # Use the COSMOS tlm function directly
    from openc3.script import tlm
    
    # Wait for the telemetry value
    result = wait_for_telemetry_value(
        target, 
        packet, 
        item, 
        comparison,
        comparison_value,
        timeout, 
        poll_interval, 
        print_func = print_func
    )
    
    # Get the final value regardless of result
    try:
        current_value = tlm(f"{target} {packet} {item}")
    except Exception as e:
        print_func(f"Error getting final telemetry value: {str(e)}")
        current_value = None
    
    return (result, current_value) # type: ignore


def wait_for_telemetry_in_range(
    target: str,
    packet: str,
    item: str,
    min_value: Union[int, float],
    max_value: Union[int, float],
    timeout: float = DEFAULT_WAIT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    inclusive: bool = True,
    print_func: Optional[Callable] = None
) -> bool:
    """
    Wait until a telemetry value is within a specified range.
    
    Args:
        target: The COSMOS target name
        packet: The COSMOS telemetry packet name
        item: The specific COSMOS telemetry item name
        min_value: Minimum acceptable value
        max_value: Maximum acceptable value
        timeout: Maximum wait time in seconds (default from system_config)
        poll_interval: Time between checks in seconds (default from system_config)
        inclusive: If True, the range is inclusive (min <= value <= max)
                  If False, the range is exclusive (min < value < max)
        print_func: Function to use for printing status/debug info (default: test_print)
        
    Returns:
        bool: True if value entered the range, False if timeout occurred
        
    Example:
        wait_for_telemetry_range("TARGET", "HK_TLM_PK", "BATTERY", 75, 100)
    """
    
    if print_func is None:
        from .print_utils import test_print
        print_func = test_print
    
    # Use the COSMOS tlm function directly
    from openc3.script import tlm
    
    # Track start time
    start_time = time.perf_counter()
    end_time = start_time + timeout
    
    # Initialize current_value for timeout reporting
    current_value = None
    
    # Main waiting loop
    while time.perf_counter() < end_time:
        # Get current value
        try:
            current_value = tlm(f"{target} {packet} {item}")
            
            # Only check range if we received telemetry
            if current_value is not None:
                # Check if the value is in range
                if inclusive:
                    if min_value <= current_value <= max_value:
                        print_func(f"{target} {packet} {item}: value {current_value} is within range [{min_value}, {max_value}]")
                        return True
                else:
                    if min_value < current_value < max_value:
                        print_func(f"{target} {packet} {item}: value {current_value} is within range ({min_value}, {max_value})")
                        return True
                
        except Exception as e:
            # Handle errors that might occur when getting telemetry
            print_func(f"Error getting telemetry {target} {packet} {item}: {str(e)}")
            
        # Wait before checking again
        time.sleep(poll_interval)
    
    # If we get here, we timed out
    range_type = "[]" if inclusive else "()"
    print_func(
        f"Timeout waiting for {target} {packet} {item} to be within range {min_value} {range_type[0]} "
        f"value {range_type[1]} {max_value}. Current value is {current_value}."
    )
        
    return False


def wait_for_telemetry_in_timing_range(
    target: str,
    packet: str,
    item: str,
    comparison: str,
    comparison_value: Any,
    min_time: Optional[float] = None,
    max_time: Optional[float] = None,
    timeout: float = DEFAULT_WAIT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    requirement_ids: Optional[Union[str, List[str]]] = None,
    req_tracker: Optional[Any] = None,
    print_func: Optional[Callable] = None
) -> Tuple[bool, float]:
    """
    Wait for a telemetry condition and verify it occurs within a specific time window.
    
    Can be used in coordination with a RequirementTracker object to set a requirement
    directly based on the outcome of this verification.
    
    Args:
        target: The COSMOS target name
        packet: The COSMOS telemetry packet name
        item: The specific COSMOS telemetry item name
        comparison: Comparison operator to use ("==", "!=", "<", "<=", ">", ">=", "contains", "does_not_contain")
        comparison_value: The value to wait for
        min_time: Minimum acceptable time in seconds (None for no minimum)
        max_time: Maximum acceptable time in seconds (None for no maximum)
        timeout: Maximum wait time in seconds (default from system_config)
        poll_interval: Time between telemetry checks in seconds (default from system_config)
        requirement_ids: Optional comma-separated string or list of requirement IDs to update
        req_tracker: RequirementTracker instance to use (required if requirement_ids provided)
        print_func: Function to use for printing status/debug info (default: test_print)
        
    Returns:
        Tuple containing:
          - bool: True if condition met within timing requirements, False otherwise
          - float: Response time in seconds if successful, or timeout value if timed out
          
    Example:
        # Basic usage - just wait for condition within timeout
        success, response_time = wait_for_telemetry_in_timing_range(
            "SPACECRAFT", "HK_TLM", "MODE", "==", "SCIENCE"
        )
        
        # Verify mode change occurs between 1-5 seconds after command
        success, response_time = wait_for_telemetry_in_timing_range(
            "SPACECRAFT", "HK_TLM", "MODE", "==", "SCIENCE",
            min_time=1.0, max_time=5.0
        )
        
        # With requirement tracking
        tracker = RequirementTracker()
        success, response_time = wait_for_telemetry_in_timing_range(
            "SPACECRAFT", "HK_TLM", "MODE", "==", "SCIENCE",
            min_time=1.0, max_time=5.0,
            requirement_ids="REQ-123, REQ-124", req_tracker=tracker
        )
        
        # Only minimum time requirement
        success, response_time = wait_for_telemetry_in_timing_range(
            "SPACECRAFT", "HK_TLM", "TEMPERATURE", ">", 50.0,
            min_time=2.0, timeout=20.0
        )
        
        # Only maximum time requirement
        success, response_time = wait_for_telemetry_in_timing_range(
            "SPACECRAFT", "HK_TLM", "RESPONSE", "==", "READY",
            max_time=10.0, timeout=15.0
        )
    """
    # Use test_print as the default print function if none provided
    if print_func is None:
        from .print_utils import test_print
        print_func = test_print
    
    # Import and use the COSMOS tlm function
    from openc3.script import tlm
        
    # Validate the comparison operator
    if comparison not in COMPARISON_OPERATORS:
        valid_ops = ", ".join(COMPARISON_OPERATORS.keys())
        raise ValueError(f"Invalid comparison operator '{comparison}'. Must be one of: {valid_ops}")
    
    # Function to perform the comparison
    compare = COMPARISON_OPERATORS[comparison]
    
    # Start timing
    start_time = time.perf_counter()
    
    # Initialize current_value for timeout reporting
    current_value = None
    
    # Main waiting loop
    end_time = start_time + timeout
    while time.perf_counter() < end_time:
        # Get current value
        try:
            current_value = tlm(f"{target} {packet} {item}")
            
            # Only check condition if we received telemetry
            if current_value is not None:
                # Check for the expected condition
                if compare(current_value, comparison_value):
                    # Condition met
                    response_time = time.perf_counter() - start_time
                    
                    # Format requirement message
                    condition_desc = f"{target} {packet} {item} {comparison} {comparison_value}"
                    
                    if min_time is not None and max_time is not None:
                        # Check min/max time requirements
                        if min_time <= response_time <= max_time:
                            success = True
                            req_message = f"{condition_desc} occurred in {response_time:.6f}s (required: {min_time:.6f}s to {max_time:.6f}s)"
                        else:
                            success = False
                            if response_time < min_time:
                                req_message = f"{condition_desc} occurred too quickly: {response_time:.6f}s (required: >= {min_time:.6f}s)"
                            else:
                                req_message = f"{condition_desc} occurred too slowly: {response_time:.6f}s (required: <= {max_time:.6f}s)"
                    
                    elif min_time is not None:
                        # Only minimum time specified
                        if response_time >= min_time:
                            success = True
                            req_message = f"{condition_desc} occurred in {response_time:.6f}s (required: >= {min_time:.6f}s)"
                        else:
                            success = False
                            req_message = f"{condition_desc} occurred too quickly: {response_time:.6f}s (required: >= {min_time:.6f}s)"
                    
                    elif max_time is not None:
                        # Only maximum time specified
                        if response_time <= max_time:
                            success = True
                            req_message = f"{condition_desc} occurred in {response_time:.6f}s (required: <= {max_time:.6f}s)"
                        else:
                            success = False
                            req_message = f"{condition_desc} occurred too slowly: {response_time:.6f}s (required: <= {max_time:.6f}s)"
                    
                    else:
                        # No specific timing requirements, just needed to happen before timeout
                        success = True
                        req_message = f"{condition_desc} occurred in {response_time:.6f}s (before timeout of {timeout}s)"
                    
                    # Update the requirement if tracking, otherwise print the message
                    if requirement_ids is not None and req_tracker is not None:
                        if success:
                            req_tracker.set_multiple_requirements(requirement_ids, "P", req_message)
                        else:
                            req_tracker.set_multiple_requirements(requirement_ids, "F", req_message)
                    else:
                        print_func(req_message)
                    
                    return success, response_time
                
        except Exception as e:
            # Handle errors that might occur when getting telemetry
            print_func(f"Error getting telemetry {target} {packet} {item}: {str(e)}")
            
        # Wait before checking again
        time.sleep(poll_interval)
    
    # If we get here, we timed out
    req_message = f"TIMEOUT: {target} {packet} {item} never reached {comparison_value} (current: {current_value}, timeout: {timeout}s)"
    
    # Update the requirement if tracking, otherwise print the message
    if requirement_ids is not None and req_tracker is not None:
        req_tracker.set_multiple_requirements(requirement_ids, "F", req_message)
    else:
        print_func(req_message)        
    
    return False, timeout


def wait_multiple_telemetry(
    conditions: List[List[Any]],
    timeout: Optional[float] = None,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    require_all: bool = True,
    print_func: Optional[Callable] = None
) -> Tuple[bool, Dict[str, bool]]:
    """
    Wait for multiple telemetry conditions simultaneously.
    
    Args:
        conditions: List of condition lists, each with elements:
                  - target: COSMOS target name
                  - packet: COSMOS packet name
                  - item: COSMOS telemetry item name
                  - comparison: Comparison operator (optional, default: '==')
                  - value: The value to compare against
        timeout: Maximum wait time in seconds (default: None, which uses system_config value)
        poll_interval: Time between checks in seconds (default from system_config)
        require_all: If True, all conditions must be met; if False, any condition met is success
        print_func: Function to use for printing status/debug info (default: test_print)
    
    Valid comparison operators:
        "==", "!=", "<", "<=", ">", ">=", "contains", "does_not_contain"
    
    Returns:
        Tuple[bool, Dict[str, bool]]: 
            - bool: Overall success (True if requirements met based on require_all setting)
            - Dict[str, bool]: Dictionary mapping auto-generated condition names to individual results (True/False)
    
    Raises:
        ValueError: If the timeout is negative
                    If a condition has an invalid number of elements
                    If the target, packet, or item in a condition are not strings
                    If an invalid comparison operator is provided.
        Exception: If there's an error retrieving telemetry values.
        
    Examples:
        # Basic usage - check overall success first
        # Using default comparison operator ('==') for first condition only
        overall_success, results = wait_multiple_telemetry([
            ['TARGET', 'HK_TLM_PK', 'MODE', 'SAFE'],
            ['TARGET', 'HK_TLM_PK', 'BATTERY', '>=', 75]
        ])
        
        # Using default comparison operator ('==')
        overall_success, results = wait_multiple_telemetry([
            ['TARGET', 'HK_TLM_PK', 'MODE', 'SAFE'],
            ['TARGET', 'HK_TLM_PK', 'POWER_STATE', 'ON']
        ])
        
        if overall_success:
            print("All conditions met!")
        else:
            print("Some conditions failed:")
            for condition_name, success in results.items():
                if not success:
                    print(f"  Failed: {condition_name}")
        
        # Require any condition to pass (not all)
        overall_success, results = wait_multiple_telemetry([
            ['TARGET', 'HK_TLM_PK', 'MODE', 'SAFE'],
            ['TARGET', 'HK_TLM_PK', 'MODE', 'SCIENCE']
        ], require_all=False)
    
        # Simple example with building an expected_conditions variable and ignoring the detailed results return
        expected_conditions = [
            ['TARGET', 'HEALTH_TLM', 'TEMPERATURE', '<', 30],
            ['TARGET', 'HEALTH_TLM', 'POWER_STATUS', 'ON']
        ]
        overall_success, _ = wait_multiple_telemetry(expected_conditions)
    
    
    Note:
        - If a telemetry retrieval error occurs for a condition, that condition is marked as failed.
        - The function tracks state changes and only prints when a condition's state changes.
    """
    if timeout is None:
        timeout = DEFAULT_WAIT_TIMEOUT
    elif timeout < 0:
        raise ValueError("Timeout must be a non-negative number")
    
    if print_func is None:
        from .print_utils import test_print
        print_func = test_print
    
    # Use the COSMOS tlm function directly
    from openc3.script import tlm
    
    # Validate conditions and set up comparison functions
    formatted_conditions = []
    for i, condition in enumerate(conditions):
        if len(condition) < 4 or len(condition) > 5:
            raise ValueError(f"Condition {i} has invalid number of elements. Expected 4 or 5, got {len(condition)}")
        
        # Check that target, packet, and item are strings
        if not all(isinstance(elem, str) for elem in condition[:3]):
            raise ValueError(f"Condition {i}: target, packet, and item must be strings")
        
        formatted_condition = {
            'target': condition[0],
            'packet': condition[1],
            'item': condition[2],
            'comparison': '==' if len(condition) == 4 else condition[3],
            'value': condition[-1]
        }
        
        if formatted_condition['comparison'] not in COMPARISON_OPERATORS:
            valid_ops = ", ".join(COMPARISON_OPERATORS.keys())
            raise ValueError(f"Invalid comparison operator '{formatted_condition['comparison']}' in condition {i}. Must be one of: {valid_ops}")
            
        # Add the comparison function
        formatted_condition['compare_func'] = COMPARISON_OPERATORS[formatted_condition['comparison']]
         
        # Create a descriptive name for this condition
        formatted_condition['name'] = f"{formatted_condition['target']}_{formatted_condition['packet']}_{formatted_condition['item']}_{formatted_condition['comparison']}_{str(formatted_condition['value'])}"
        
        formatted_conditions.append(formatted_condition)
            
    # Initialize results dictionary and previous state tracking
    results = {condition['name']: False for condition in formatted_conditions}
    previous_results = {condition['name']: None for condition in formatted_conditions}  # None = untested
    last_values = {condition['name']: None for condition in formatted_conditions}  # Track last value for each condition
    
    # Track start time
    start_time = time.perf_counter()
    end_time = start_time + timeout
    
    # Main waiting loop
    while time.perf_counter() < end_time:
        # Check all conditions
        all_met = True
        any_met = False
        
        for condition in formatted_conditions:
            name = condition['name']
            
            # Skip checking already satisfied conditions if not require_all
            if not require_all and results[name]:
                any_met = True
                continue
                
            # Get current value
            try:
                current_value = tlm(f"{condition['target']} {condition['packet']} {condition['item']}")
                
                # Store the last value
                last_values[name] = current_value
                
                # Only check condition if we received telemetry
                if current_value is not None:
                    # Check condition
                    result = condition['compare_func'](current_value, condition['value'])
                    
                    # Check if state changed and print only on transitions
                    if previous_results[name] != result:
                        if result:
                            # Condition newly met (from None/False to True)
                            print_func(
                                f" <*> Condition met: {condition['target']} {condition['packet']} {condition['item']} "
                                f"{condition['comparison']} {condition['value']} (current: {current_value})"
                            )
                        else:
                            # Condition newly failed (from None/True to False)
                            if previous_results[name] is not None:  # Only print if it was previously met
                                print_func(
                                    f" <!> Condition no longer met: Expecting {condition['target']} {condition['packet']} {condition['item']} "
                                    f"{condition['comparison']} {condition['value']} (current: {current_value})"
                                )
                    
                    # Update state tracking
                    previous_results[name] = result
                    results[name] = result
                    
                    if result:
                        any_met = True
                    else:
                        all_met = False
                else:
                    # current_value is None, mark as not met
                    results[name] = False
                    all_met = False                    
            
            except Exception as e:
                # Handle errors that might occur when getting telemetry
                # Only print error if it's a new error (state change)
                if previous_results[name] != False:
                    print_func(f" <!> Error checking condition {name}: {str(e)}")
                previous_results[name] = False
                results[name] = False
                all_met = False
                
        # Check if we're done
        if (require_all and all_met) or (not require_all and any_met):
            # Return overall success based on require_all setting
            overall_success = all_met if require_all else any_met
            return overall_success, results
            
        # Wait before checking again
        time.sleep(poll_interval)
    
    # If we get here, we timed out
    print_func(f" <!> Timeout waiting for {'all' if require_all else 'any'} telemetry conditions to be met")
    for condition in formatted_conditions:
        name = condition['name']
        current_value = last_values[name]
        print_func(
            f"Expected Condition: {condition['target']} {condition['packet']} {condition['item']} "
            f"{condition['comparison']} {condition['value']} (current: {current_value}) = {results[name]}"
        )
    
    # Return overall failure due to timeout
    return False, results
