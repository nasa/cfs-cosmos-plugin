# NASA Docket No. GSC-19606-1, and identified as Test Utilities Python
# package to facilitate testing software with the open source COSMOS
# ground system
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

"""Utilities for tracking and verifying timing requirements in COSMOS tests."""

import time
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from .system_config import DEFAULT_WAIT_TIMEOUT, DEFAULT_POLL_INTERVAL

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

class TimingTracker:
    """Class for tracking multiple timing events and measurements."""
    
    def __init__(self, high_precision: bool = False):
        """
        Initialize a timing tracker.
        
        Args:
            high_precision: If True, use high precision time.perf_counter() instead of time.time()
                           for more accurate measurements (but without absolute timestamps)
        """
        self._time_func = time.perf_counter if high_precision else time.time
        self._start_times: Dict[str, float] = {}
        self._stop_times: Dict[str, float] = {}
        self._elapsed_times: Dict[str, float] = {}
        self._running: List[str] = []
    
    
    def start(self, name: str = "default") -> float:
        """
        Start timing a named event.
        
        Args:
            name: Name for this timing event
            
        Returns:
            The start time value
        """
        start_time = self._time_func()
        self._start_times[name] = start_time
        if name not in self._running:
            self._running.append(name)
        return start_time
    
    
    def stop(self, name: str = "default") -> float:
        """
        Stop timing a named event and calculate the elapsed time.
        
        Args:
            name: Name for this timing event
            
        Returns:
            The elapsed time in seconds
            
        Raises:
            ValueError: If the named timer hasn't been started
        """
        if name not in self._start_times:
            raise ValueError(f"<!> CTU TimingTracker.stop: Timer '{name}' has not been started")
        
        stop_time = self._time_func()
        self._stop_times[name] = stop_time
        
        elapsed = stop_time - self._start_times[name]
        self._elapsed_times[name] = elapsed
        
        if name in self._running:
            self._running.remove(name)
            
        return elapsed
    
    
    def elapsed(self, name: str = "default") -> float:
        """
        Get the current elapsed time for a named event.
        
        If the timer is still running, this calculates the elapsed time so far.
        If the timer has been stopped, this returns the final elapsed time.
        
        Args:
            name: Name for this timing event
            
        Returns:
            The elapsed time in seconds
            
        Raises:
            ValueError: If the named timer hasn't been started
        """
        if name not in self._start_times:
            raise ValueError(f"<!> CTU TimingTracker.elapsed: Timer '{name}' has not been started")
        
        if name in self._running:
            # Timer is still running, calculate current elapsed time
            return self._time_func() - self._start_times[name]
        else:
            # Timer has been stopped, return the stored elapsed time
            return self._elapsed_times[name]
    
    
    def verify_timing(self, name: str, min_time: Optional[float] = None, 
                     max_time: Optional[float] = None) -> Tuple[bool, float, str]:
        """
        Verify that a timing event meets the specified constraints.
        
        Args:
            name: Name for this timing event
            min_time: Minimum acceptable time in seconds (None for no minimum)
            max_time: Maximum acceptable time in seconds (None for no maximum)
            
        Returns:
            Tuple containing:
              - bool: True if timing constraints were met
              - float: The elapsed time
              - str: A message describing the result
              
        Raises:
            ValueError: If the named timer hasn't been started
        """
        elapsed = self.elapsed(name)
        
        # Check constraints
        if min_time is not None and max_time is not None:
            # Both constraints specified
            if min_time <= elapsed <= max_time:
                result = True
                message = f"<*> CTU: Timing '{name}' is within range: {elapsed:.6f}s (required: {min_time:.6f}s to {max_time:.6f}s)"
            else:
                result = False
                if elapsed < min_time:
                    message = f"<!> CTU: Timing '{name}' too fast: {elapsed:.6f}s (minimum: {min_time:.6f}s)"
                else:
                    message = f"<!> CTU: Timing '{name}' too slow: {elapsed:.6f}s (maximum: {max_time:.6f}s)"
                    
        elif min_time is not None:
            # Only minimum specified
            if elapsed >= min_time:
                result = True
                message = f"<*> CTU: Timing '{name}' meets minimum: {elapsed:.6f}s (required: >= {min_time:.6f}s)"
            else:
                result = False
                message = f"<!> CTU: Timing '{name}' too fast: {elapsed:.6f}s (minimum: {min_time:.6f}s)"
                
        elif max_time is not None:
            # Only maximum specified
            if elapsed <= max_time:
                result = True
                message = f"<*> CTU: Timing '{name}' meets maximum: {elapsed:.6f}s (required: <= {max_time:.6f}s)"
            else:
                result = False
                message = f"<!> CTU: Timing '{name}' too slow: {elapsed:.6f}s (maximum: {max_time:.6f}s)"
                
        else:
            # No constraints specified
            result = True
            message = f"<*> CTU: Timing '{name}' elapsed time: {elapsed:.6f}s"
            
        return result, elapsed, message
    
    
    def verify_timing_requirement(
        self,
        requirement_ids: Union[str, List[str]],
        name: str,
        min_time: Optional[float] = None, 
        max_time: Optional[float] = None,
        req_tracker: Optional[Any] = None,
        print_func: Optional[Callable] = None
    ) -> Tuple[bool, float, str]:
        """
        Verify that a timing event meets timing requirements and update requirement status.
        
        Args:
            requirement_ids: Comma-separated string or list of requirement IDs to update
            name: Name for this timing event
            min_time: Minimum acceptable time in seconds (None for no minimum)
            max_time: Maximum acceptable time in seconds (None if timeout is the maximum)
            req_tracker: RequirementTracker instance to use (required for requirement updates)
            print_func: Function to use for printing status messages (default: test_print)
            
        Returns:
            Tuple containing:
              - bool: True if timing constraints were met
              - float: The elapsed time
              - str: A message describing the result
              
        Raises:
            ValueError: If the named timer hasn't been started
        """
        # Use test_print as the default print function if none provided
        if print_func is None:
            from .print_utils import test_print
            print_func = print_func if print_func else test_print
        
        # Check if we have a requirement tracker
        if req_tracker is None:
            print_func("<!> CTU verify_timing_requirement Warning: No requirement tracker provided. Cannot update requirement status. "
                       "Pass a RequirementTracker instance to req_tracker parameter.")
        
        # Verify timing constraints
        success, elapsed, message = self.verify_timing(name, min_time, max_time)
        
        # Format a message for the requirement
        if min_time is not None and max_time is not None:
            req_message = f"Timing '{name}' measured at {elapsed:.6f}s (required: {min_time:.6f}s to {max_time:.6f}s)"
        elif min_time is not None:
            req_message = f"Timing '{name}' measured at {elapsed:.6f}s (required: >= {min_time:.6f}s)"
        elif max_time is not None:
            req_message = f"Timing '{name}' measured at {elapsed:.6f}s (required: <= {max_time:.6f}s)"
        else:
            req_message = f"Timing '{name}' measured at {elapsed:.6f}s (no specific timing requirement)"
        
        # Update the requirements if tracker is available
        if req_tracker is not None:
            if success:
                req_tracker.set_multiple_requirements(requirement_ids, "P", req_message)
            else:
                req_tracker.set_multiple_requirements(requirement_ids, "F", req_message)
        else:
            # Print result only if no requirement tracker (to avoid redundant messages)
            print_func(f"{"<*>" if success else "<!>"} CTU: {req_message}")
        
        return success, elapsed, message
    
    
    def reset(self, name: Optional[str] = None) -> None:
        """
        Reset timers.
        
        Args:
            name: Name of the timer to reset, or None to reset all timers
        """
        if name is None:
            # Reset all timers
            self._start_times = {}
            self._stop_times = {}
            self._elapsed_times = {}
            self._running = []
        else:
            # Reset only the specified timer
            if name in self._start_times:
                del self._start_times[name]
            if name in self._stop_times:
                del self._stop_times[name]
            if name in self._elapsed_times:
                del self._elapsed_times[name]
            if name in self._running:
                self._running.remove(name)
    
    
    def get_all_timings(self) -> Dict[str, Dict[str, Union[float, bool]]]:
        """
        Get information about all tracked timings.
        
        Returns:
            Dictionary mapping timer names to dictionaries containing:
              - start_time: The start time
              - stop_time: The stop time (or None if still running)
              - elapsed: The elapsed time (current if running, final if stopped)
              - running: Whether the timer is still running
        """
        results = {}
        for name in set(self._start_times.keys()):
            results[name] = {
                "start_time": self._start_times.get(name),
                "stop_time": self._stop_times.get(name),
                "elapsed": self.elapsed(name),
                "running": name in self._running
            }
        return results
    
    
    def report(self, print_func: Optional[Callable] = None) -> None:
        """
        Generate a report of all timings.
        
        Args:
            print_func: Function to use for printing (default: test_print)
        """
        # Use test_print as the default print function if none provided
        if print_func is None:
            from .print_utils import test_print
            print_func = test_print
            
        all_timings = self.get_all_timings()
        
        if not all_timings:
            print_func("<!> CTU TimingTracker.report: No timings recorded to report")
            return
            
        print_func("\n----- Timing Report -----")
        for name, info in all_timings.items():
            status = "RUNNING" if info["running"] else "STOPPED"
            print_func(f"Timer '{name}': {info['elapsed']:.6f}s ({status})")
        print_func("------------------------\n")


