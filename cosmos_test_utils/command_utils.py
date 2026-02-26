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

"""Utilities for sending commands and tracking responses in COSMOS tests."""

import time  # Used for timestamps
from typing import Any, Callable, Dict, List, Optional

from .system_config import DEFAULT_WAIT_TIMEOUT, DEFAULT_POLL_INTERVAL

class CommandSender:
    """Class for sending commands and verifying responses with requirement tracking."""
    
    def __init__(
        self,
        req_tracker: Optional[Any] = None,
        print_func: Optional[Callable] = print 
    ):
        """Initialize a CommandSender.
        
        Args:
            req_tracker: RequirementTracker instance to use
            print_func: Function to use for printing status/debug info (default: built-in print)
        """
        # Import COSMOS functions
        try:
            from openc3.script import cmd, tlm
            self.cmd = cmd
            self.tlm = tlm
        except ImportError:
            # For testing outside of COSMOS
            print("Warning: openc3.script not found, using mock cmd/tlm functions")
            self.cmd = lambda cmd_string, **kwargs: None  # Updated: cmd returns None
            self.tlm = lambda tlm_string: "MOCK_VALUE"
        
        # Store the requirement tracker
        self.req_tracker = req_tracker
        
        # Protect against None print_func - fallback to built-in print
        if print_func is None:
            self.print_func = print
        else:
            self.print_func = print_func
        
        # Track command history
        self.command_history = []
    
    
    def send_command(self, command_string: str, **kwargs) -> None:
        """Send a single command and track it in command history.
        
        This is a basic function for sending commands without waiting for responses.
        For commands where you need to verify the response, use send_cmd_with_response_check().
        
        Features:
        - Command history tracking
        - Direct COSMOS cmd function parameter passing
        
        Args:
            command_string: The command string to send
            **kwargs: Additional arguments passed directly to the COSMOS cmd() function.
                     Currently supported by openc3 COSMOS: timeout (default: 5), 
                     log_message (default: True), validate (default: True).
                     If COSMOS adds more arguments, this function will still work.
            
        Examples:
            # Simple command
            sender.send_command("TARGET NOOP")
            
            # Command with f-string formatting
            value = 42
            sender.send_command(f"TARGET SET_VALUE with VALUE {value}")
            
            # Command with multiple variables
            mode = "SCIENCE"
            delay = 10
            sender.send_command(f"TARGET SET_MODE with MODE '{mode}' DELAY {delay}")
            
        See examples/command_examples.py or README.md for more nuanced and detailed usage examples.
        """
        # Send the command (cmd returns None)
        self.cmd(command_string, **kwargs)
        
        # Create command record with useful information
        command_record = {
            "command": command_string,
            "timestamp": time.time(),
            # Only include kwargs if they're not empty
            **({"kwargs": kwargs} if kwargs else {})
        }
        
        # Add to history
        self.command_history.append(command_record)
        
        # Log the command to our print function
        self.print_func(f"Command sent: {command_string}")
    
    
    def send_cmd_multiple_times(
        self,
        command_string: str,
        count: int = 1, 
        delay: float = 0.0,
        **kwargs
    ) -> None:
        """Send a command multiple times.
        
        Features:
        - Multiple command execution
        - Configurable delay between commands
        - Command history tracking for each command
        - Direct COSMOS cmd function parameter passing
        
        Args:
            command_string: The command string to send
            count: Number of times to send the command
            delay: Delay in seconds between commands
            **kwargs: Additional arguments passed directly to the COSMOS cmd() function
            
        Examples:
            # Simple command repeated 3 times
            sender.send_cmd_multiple_times("TARGET NOOP", count=3)
            
            # Command with f-string formatting repeated 5 times with delay
            value = 42
            sender.send_cmd_multiple_times(f"TARGET SET_VALUE with VALUE {value}", count=5, delay=1.0)
        """
        for i in range(count):
            # Send command with specific parameters
            self.send_command(command_string, **kwargs)
            
            # Add delay if this isn't the last command
            if i < count - 1 and delay > 0:
                time.sleep(delay)
    
    
    def send_cmd_with_response_check(
        self,
        command_string: str,
        target: str,
        packet: str,
        item: str,
        comparison: str,
        comparison_value: Any,
        tlm_timeout: float = DEFAULT_WAIT_TIMEOUT,
        tlm_poll_interval: float = DEFAULT_POLL_INTERVAL,
        **kwargs
    ) -> bool:
        """Send a command and wait for a telemetry item to meet a given comparison criteria.
        
        This function sends a command and then waits for a specific telemetry item
        to meet an expected comparison criteria. Command details and response information
        are available through get_command_history().
        
        Features:
        - Command history tracking
        - Response time measurement
        - Flexible value comparison options
        - Detailed response tracking
        
        Args:
            command_string: The command string to send
            target: The COSMOS target name to monitor for response telemetry
            packet: The COSMOS telemetry packet name to monitor for response
            item: The specific COSMOS telemetry item name to monitor for response
            comparison: Comparison operator comparing item to comparison_value
                       Options: "==", "!=", "<", "<=", ">", ">=", "contains", "does_not_contain"
            comparison_value: The telemetry value to compare against
            tlm_timeout: Maximum time to wait for telemetry response in seconds (default from system_config)
            tlm_poll_interval: Time between telemetry checks in seconds (default from system_config)
            **kwargs: Additional arguments passed directly to the COSMOS cmd() function
            
        Returns:
            bool: True if the telemetry response met the comparison criteria within the timeout
        
        Examples:
            # Basic usage - wait for a specific value
            success = sender.send_cmd_with_response_check(
                "TARGET SET_MODE with MODE 'SCIENCE'",
                "TARGET", "HK_TLM", "MODE", "==", "SCIENCE",
                tlm_timeout=10.0
            )
            
            # Using a comparison operator
            success = sender.send_cmd_with_response_check(
                "TARGET INCREASE_VALUE with DELTA 5",
                "TARGET", "HK_TLM", "VALUE", ">=", 10
            )
            
            # With f-string formatting and custom telemetry polling
            threshold = 75
            success = sender.send_cmd_with_response_check(
                f"TARGET SET_THRESHOLD with VALUE {threshold}",
                "TARGET", "HK_TLM", "THRESHOLD", "==", threshold,
                tlm_poll_interval=0.1
            )
            
            # Check command history for details
            history = sender.get_command_history()
            last_cmd = history[-1]
            if last_cmd.get('response', {}).get('success'):
                print(f"Response received in {last_cmd['response']['time']:.2f} seconds")
                print(f"Final value: {last_cmd['response']['value']}")
        
        See examples/command_examples.py or README.md for more nuanced and detailed usage examples.
        """
        # Import the wait utility function
        from .wait_utils import wait_for_telemetry_value
        
        # Send the command and record command info
        self.send_command(command_string, **kwargs)
        start_time = time.perf_counter()  # Start timing for response
        
        # Use wait_for_telemetry_value to wait for the expected response
        success = wait_for_telemetry_value(
            target, packet, item, comparison, comparison_value,
            timeout=tlm_timeout, 
            poll_interval=tlm_poll_interval,
            print_func=self.print_func
        )        
        
        # Calculate response time
        end_time = time.perf_counter()
        response_time = end_time - start_time
        
        # Get the most recent command record to update with response info
        cmd_record = self.command_history[-1]
        
        if success:
            # Get the current value (which matches the expected value)
            current_value = self.tlm(f"{target} {packet} {item}")
            self.print_func(f"<*> Response received in {response_time:.6f} seconds")
            
            # Update command record with response info
            cmd_record["response"] = {
                "success": True,
                "time": response_time,
                "value": current_value,
                "target": target,
                "packet": packet,
                "item": item,
                "comparison_value": comparison_value,
                "comparison": comparison
            }
            
        else:
            # Timeout occurred - get the current value for reporting
            try:
                current_value = self.tlm(f"{target} {packet} {item}")
                
                # Update command record with timeout info
                cmd_record["response"] = {
                    "success": False,
                    "time": tlm_timeout,  # Use the specified telemetry timeout value
                    "value": current_value,
                    "target": target,
                    "packet": packet,
                    "item": item,
                    "comparison_value": comparison_value,
                    "comparison": comparison,
                    "timeout": tlm_timeout
                }
                
            except Exception as e:
                self.print_func(f"<!> Error getting telemetry after timeout: {str(e)}")
                
                # Update command record with error info
                cmd_record["response"] = {
                    "success": False,
                    "time": tlm_timeout,
                    "error": str(e),
                    "target": target,
                    "packet": packet,
                    "item": item,
                    "comparison_value": comparison_value,
                    "comparison": comparison,
                    "timeout": tlm_timeout
                }
        
        return success
    
    
    def send_cmd_with_requirement(
        self,
        command_string: str,
        target: str,
        packet: str,
        item: str,
        comparison: str,
        comparison_value: Any,
        requirement_ids: str,
        tlm_timeout: float = DEFAULT_WAIT_TIMEOUT,
        tlm_poll_interval: float = DEFAULT_POLL_INTERVAL,
        **kwargs
    ) -> bool:
        """Send a command, wait for telemetry to meet certain criteria, and set requirement status based on the result.
        
        Features:
        - Command history tracking
        - Response time measurement
        - Requirement status setting (Pass/Fail based on telemetry response)
        - Detailed response and requirement tracking
        
        Args:
            command_string: The command string to send
            target: The COSMOS target name for telemetry monitoring
            packet: The COSMOS telemetry packet name for telemetry monitoring
            item: The specific COSMOS telemetry item name to monitor for the comparison
            comparison: Comparison operator comparing item to comparison_value
            comparison_value: The value to compare against the telemetry 'item' using 'comparison'
            requirement_ids: Comma-separated string of requirement IDs to update
            tlm_timeout: Maximum time to wait for telemetry response in seconds (default from system_config)
            tlm_poll_interval: Time between telemetry checks in seconds (default from system_config)
            **kwargs: Additional arguments passed directly to the COSMOS cmd() function
            
        Returns:
            bool: True if the telemetry response met the comparison criteria
        
        Examples:
            # Basic requirement verification
            success = sender.send_cmd_with_requirement(
                "TARGET SET_MODE with MODE 'SCIENCE'",
                "TARGET", "HK_TLM", "MODE", "==", "SCIENCE",
                "REQ-123"
            )
            
            # With custom timeouts and multiple requirements
            success = sender.send_cmd_with_requirement(
                "TARGET CONFIGURE",
                "TARGET", "STATUS_TLM", "CONFIG_STATE", "==", "CONFIGURED",
                "REQ-456, REQ-457, REQ-458",
                tlm_timeout=15.0
            )
            
            # With f-string formatting, custom polling interval, and multiple requirements
            threshold = 75
            success = sender.send_cmd_with_requirement(
                f"TARGET SET_THRESHOLD with VALUE {threshold}",
                "TARGET", "HK_TLM", "THRESHOLD", "==", threshold,
                "REQ-789, REQ-790",
                tlm_poll_interval=0.05
            )
        """
        # Check if we have a requirement tracker
        if self.req_tracker is None:
            self.print_func("Warning: No requirement tracker set. Cannot update requirement status. "
                           "Set requirement tracker when creating CommandSender: CommandSender(req_tracker=tracker) "
                           "or use set_req_tracker(tracker) method.")
        
        # Send command and check for response
        success = self.send_cmd_with_response_check(
            command_string, 
            target, packet, item, comparison, comparison_value,
            tlm_timeout=tlm_timeout, 
            tlm_poll_interval=tlm_poll_interval,
            **kwargs
        )
        
        # Get the most recent command record for response info
        cmd_record = self.command_history[-1]
        response_time = cmd_record.get("response", {}).get("time", tlm_timeout)
        
        # Format the requirement message
        condition_desc = f"'{command_string}' -> {target} {packet} {item} {comparison} {comparison_value}"
        
        if success:
            req_message = f"Command {condition_desc} met the specified condition in {response_time:.6f}s"
        else:
            current_value = cmd_record.get("response", {}).get("value", "unknown")
            req_message = f"Command {condition_desc} did not meet the specified condition within {tlm_timeout}s (current: {current_value})"
        
        # Update the requirement if tracker is available
        if self.req_tracker is not None:
            if success:
                self.req_tracker.set_multiple_requirements(requirement_ids, "P", req_message)
            else:
                self.req_tracker.set_multiple_requirements(requirement_ids, "F", req_message)
        else:
            # Add prefix to message indicating no requirement tracker
            req_message = f"<!> No requirement tracker set - requirement not logged: {req_message}"
            # Print result only if no requirement tracker (to avoid redundant messages)
            self.print_func(req_message)
        
        # Add requirement info to command record
        cmd_record["requirement"] = {
            "ids": requirement_ids,
            "success": success,
            "message": req_message
        }
        
        return success
    
    
    def send_cmd_with_timing_requirement(
        self,
        command_string: str,
        target: str,
        packet: str,
        item: str,
        comparison: str,
        comparison_value: Any,
        requirement_ids: str,
        min_time: Optional[float] = None,
        max_time: Optional[float] = None,
        tlm_timeout: float = DEFAULT_WAIT_TIMEOUT,
        tlm_poll_interval: float = DEFAULT_POLL_INTERVAL,
        **kwargs
    ) -> bool:
        """Send a command, check response timing, and set requirement status based on whether or not the correct response fell within the given response window.
        
        Features:
        - Command history tracking
        - Response time measurement against timing thresholds
        - Requirement status setting based on timing compliance
        - Detailed response, timing, and requirement tracking
        
        Args:
            command_string: The command string to send
            target: The COSMOS target name for telemetry monitoring
            packet: The COSMOS telemetry packet name for telemetry monitoring
            item: The specific COSMOS telemetry item name to monitor for the comparison
            comparison: Comparison operator comparing item to comparison_value
            comparison_value: The value to compare against the telemetry 'item' using 'comparison'
            requirement_ids: Comma-separated string of requirement IDs to update
            min_time: Minimum acceptable response time (None for no minimum)
            max_time: Maximum acceptable response time (None for no maximum)
            tlm_timeout: Maximum time to wait for telemetry response in seconds (default from system_config)
            tlm_poll_interval: Time between telemetry checks in seconds (default from system_config)
            **kwargs: Additional arguments passed directly to the COSMOS cmd() function
            
        Returns:
            bool: True if response matched and met timing requirements
        
        Examples:
            # Basic timing requirement with min and max response times
            success = sender.send_cmd_with_timing_requirement(
                "TARGET SET_MODE with MODE 'SCIENCE'",
                "TARGET", "HK_TLM", "MODE", "==", "SCIENCE",
                "REQ-TIMING-001",
                min_time=1.0,
                max_time=5.0
            )
            
            # Only maximum response time with custom timeouts and multiple requirements
            success = sender.send_cmd_with_timing_requirement(
                "TARGET QUICK_RESPONSE",
                "TARGET", "STATUS_TLM", "READY", "==", True,
                "REQ-TIMING-002, REQ-TIMING-003",
                max_time=2.0,
                tlm_timeout=10.0
            )
            
            # With f-string formatting and multiple requirements
            threshold = 100
            success = sender.send_cmd_with_timing_requirement(
                f"TARGET SET_THRESHOLD with VALUE {threshold}",
                "TARGET", "CONFIG_TLM", "THRESHOLD", "==", threshold,
                "REQ-TIMING-004, REQ-TIMING-005, REQ-TIMING-006",
                min_time=0.5,
                max_time=3.0
            )
        """
        # Check if we have a requirement tracker
        if self.req_tracker is None:
            self.print_func("Warning: No requirement tracker set. Cannot update requirement status. "
                           "Set requirement tracker when creating CommandSender: CommandSender(req_tracker=tracker) "
                           "or use set_req_tracker(tracker) method.")
        
        # Validate timeout against timing constraints
        if min_time is not None and tlm_timeout <= min_time:
            self.print_func(f"Warning: tlm_timeout ({tlm_timeout}s) is less than or equal to min_time ({min_time}s). "
                           f"This may prevent meeting timing requirements.")
        
        if max_time is not None:
            if tlm_timeout == DEFAULT_WAIT_TIMEOUT and tlm_timeout <= max_time:
                # Only automatically adjust if timeout is still at default value
                original_timeout = tlm_timeout
                tlm_timeout = max_time + 1.0
                self.print_func(f"Info: tlm_timeout was at default ({original_timeout}s) and less than or equal to max_time ({max_time}s). "
                               f"Automatically adjusted tlm_timeout to {tlm_timeout}s to allow timing window to be tested.")
            elif tlm_timeout <= max_time:
                # User explicitly set timeout but it's too small
                self.print_func(f"Warning: tlm_timeout ({tlm_timeout}s) is less than or equal to max_time ({max_time}s). "
                               f"This may prevent meeting timing requirements.")
        
        # Additional validation: ensure min_time <= max_time if both are specified
        if min_time is not None and max_time is not None and min_time > max_time:
            raise ValueError(f"min_time ({min_time}s) cannot be greater than max_time ({max_time}s)")
        
        # Send command and check for response
        success = self.send_cmd_with_response_check(
            command_string, 
            target, packet, item, comparison, comparison_value,
            tlm_timeout=tlm_timeout, 
            tlm_poll_interval=tlm_poll_interval,
            **kwargs
        )
        
        # Get the most recent command record for response info
        cmd_record = self.command_history[-1]
        response_time = cmd_record.get("response", {}).get("time", tlm_timeout)
        
        # Initialize requirement status and message
        req_success = False
        req_message = ""
        condition_desc = f"'{command_string}' -> {target} {packet} {item} {comparison} {comparison_value}"
        
        if not success:
            # Response not received within timeout
            req_success = False
            req_message = f"Command {condition_desc} did not meet the specified condition within timeout of {tlm_timeout} seconds"
        else:
            # Response received, check timing requirements
            if min_time is not None and max_time is not None:
                # Both min and max specified
                if min_time <= response_time <= max_time:
                    req_success = True
                    req_message = f"Command {condition_desc} met the specified condition in {response_time:.6f}s (required: {min_time:.6f}s to {max_time:.6f}s)"
                else:
                    req_success = False
                    if response_time < min_time:
                        req_message = f"Command {condition_desc} met the specified condition too quickly: {response_time:.6f}s (required: >= {min_time:.6f}s)"
                    else:
                        req_message = f"Command {condition_desc} met the specified condition too slowly: {response_time:.6f}s (required: <= {max_time:.6f}s)"
            
            elif min_time is not None:
                # Only min specified
                if response_time >= min_time:
                    req_success = True
                    req_message = f"Command {condition_desc} met the specified condition in {response_time:.6f}s (required: >= {min_time:.6f}s)"
                else:
                    req_success = False
                    req_message = f"Command {condition_desc} met the specified condition too quickly: {response_time:.6f}s (required: >= {min_time:.6f}s)"
            
            elif max_time is not None:
                # Only max specified
                if response_time <= max_time:
                    req_success = True
                    req_message = f"Command {condition_desc} met the specified condition in {response_time:.6f}s (required: <= {max_time:.6f}s)"
                else:
                    req_success = False
                    req_message = f"Command {condition_desc} met the specified condition too slowly: {response_time:.6f}s (required: <= {max_time:.6f}s)"
            
            else:
                # No specific timing requirements, just needed a response
                req_success = True
                req_message = f"Command {condition_desc} met the specified condition in {response_time:.6f}s"
        
        # Update the requirement if tracker is available
        if self.req_tracker is not None:
            if req_success:
                self.req_tracker.set_multiple_requirements(requirement_ids, "P", req_message)
            else:
                self.req_tracker.set_multiple_requirements(requirement_ids, "F", req_message)
        else:
            # Add prefix to message indicating no requirement tracker
            req_message = f"<!> No requirement tracker set - requirement not logged: {req_message}"
            # Print result only if no requirement tracker (to avoid redundant messages)
            self.print_func(req_message)
        
        # Add requirement info to command record
        cmd_record["requirement"] = {
            "ids": requirement_ids,
            "success": req_success,
            "message": req_message
        }
        
        # Return the overall result (both response received AND requirements met)
        return req_success
    
    
    def send_cmd_multiple_times_with_requirement(
        self,
        command_string: str,
        count: int,
        target: str,
        packet: str,
        item: str,
        base_tlm_value: int,
        requirement_ids: str,
        expected_increment_per_cmd: int = 1,
        cmd_delay: float = 0.0,
        tlm_timeout_ea_cmd: float = DEFAULT_WAIT_TIMEOUT,
        tlm_poll_interval: float = DEFAULT_POLL_INTERVAL,
        fail_on_first_error: bool = False,
        **kwargs
    ) -> bool:
        """Send a command multiple times and set requirements based on each response.
        
        This function is designed for use with integer telemetry that has a predictable
        increment after each command is received. It assumes that the telemetry value
        will increase by a fixed amount (default 1) for each command sent.
        
        Features:
        - Command history tracking for each command
        - Response time measurement for each command
        - Requirement tracking for each command execution
        - Configurable delay between commands
        - Optional early termination on failure
        - Automatic increment of expected telemetry value for each command
        
        Args:
            command_string: The command string to send
            count: Number of times to send the command (must be greater than 0)
            target: The COSMOS target name for telemetry monitoring
            packet: The COSMOS telemetry packet name for telemetry monitoring
            item: The specific COSMOS telemetry item name to monitor for the comparison
            base_tlm_value: The base telemetry value to start comparisons from (integer)
            requirement_ids: Comma-separated string of requirement IDs to update for each command
            expected_increment_per_cmd: Expected increment of telemetry value per command (integer, default: 1)
            cmd_delay: Delay in seconds between commands (non-negative)
            tlm_timeout_ea_cmd: Maximum time to wait for each tlm response condition to be met
            tlm_poll_interval: Time between telemetry checks in seconds
            fail_on_first_error: If True, stop sending commands after first failure
            **kwargs: Additional arguments passed directly to the COSMOS cmd() function
            
        Returns:
            bool: True if all calls to send_cmd_with_requirement() completed successfully
        
        Raises:
            ValueError: If count is not greater than 0 or cmd_delay is negative
 
        Examples:
            # Basic multiple (3) commands with requirement verification
            # Expects the tlm will increment by 1 (default) each command sent
            all_success = sender.send_cmd_multiple_times_with_requirement(
                "TARGET NOOP_CMD", 3,
                "TARGET", "HK_PKT", "cmdCnt",
                savedHKCnt,
                "REQ-NOOP-001"
            )
            
            # With delay between (5) commands, custom timeouts, and multiple requirements
            all_success = sender.send_cmd_multiple_times_with_requirement(
                "TARGET PERIODIC_TASK", 5,
                "TARGET", "STATUS_TLM", "TASK_COUNT",
                base_tlm_value=initial_task_count,
                requirement_ids="REQ-PERIODIC-001, REQ-PERIODIC-002",
                expected_increment_per_cmd=2,
                cmd_delay=2.0,
                tlm_timeout_ea_cmd=8.0
            )
            
            # With f-string formatting, fail on first requirement failure, and multiple requirements
            value = 100
            all_success = sender.send_cmd_multiple_times_with_requirement(
                f"TARGET SET_VALUE with VALUE {value}", 4,
                "TARGET", "CONFIG_TLM", "VALUE_COUNTER",
                initial_value_count,
                requirement_ids="REQ-SET-VALUE-001, REQ-SET-VALUE-002, REQ-SET-VALUE-003",
                expected_increment_per_cmd=5,
                fail_on_first_error=True
            )
        """
        if count <= 0:
            raise ValueError("count must be a greater than 0 integer")
        if cmd_delay < 0:
            raise ValueError("cmd_delay must be non-negative")
        
        all_successful = True
        
        for i in range(count):
            # Calculate the expected telemetry value for this command
            expected_value = base_tlm_value + (expected_increment_per_cmd * (i + 1))

            # Send command and check requirements (using the same requirement_ids for all)
            success = self.send_cmd_with_requirement(
                command_string,
                target, packet, item, "==", expected_value,
                requirement_ids,
                tlm_timeout=tlm_timeout_ea_cmd, 
                tlm_poll_interval=tlm_poll_interval,
                **kwargs
            )
            
            # Update overall success
            all_successful = all_successful and success
            
            # Check if we should stop on failure
            if not success and fail_on_first_error:
                self.print_func(f"<!> Stopping command sequence after failure on command {i+1} of {count}")
                break
                
            # Add delay if this isn't the last command
            if i < count - 1 and cmd_delay > 0:
                time.sleep(cmd_delay)
        
        return all_successful
    
    
    def send_cmd_multiple_times_with_timing_requirement(
        self,
        command_string: str,
        count: int,
        target: str,
        packet: str,
        item: str,
        base_tlm_value: int,
        requirement_ids: str,
        expected_increment_per_cmd: int = 1,
        min_time: Optional[float] = None,
        max_time: Optional[float] = None,
        cmd_delay: float = 0.0,
        tlm_timeout_ea_cmd: float = DEFAULT_WAIT_TIMEOUT,
        tlm_poll_interval: float = DEFAULT_POLL_INTERVAL,
        fail_on_first_error: bool = False,
        **kwargs
    ) -> bool:
        """Send a command multiple times and set requirements based on response timing.
        
        This function is designed for use with integer telemetry that has a predictable
        increment after each command is received. It assumes that the telemetry value
        will increase by a fixed amount (default 1) for each command sent.

        Features:
        - Command history tracking for each command
        - Response time measurement against timing thresholds
        - Requirement tracking for each command execution
        - Configurable delay between commands
        - Optional early termination on failure
        - Automatic increment of expected telemetry value for each command
        
        Args:
            command_string: The command string to send
            count: Number of times to send the command (must be greater than 0)
            target: The COSMOS target name for telemetry monitoring
            packet: The COSMOS telemetry packet name for telemetry monitoring
            item: The specific COSMOS telemetry item name to monitor for the comparison
            base_tlm_value: The base telemetry value to start comparisons from (integer)
            requirement_ids: Comma-separated string of requirement IDs to update for each command
            expected_increment_per_cmd: Expected increment of telemetry value per command (integer, default: 1)
            min_time: Minimum acceptable response time (None for no minimum)
            max_time: Maximum acceptable response time (None for no maximum)
            cmd_delay: Delay in seconds between commands (non-negative)
            tlm_timeout_ea_cmd: Maximum time to wait for each tlm response condition to be met
            tlm_poll_interval: Time between telemetry checks in seconds
            fail_on_first_error: If True, stop sending commands after first failure
            **kwargs: Additional arguments passed directly to the COSMOS cmd() function
            
        Returns:
            bool: True if all calls to send_cmd_with_timing_requirement() completed successfully
        
        Raises:
            ValueError: If count is not greater than 0 or cmd_delay is negative

        Examples:
            # Basic multiple (3) command timing with requirement verification
            all_success = sender.send_cmd_multiple_times_with_timing_requirement(
                "TARGET NOOP_CMD", 3,
                "TARGET", "HK_PKT", "cmdCnt",
                savedHKCnt,
                "REQ-NOOP-TIMING-001",
                min_time=0.1,
                max_time=5.0
            )
            
            # With delay between (5) commands, custom timeouts, and multiple requirements
            all_success = sender.send_cmd_multiple_times_with_timing_requirement(
                "TARGET PERIODIC_TASK", 5,
                "TARGET", "STATUS_TLM", "TASK_COUNT",
                base_tlm_value=initial_task_count,
                requirement_ids="REQ-PERIODIC-TIMING-001, REQ-PERIODIC-TIMING-002",
                expected_increment_per_cmd=2,
                min_time=1.5,
                max_time=3.0,
                cmd_delay=2.0,
                tlm_timeout_ea_cmd=8.0
            )
            
            # With f-string formatting, fail on first timing requirement error, and multiple requirements
            value = 100
            all_success = sender.send_cmd_multiple_times_with_timing_requirement(
                f"TARGET SET_VALUE with VALUE {value}", 4,
                "TARGET", "CONFIG_TLM", "VALUE_COUNTER",
                initial_value_count,
                requirement_ids="REQ-SET-VALUE-TIMING-001, REQ-SET-VALUE-TIMING-002, REQ-SET-VALUE-TIMING-003",
                expected_increment_per_cmd=5,
                min_time=0.5,
                max_time=2.0,
                fail_on_first_error=True
            )
        """
        if count <= 0:
            raise ValueError("count must be a greater than 0 integer")
        if cmd_delay < 0:
            raise ValueError("cmd_delay must be non-negative")

        all_successful = True
        
        for i in range(count):
            # Calculate the expected telemetry value for this command
            expected_value = base_tlm_value + (expected_increment_per_cmd * (i + 1))

            # Send command and check requirements (using the same requirement_ids for all)
            success = self.send_cmd_with_timing_requirement(
                command_string,
                target, packet, item, "==", expected_value,
                requirement_ids,
                min_time=min_time,
                max_time=max_time,
                tlm_timeout=tlm_timeout_ea_cmd, 
                tlm_poll_interval=tlm_poll_interval,
                **kwargs
            )
            
            # Update overall success
            all_successful = all_successful and success
            
            # Check if we should stop on failure
            if not success and fail_on_first_error:
                self.print_func(f"<!> Stopping command sequence after failure on command {i+1} of {count}")
                break
                
            # Add delay if this isn't the last command
            if i < count - 1 and cmd_delay > 0:
                time.sleep(cmd_delay)
        
        return all_successful
    
    
    def get_command_history(self, num_commands: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the history of commands sent.
        
        Features:
        - Access to complete or partial command history
        - Includes command details, results, and response info
        
        Args:
            num_commands: Number of most recent commands to return (None for all commands)
        
        Returns:
            List of command records
        
        Examples:
            # Get all command history
            all_commands = sender.get_command_history()
            
            # Get last 5 commands
            recent_commands = sender.get_command_history(5)
            
            # Get response time from last command
            last_cmd = sender.get_command_history(1)[0]
            if 'response' in last_cmd:
                response_time = last_cmd['response']['time']
                print(f"Last command response time: {response_time:.3f}s")
        """
        if num_commands is None:
            return self.command_history
        else:
            return self.command_history[-num_commands:] if num_commands > 0 else []
    
    
    def clear_history(self) -> None:
        """Clear the command history.
        
        Features:
        - Reset command history to start fresh
        """
        self.command_history = []
        
    
    def print_command_history(
        self, 
        detail_level: int = 1,
        include_responses: bool = True,
        include_requirements: bool = True,
        max_entries: Optional[int] = None,
        print_func: Optional[Callable] = None
    ) -> None:
        """Print the command history in a formatted, readable way.
        
        This method provides a clean presentation of the command history with
        configurable detail levels and filtering options.
        
        Args:
            detail_level: Level of detail to print (default: 1)
                         0 = Basic (command strings and basic response and requirement status, if any)
                         1 = Standard (commands, timestamps, telemetry conditions, requirements)
                         2 = Verbose (all information including kwargs and final values)
            include_responses: Whether to include response details when available (default: True)
            include_requirements: Whether to include requirement details when available (default: True)
            max_entries: Maximum number of entries to print, None = all (default: None)
            print_func: Function to use for printing (default: print)
        
        Examples:
            # Print basic command history
            sender.print_command_history(detail_level=0)
            
            # Print standard history with response details
            sender.print_command_history()
            
            # Print verbose history of the last 5 commands
            sender.print_command_history(detail_level=2, max_entries=5)
        """
        # Set print function
        if print_func is None:
            print_func = print
        
        if not self.command_history:
            print_func("No commands in history.")
            return
        
        # Apply limits
        history = self.command_history
        
        if max_entries and max_entries < len(history):
            history = history[-max_entries:]  # Get the most recent entries
        
        print_func("\n=== Command History ===")
        print_func(f"Total entries: {len(history)} of {len(self.command_history)}")
        print_func("=====================\n")
        
        for i, cmd in enumerate(history):
            # Command header (always shown)
            header = f"Command {i+1}/{len(history)}"
            print_func(f"\n{header}")
            print_func("=" * len(header))
            
            # Common command echo (always printed for all detail levels)
            print_func(f"Command {i+1}: {cmd['command']}")
            
            # Detail level 1+: Show timestamp (standard and verbose)
            if detail_level >= 1:
                from datetime import datetime
                timestamp = datetime.fromtimestamp(cmd['timestamp']).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                print_func(f"Sent at: {timestamp}")
            
            # Detail level 2: Show command kwargs if present (verbose only)
            if detail_level >= 2 and 'kwargs' in cmd:
                kwargs_str = ", ".join(f"{k}={v}" for k, v in cmd['kwargs'].items())
                print_func(f"Command kwargs: {{{kwargs_str}}}")
            
            # Response handling (if present and requested)
            if include_responses and 'response' in cmd:
                resp = cmd['response']
                
                # Detail level 1+: Build telemetry condition string
                if detail_level >= 1 and 'target' in resp:
                    condition_str = f"{resp['target']} {resp['packet']} {resp['item']} {resp.get('comparison', '==')} {resp['comparison_value']}"
                    print_func(f"Telemetry Condition: {condition_str}")
                
                # Common result status (all detail levels)
                result_text = "SUCCESS" if resp.get('success', False) else "FAILED"
                print_func(f"Telemetry Condition Result: {result_text}")
                
                # Detail level 1+: Show detailed timing and error info
                if detail_level >= 1:
                    print_func(f"Result Time: {resp.get('time', 'N/A'):.6f}s")
                    
                    # Detail level 2: Show final telemetry value (verbose only)
                    if detail_level >= 2 and 'value' in resp:
                        print_func(f"Final Telemetry Value: {resp['value']}")
                    
                    # Error message if present
                    if 'error' in resp:
                        print_func(f"Error Message: {resp['error']}")
                    
                    # Timeout if occurred
                    if not resp.get('success', False) and 'timeout' in resp:
                        print_func(f"Telemetry Timeout Occurred at: {resp['timeout']}")
            
            # Requirement handling (if present and requested)
            if include_requirements and 'requirement' in cmd:
                req = cmd['requirement']
                
                # Detail level 1+: Show requirement message
                if detail_level >= 1:
                    print_func(f"Requirements {req['ids']}: {req.get('message', 'No message')}")
                
                # All detail levels: Show Pass/Fail status
                result_text = "Pass" if req.get('success', False) else "Fail"
                print_func(f"Requirements {req['ids']}: {result_text}")
            
            print_func("\n" + "-" * 40)
        
        print_func(f"\nEnd of command history. {len(history)} entries shown.")
    
    
    def set_req_tracker(self, req_tracker: Any) -> None:
        """Set the requirement tracker for this CommandSender instance.
        
        Args:
            req_tracker: RequirementTracker instance to use for requirement tracking
            
        Example:
            from cosmos_test_utils import RequirementTracker
            
            sender = CommandSender()
            tracker = RequirementTracker()
            sender.set_req_tracker(tracker)
        """
        self.req_tracker = req_tracker
