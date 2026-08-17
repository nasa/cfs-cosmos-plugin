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

"""Utilities for dynamically tracking requirement status in COSMOS tests."""

from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

class RequirementTracker:
    """Class for dynamically tracking requirement status and history.
    
    This class maintains a collection of requirements, their states, and
    the history of state transitions. It provides methods to set and query
    requirement states.
    
    Valid requirement state codes:
    - "U" or "UNTESTED": Untested
    - "P" or "PASS": Passed
    - "F" or "FAIL": Failed
    - "I" or "INSPECT": Needs Inspection
    - "A" or "ANALYSIS": Needs Analysis
    - "IA" or "INSPECT/ANALYSIS": Needs Inspection/Analysis
    """
    
    # Class-level state mappings for consistency across all methods
    STATE_TO_LONG = {
        "U": "UNTESTED",
        "P": "PASS",
        "F": "FAIL",
        "I": "INSPECT",
        "A": "ANALYSIS",
        "IA": "INSPECT/ANALYSIS"
    }
    
    LONG_TO_STATE = {
        "UNTESTED": "U",
        "PASS": "P",
        "FAIL": "F",
        "INSPECT": "I",
        "ANALYSIS": "A",
        "INSPECT/ANALYSIS": "IA"
    }
    
    def __init__(self, label: str = "Requirement"):
        """Initialize a new RequirementTracker.
        
        Args:
            label: The label to use for tracked items in display output (default: "Requirement").
                   This only affects display strings, not internal variable names or functionality.
                   Example: "Test", "Objective", "Criterion", etc.
        """
        # Main data structure for requirements
        self.requirements: Dict[str, Dict[str, Any]] = {}
        # For storing the requirements in order of addition
        self._req_list: List[Dict[str, Any]] = []
        # Debug mode
        self.debug_mode = False
        # Display label for tracked items
        self.label = label
    
    
    def _normalize_state(self, state: str) -> str:
        """
        Normalize a state to its short code form.
        
        Accepts both short codes (U, P, F, I, A, IA) and long form names
        (UNTESTED, PASS, FAIL, INSPECT, ANALYSIS, INSPECT/ANALYSIS).
        
        Args:
            state: The state in either short or long form
            
        Returns:
            The short code version of the state
            
        Raises:
            ValueError: If state is not a valid short code or long form name
        """
        state_upper = state.upper()
        
        # Check if it's already a short code
        if state_upper in self.STATE_TO_LONG:
            return state_upper
        
        # Check if it's a long form name
        if state_upper in self.LONG_TO_STATE:
            return self.LONG_TO_STATE[state_upper]
        
        # Not valid
        valid_options = list(self.STATE_TO_LONG.keys()) + list(self.LONG_TO_STATE.keys())
        raise ValueError(f"Invalid state '{state}'. Must be one of: {', '.join(valid_options)}")
    
    
    def set_requirement(self, requirement_id: str, state: str, message: str, silent: bool = False) -> Dict[str, str]:
        """
        Set the state of a requirement.
        
        This method adds a requirement to the tracker if it does not exist, 
        or updates the state of a requirement according to the
        following transition rules:
        1. Cannot move from FAIL to any other state
        2. Cannot move from ANALYSIS, INSPECT, or INSPECT/ANALYSIS to PASS
        3. Cannot move from INSPECT/ANALYSIS to INSPECT or ANALYSIS
        4. Cannot move any state to UNTESTED
        5. Moving from INSPECT to ANALYSIS or from ANALYSIS to INSPECT results in INSPECT/ANALYSIS
        6. Ignores attempts to set state "U"/"UNTESTED" for existing requirements
        
        Args:
            requirement_id: The unique identifier for the requirement
            state: The target state - accepts both short codes (U, P, F, I, A, IA) 
                   and long form names (UNTESTED, PASS, FAIL, INSPECT, ANALYSIS, INSPECT/ANALYSIS)
            message: A message describing the reason for this state update
            silent: If True, suppresses printing of the state transition and set messages
                    to the console/log. The returned dictionary still contains the messages
                    for callers who want to handle them manually. Useful for reducing log
                    noise. Defaults to False.
            
        Returns:
            A dictionary with status information about the operation:
            {
                "result": "success" or "error",
                "message": Description of the result,
                "display_message": Formatted message for display,
                "state_message": State transition message,
                "set_message": Current state message
            }
        """
        # Validate inputs
        error_messages = []
        
        if not requirement_id:
            error_messages.append("*** <!> CTU ALERT: requirement_set: requirement ID not provided")
        
        # Normalize and validate state
        try:
            state = self._normalize_state(state)
        except ValueError as e:
            error_messages.append(f"*** <!> CTU ALERT: requirement_set: {str(e)}")
        
        if not message:
            print("\n*** <!> CTU WARNING: requirement_set: message not provided\n")
            message = "[No message set]"
        
        # Exit on error
        if error_messages:
            for error in error_messages:
                print(error)
            return {
                "result": "error",
                "message": "\n".join(error_messages),
                "display_message": "\n".join(error_messages),
                "state_message": "",
                "set_message": ""
            }
        
        # Check if this is the first time setting this requirement
        if requirement_id not in self.requirements:
            # Initialize this requirement with full state name
            set_state_long = self.STATE_TO_LONG[state]
            set_state = set_state_long
            
            self.requirements[requirement_id] = {
                "state": set_state_long,
                "requirement_id": requirement_id,
                "events": [],
                "index": len(self._req_list)
            }
            
            self._req_list.append(self.requirements[requirement_id])
            
            # Add the first event
            event = {
                "timestamp": datetime.now().isoformat(),
                "prev_state": "none",
                "attempted_state": state,
                "set_state": set_state_long,
                "message": message
            }
            self.requirements[requirement_id]["events"].append(event)
            
            state_transition_msg = f"*** <*> CTU {self.label} State Initialized ({requirement_id}): Set to {set_state_long}"
            set_message = self._format_set_message(requirement_id, set_state_long, message)
        
        else:
            # Update existing requirement
            req = self.requirements[requirement_id]
            prev_state = req["state"]
            attempted_state = state
            set_state = prev_state  # Default to keeping the same state
            transition_message = ""
            
            # Ignore attempts to set state "U" (UNTESTED) for existing requirements
            if attempted_state == "U":
                return {
                    "result": "success",
                    "message": f"Ignored attempt to set state 'U' for existing {self.label.lower()}",
                    "display_message": "",
                    "state_message": "",
                    "set_message": ""
                }
            
            # Apply transition rules (comparing against stored state names)
            if (
                prev_state != "FAIL" and
                not (prev_state == "ANALYSIS" and attempted_state == "P") and
                not (prev_state == "INSPECT" and attempted_state == "P") and
                not (prev_state == "INSPECT/ANALYSIS" and attempted_state == "P") and
                not (prev_state == "INSPECT/ANALYSIS" and attempted_state == "I") and
                not (prev_state == "INSPECT/ANALYSIS" and attempted_state == "A") and
                attempted_state != "U"
            ):
                # Special case for INSPECT->ANALYSIS or ANALYSIS->INSPECT
                if ((prev_state == "ANALYSIS" and attempted_state == "I") or 
                    (prev_state == "INSPECT" and attempted_state == "A")):
                    set_state = "INSPECT/ANALYSIS"
                    attempted_state_long = self.STATE_TO_LONG[attempted_state]
                    transition_message = f"State moved from {prev_state} to {set_state}, {attempted_state_long} was added to the existing state"
                else:
                    set_state = self.STATE_TO_LONG[attempted_state]
                    transition_message = f"State moved from {prev_state} to {set_state}"
                
                state_transition_msg = f"*** <*> CTU: {self.label} State Changed ({requirement_id}): {transition_message}"
            else:
                # Disallowed transition - state remains unchanged
                attempted_state_long = self.STATE_TO_LONG[attempted_state]
                transition_message = f"Attempted transition from {prev_state} to {attempted_state_long}: Transition not allowed"
                state_transition_msg = f"*** <!> CTU ALERT: {self.label} State NOT Changed ({requirement_id}): {transition_message}"
            
            # Update requirement state
            req["state"] = set_state
            
            # Add new event
            event = {
                "timestamp": datetime.now().isoformat(),
                "prev_state": prev_state,
                "attempted_state": attempted_state,
                "set_state": set_state,
                "message": message
            }
            req["events"].append(event)
            
            set_message = self._format_set_message(requirement_id, set_state, message)
        
        # Display messages
        if not silent:
            print(state_transition_msg)
            if set_state != "UNTESTED":
                print(set_message)
        
        return {
            "result": "success",
            "message": f"{self.label} state updated",
            "display_message": f"{state_transition_msg}\n{set_message}" if set_state != "UNTESTED" else state_transition_msg,
            "state_message": state_transition_msg,
            "set_message": set_message
        }
    
    
    def set_multiple_requirements(self, requirement_ids: Union[str, List[str]], state: str, message: str, silent: bool = False) -> List[Dict[str, str]]:
        """
        Set the same state for multiple requirements with the same message.
        
        This method calls set_requirement() for each requirement ID in the list.
        
        Args:
            requirement_ids: Either a comma-separated string of requirement IDs or a list of requirement IDs
            state: The target state - accepts both short codes (U, P, F, I, A, IA) 
                   and long form names (UNTESTED, PASS, FAIL, INSPECT, ANALYSIS, INSPECT/ANALYSIS)
            message: A message describing the reason for this state update
            silent: If True, suppresses printing of the state transition and set messages
                    for each requirement. Defaults to False.
            
        Returns:
            A list of dictionaries with status information for each requirement
        """
        # Input validation
        if not requirement_ids:
            error_message = "*** <!> CTU ALERT: set_multiple_requirements: requirement IDs not set"
            print(f"\n{error_message}\n")
            return [{"result": "error", "message": error_message}]
        
        # Convert string to list if needed
        if isinstance(requirement_ids, str):
            # Split on commas and remove any spaces
            req_list = [req_id.strip() for req_id in requirement_ids.split(',')]
        else:
            req_list = requirement_ids
        
        # Call set_requirement for each requirement ID
        results = []
        for req_id in req_list:
            if req_id:  # Skip empty strings
                result = self.set_requirement(req_id, state, message, silent=silent)
                results.append(result)
        
        return results
    
    
    def get_requirement(self, requirement_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state and history of a requirement.
        
        Args:
            requirement_id: The unique identifier for the requirement
            
        Returns:
            Dictionary with requirement information or None if not found
        """
        if requirement_id in self.requirements:
            return self.requirements[requirement_id]
        return None
    
    
    def get_all_requirements(self) -> List[Dict[str, Any]]:
        """
        Get all requirements in order of addition.
        
        Returns:
            List of requirement dictionaries
        """
        return self._req_list.copy()
    
    
    def get_requirements_by_state(self, state: str) -> List[Dict[str, Any]]:
        """
        Get all requirements with a specific state.
        
        Args:
            state: The state to filter by - accepts both short codes (U, P, F, I, A, IA)
                   and long form names (UNTESTED, PASS, FAIL, INSPECT, ANALYSIS, INSPECT/ANALYSIS)
            
        Returns:
            List of requirement dictionaries with the specified state
        """
        # Normalize state to long form for comparison
        try:
            state_normalized = self._normalize_state(state)
            search_state = self.STATE_TO_LONG[state_normalized]
        except ValueError:
            # Invalid state, return empty list
            return []
        
        return [req for req in self._req_list if req["state"] == search_state]
    
    
    def set_debug_mode(self, enabled: bool = True) -> None:
        """
        Enable or disable debug mode for reporting.
        
        When debug mode is enabled, detailed event history is shown in reports.
        
        Args:
            enabled: Whether debug mode should be enabled
        """
        self.debug_mode = enabled
    
    
    def generate_requirements_report(self) -> str:
        """
        Generate a formatted report of all requirements.
        
        The report includes detailed event history if debug_mode is enabled.
        Use set_debug_mode(True) to see detailed event history.
            
        Returns:
            Formatted string with requirement status report
        """
        if not self._req_list:
            return f"<!> CTU generate_requirements_report: No {self.label.lower()}s have been tracked."
        
        label_upper = self.label.upper()
        label_plural = f"{self.label}s"
        
        report = []
        report.append("\n==================================================")
        report.append(f"{label_upper} VERIFICATION REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("==================================================\n")
        
        # Count by state
        states = {"UNTESTED": 0, "PASS": 0, "FAIL": 0, "INSPECT": 0, "ANALYSIS": 0, "INSPECT/ANALYSIS": 0}
        for req in self._req_list:
            if req["state"] in states:
                states[req["state"]] += 1
        
        # Calculate percentages safely
        total = len(self._req_list)
        percentage = lambda count: (count / total * 100) if total > 0 else 0.0
        
        # Summary
        report.append("SUMMARY:")
        report.append(f"Total {label_plural}: {total}")
        report.append(f"                Passed: {states['PASS']} ({percentage(states['PASS']):.1f}%)")
        report.append(f"                Failed: {states['FAIL']} ({percentage(states['FAIL']):.1f}%)")
        report.append(f"     Inspection Needed: {states['INSPECT']} ({percentage(states['INSPECT']):.1f}%)")
        report.append(f"       Analysis Needed: {states['ANALYSIS']} ({percentage(states['ANALYSIS']):.1f}%)")
        report.append(f"Insp & Analysis Needed: {states['INSPECT/ANALYSIS']} ({percentage(states['INSPECT/ANALYSIS']):.1f}%)")
        report.append(f"              Untested: {states['UNTESTED']} ({percentage(states['UNTESTED']):.1f}%)")
        report.append("")
        
        # Details - Just the requirements list without embedded debug info
        report.append("DETAILS:")
        for req in self._req_list:
            report.append(f"FSW {label_upper}: {req['requirement_id']:<32} P/F Status: {req['state']}")
        
        # Add debugging section if debug mode is enabled
        if self.debug_mode:
            report.append("")
            report.append(f"{self.label} Debugging Info:")
            report.append("")
            
            for req in self._req_list:
                if req["events"]:
                    report.append(f"{req['requirement_id']}:")
                    report.append("  Events:")
                    for i, event in enumerate(req["events"]):
                        report.append(f"    {i+1}. {event['timestamp']}")
                        if event['prev_state'] != "none":
                            report.append(f"       State: {event['prev_state']} -> {event['set_state']}")
                            if event['attempted_state'] != event['set_state']:
                                report.append(f"       (Attempted: {event['attempted_state']})")
                        else:
                            report.append(f"       Initial State: {event['set_state']}")
                        report.append(f"       Message: {event['message']}")
                        report.append("")
        
        return "\n".join(report)    
    
    
    def requirements_report(self, print_func: Optional[Callable] = None) -> None:
        """
        Generate and print a report of requirements and their statuses.
        
        This method prints a report of requirements and their statuses directly.
        It produced details history of requirement state changes if debug_mode is True.
        
        Args:
            print_func: Function to use for printing (default: test_print)
        """
        # Set up print function with test_print as default
        if print_func is None:
            from .print_utils import test_print
            print_func = test_print
        
        if not self._req_list:
            print_func(f"<!> CTU requirements_report: No {self.label.lower()}s have been tracked.")
            return
        
        label_upper = self.label.upper()
        
        # Report the requirements and their statuses
        for req in self._req_list:
            requirement_id = req["requirement_id"]
            req_state = req["state"]
            print_func(f"FSW {label_upper}: {requirement_id:<32} P/F Status: {req_state}")
        
        # Report the requirement set debug info if debug mode is enabled
        if self.debug_mode:
            for req in self._req_list:
                requirement_id = req["requirement_id"]
                for event_index, event in enumerate(req["events"]):
                    prev_state = event["prev_state"]
                    attempted_state = event["attempted_state"]
                    set_state = event["set_state"]
                    message = event["message"]
                    
                    # Format the output consistently
                    if event_index < 10:
                        print_func(f"{self.label} Debug: {requirement_id:<30} Event  [{event_index}]:  "
                                  f"Previous: {prev_state:>4},     Attempted: {attempted_state},     "
                                  f"Set: {set_state},     Message: \"{message}\"")
                    else:
                        print_func(f"{self.label} Debug: {requirement_id:<30} Event [{event_index}]:  "
                                  f"Previous: {prev_state:>4},     Attempted: {attempted_state},     "
                                  f"Set: {set_state},     Message: \"{message}\"")
    
    
    def reset(self) -> None:
        """Reset the requirement tracker, clearing all data."""
        self.requirements = {}
        self._req_list = []
        self.debug_mode = False
    
    
    def _format_set_message(self, requirement_id: str, state: str, message: str) -> str:
        """Format a message about the requirement state.
        
        Args:
            requirement_id: The requirement ID
            state: The requirement state (long form name)
            message: The message about the requirement
            
        Returns:
            A formatted message string
        """
        if state == "PASS":
            return f"<*> {requirement_id} Passed: {message}"
        elif state == "FAIL":
            return f"<!> {requirement_id} Failed: {message}"
        elif state == "INSPECT":
            return f"<!><I> {requirement_id} needs Inspection: {message}"
        elif state == "ANALYSIS":
            return f"<!><A> {requirement_id} needs Analysis: {message}"
        elif state == "INSPECT/ANALYSIS":
            return f"<!><IA> {requirement_id} needs Inspection/Analysis: {message}"
        else:
            return ""  # For "UNTESTED" state