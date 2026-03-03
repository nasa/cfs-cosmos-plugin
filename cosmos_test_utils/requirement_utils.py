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

"""Utilities for dynamically tracking requirement status in COSMOS tests."""

from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

class RequirementTracker:
    """Class for dynamically tracking requirement status and history.
    
    This class maintains a collection of requirements, their states, and
    the history of state transitions. It provides methods to set and query
    requirement states.
    
    Valid requirement states:
    - "U": Untested
    - "P": Passed
    - "F": Failed
    - "I": Needs Inspection
    - "A": Needs Analysis
    - "IA": Needs Inspection/Analysis
    """
    
    def __init__(self):
        """Initialize a new RequirementTracker."""
        # Main data structure for requirements
        self.requirements: Dict[str, Dict[str, Any]] = {}
        # For storing the requirements in order of addition
        self._req_list: List[Dict[str, Any]] = []
        # Debug mode
        self.debug_mode = False
    
    
    def set_requirement(self, requirement_id: str, state: str, message: str) -> Dict[str, str]:
        """Set the state of a requirement.
        
        This method adds a requirement to the tracker if it does not exist, 
        or updates the state of a requirement according to the
        following transition rules:
        1. Cannot move from F to any other state
        2. Cannot move from A, I, or IA to P
        3. Cannot move from IA to I or A
        4. Cannot move any state to U
        5. Moving from I to A or from A to I results in IA
        6. Ignores attempts to set state "U" for existing requirements
        
        Args:
            requirement_id: The unique identifier for the requirement
            state: The target state (U, P, F, I, A, or IA)
            message: A message describing the reason for this state update
            
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
            error_messages.append("*** <!> ALERT: requirement_set: requirement ID not provided")
        
        valid_states = ["U", "P", "F", "I", "A", "IA"]
        if state not in valid_states:
            error_messages.append(f"*** <!> ALERT: requirement_set: requirement state must be one of {', '.join(valid_states)}")
        
        if not message:
            print("\n*** <!> WARNING: requirement_set: message not provided\n")
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
            # Initialize this requirement
            set_state = state
            
            self.requirements[requirement_id] = {
                "state": set_state,
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
                "set_state": set_state,
                "message": message
            }
            self.requirements[requirement_id]["events"].append(event)
            
            state_transition_msg = f"*** <*> Requirement State Initialized ({requirement_id}): Set to {set_state}"
            set_message = self._format_set_message(requirement_id, set_state, message)
        
        else:
            # Update existing requirement
            req = self.requirements[requirement_id]
            prev_state = req["state"]
            attempted_state = state
            set_state = prev_state  # Default to keeping the same state
            transition_message = ""
            
            # Ignore attempts to set state "U" for existing requirements
            if attempted_state == "U":
                return {
                    "result": "success",
                    "message": "Ignored attempt to set state 'U' for existing requirement",
                    "display_message": "",
                    "state_message": "",
                    "set_message": ""
                }
            
            # Apply transition rules
            if (
                prev_state != "F" and
                not (prev_state == "A" and attempted_state == "P") and
                not (prev_state == "I" and attempted_state == "P") and
                not (prev_state == "IA" and attempted_state == "P") and
                not (prev_state == "IA" and attempted_state == "I") and
                not (prev_state == "IA" and attempted_state == "A") and
                attempted_state != "U"
            ):
                # Special case for I->A or A->I
                if ((prev_state == "A" and attempted_state == "I") or 
                    (prev_state == "I" and attempted_state == "A")):
                    set_state = "IA"
                    transition_message = f"State moved from {prev_state} to {set_state}, {attempted_state} was added to the existing state"
                else:
                    set_state = attempted_state
                    transition_message = f"State moved from {prev_state} to {attempted_state}"
                
                state_transition_msg = f"*** <*> Requirement State Changed ({requirement_id}): {transition_message}"
            else:
                # Disallowed transition - state remains unchanged
                transition_message = f"Attempted transition from {prev_state} to {attempted_state}: Transition not allowed"
                state_transition_msg = f"*** <!> ALERT: Requirement State NOT Changed ({requirement_id}): {transition_message}"
            
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
        print(state_transition_msg)
        if set_state != "U":
            print(set_message)
        
        return {
            "result": "success",
            "message": "Requirement state updated",
            "display_message": f"{state_transition_msg}\n{set_message}" if set_state != "U" else state_transition_msg,
            "state_message": state_transition_msg,
            "set_message": set_message
        }
    
    
    def set_multiple_requirements(self, requirement_ids: Union[str, List[str]], state: str, message: str) -> List[Dict[str, str]]:
        """Set the same state for multiple requirements with the same message.
        
        This method calls set_requirement() for each requirement ID in the list.
        
        Args:
            requirement_ids: Either a comma-separated string of requirement IDs or a list of requirement IDs
            state: The target state (U, P, F, I, A, or IA) for all requirements
            message: A message describing the reason for this state update
            
        Returns:
            A list of dictionaries with status information for each requirement
        """
        # Input validation
        if not requirement_ids:
            error_message = "*** <!> ALERT: set_multiple_requirements: requirement IDs not set"
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
                result = self.set_requirement(req_id, state, message)
                results.append(result)
        
        return results
    
    
    def get_requirement(self, requirement_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state and history of a requirement.
        
        Args:
            requirement_id: The unique identifier for the requirement
            
        Returns:
            Dictionary with requirement information or None if not found
        """
        if requirement_id in self.requirements:
            return self.requirements[requirement_id]
        return None
    
    
    def get_all_requirements(self) -> List[Dict[str, Any]]:
        """Get all requirements in order of addition.
        
        Returns:
            List of requirement dictionaries
        """
        return self._req_list.copy()
    
    
    def get_requirements_by_state(self, state: str) -> List[Dict[str, Any]]:
        """Get all requirements with a specific state.
        
        Args:
            state: The state to filter by (U, P, F, I, A, or IA)
            
        Returns:
            List of requirement dictionaries with the specified state
        """
        return [req for req in self._req_list if req["state"] == state]
    
    
    def set_debug_mode(self, enabled: bool = True) -> None:
        """Enable or disable debug mode for reporting.
        
        When debug mode is enabled, detailed event history is shown in reports.
        
        Args:
            enabled: Whether debug mode should be enabled
        """
        self.debug_mode = enabled
    
    
    def generate_requirements_report(self) -> str:
        """Generate a formatted report of all requirements.
        
        The report includes detailed event history if debug_mode is enabled.
        Use set_debug_mode(True) to see detailed event history.
            
        Returns:
            Formatted string with requirement status report
        """
        if not self._req_list:
            return "No requirements have been tracked."
        
        report = []
        report.append("\n==================================================")
        report.append("REQUIREMENT VERIFICATION REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("==================================================\n")
        
        # Count by state
        states = {"U": 0, "P": 0, "F": 0, "I": 0, "A": 0, "IA": 0}
        for req in self._req_list:
            if req["state"] in states:
                states[req["state"]] += 1
        
        # Calculate percentages safely
        total = len(self._req_list)
        percentage = lambda count: (count / total * 100) if total > 0 else 0.0
        
        # Summary
        report.append("SUMMARY:")
        report.append(f"    Total Requirements: {total}")
        report.append(f"                Passed: {states['P']} ({percentage(states['P']):.1f}%)")
        report.append(f"                Failed: {states['F']} ({percentage(states['F']):.1f}%)")
        report.append(f"     Inspection Needed: {states['I']} ({percentage(states['I']):.1f}%)")
        report.append(f"       Analysis Needed: {states['A']} ({percentage(states['A']):.1f}%)")
        report.append(f"Insp & Analysis Needed: {states['IA']} ({percentage(states['IA']):.1f}%)")
        report.append(f"              Untested: {states['U']} ({percentage(states['U']):.1f}%)")
        report.append("")
        
        # Details - Just the requirements list without embedded debug info
        report.append("DETAILS:")
        for req in self._req_list:
            report.append(f"FSW Requirement: {req['requirement_id']:<32} P/F: {req['state']}")
        
        # Add debugging section if debug mode is enabled
        if self.debug_mode:
            report.append("")
            report.append("Requirement Debugging Info:")
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
        """Generate and print a report of requirements and their statuses.
        
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
            print_func("No requirements have been tracked.")
            return
        
        # Report the requirements and their statuses
        for req in self._req_list:
            requirement_id = req["requirement_id"]
            req_state = req["state"]
            print_func(f"FSW Requirement: {requirement_id:<32} P/F: {req_state}")
        
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
                        print_func(f"Requirement Debug: {requirement_id:<30} Event  [{event_index}]:  "
                                  f"Previous: {prev_state:>4},     Attempted: {attempted_state},     "
                                  f"Set: {set_state},     Message: \"{message}\"")
                    else:
                        print_func(f"Requirement Debug: {requirement_id:<30} Event [{event_index}]:  "
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
            state: The requirement state
            message: The message about the requirement
            
        Returns:
            A formatted message string
        """
        if state == "P":
            return f"<*> {requirement_id} Passed: {message}"
        elif state == "F":
            return f"<!> {requirement_id} Failed: {message}"
        elif state == "I":
            return f"<!><I> {requirement_id} needs Inspection: {message}"
        elif state == "A":
            return f"<!><A> {requirement_id} needs Analysis: {message}"
        elif state == "IA":
            return f"<!><IA> {requirement_id} needs Inspection/Analysis: {message}"
        else:
            return ""  # For "U" state