def measure_command_response_time(
    command_func: Callable,
    check_func: Callable[[], bool],
    timeout: float = DEFAULT_WAIT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    print_func: Optional[Callable] = None
) -> Tuple[bool, float]:
    """
    Measure the time between sending a command and receiving a response.
    
    Args:
        command_func: Function to call to send the command (should be parameterless)
        check_func: Function that returns True when response is received
        timeout: Maximum wait time in seconds (default from system_config)
        poll_interval: Time between checks in seconds (default from system_config)
        print_func: Function to use for printing status/debug info (default: test_print)
        
    Returns:
        Tuple containing:
          - bool: True if response was received, False if timeout
          - float: Response time in seconds, or timeout value if timed out
          
    Examples:
        # Basic example with simple functions
        def send_cmd():
            cmd("TARGET COMMAND with ARG1 5")
            
        def check_response():
            return tlm("TARGET PACKET RESPONSE") == "COMPLETE"
            
        success, response_time = measure_command_response_time(send_cmd, check_response)
        
        # Using lambda functions with COSMOS cmd() and tlm()
        success, response_time = measure_command_response_time(
            lambda: cmd("SPACECRAFT POWER_ON with COMPONENT RADIO"),
            lambda: tlm("SPACECRAFT POWER_TLM RADIO_STATE") == "ON"
        )
        
        # Using lambda with wait_for_telemetry_value from wait_utils
        from cosmos_test_utils.wait_utils import wait_for_telemetry_value
        
        success, response_time = measure_command_response_time(
            lambda: cmd("SPACECRAFT SET_MODE with MODE 'SCIENCE'"),
            lambda: wait_for_telemetry_value(
                "SPACECRAFT", "HK_TLM", "MODE", "==", "SCIENCE", 
                timeout=5.0  # Short timeout for the check function
            )
        )
    """
    # Use test_print as the default print function if none provided
    if print_func is None:
        from .print_utils import test_print
        print_func = test_print
        
    # Start timing
    start_time = time.perf_counter()
    
    # Send the command
    command_func()
    
    # Wait for response
    end_time = start_time + timeout
    while time.perf_counter() < end_time:
        if check_func():
            # Response received
            response_time = time.perf_counter() - start_time
            print_func(f"<*> CTU: Command Response received in {response_time:.6f} seconds")
            return True, response_time
        time.sleep(poll_interval)
    
    # Timeout
    print_func(f"<!> CTU: Timeout after {timeout} seconds waiting for command response")
    return False, timeout
