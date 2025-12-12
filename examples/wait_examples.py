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

"""
Examples showing how to use the wait utilities for waiting on telemetry conditions.

Note: This example uses mock functions since it can't connect to a real COSMOS system.
"""

from cosmos_test_utils import (
    wait_for_telemetry_value,
    wait_for_telemetry_expression,
    wait_for_telemetry_change,
    wait_for_sequence_count_change,
    wait_check_telemetry,
    wait_for_telemetry_in_range,
    wait_for_telemetry_in_timing_range,
    wait_multiple_telemetry
)

def main():
    print("EXAMPLE: Wait Utilities")
    print("=====================")
    
    # Set up mock functions
    setup_mock_functions()
    
    print("\n1. Basic telemetry value waiting")
    print("Waiting for telemetry value...")
    success = wait_for_telemetry_value(
        "SPACECRAFT", "HEALTH_TLM", "BATTERY", "==", 100,
        timeout=5.0  # This would normally wait 5 seconds, but our mock returns immediately
    )
    print(f"Wait result: {'Success' if success else 'Timeout'}")
    
    print("\n2. Waiting with custom comparison")
    print("Waiting for telemetry value to be greater than threshold...")
    success = wait_for_telemetry_value(
        "SPACECRAFT", "HEALTH_TLM", "TEMPERATURE", ">", 20, # Use greater-than comparison
        timeout=5.0
    )
    print(f"Wait result: {'Success' if success else 'Timeout'}")
    
    print("\n3. Waiting for telemetry change")
    print("Waiting for sequence counter to change...")
    success = wait_for_telemetry_change(
        "SPACECRAFT", "HEALTH_TLM", "COUNTER",
        timeout=5.0
    )
    print(f"Wait result: {'Success' if success else 'Timeout'}")
    
    print("\n4. Waiting for sequence counter")
    print("Waiting for 3 new packets...")
    success = wait_for_sequence_count_change(
        "SPACECRAFT", "HEALTH_TLM", 
        count=3,  # Wait for 3 new packets
        timeout=5.0
    )
    print(f"Wait result: {'Success' if success else 'Timeout'}")
    
    print("\n5. Wait and check telemetry")
    print("Waiting and checking telemetry...")
    success, value = wait_check_telemetry(
        "SPACECRAFT", "HEALTH_TLM", "MODE", "==", "SCIENCE",
        timeout=5.0
    )
    print(f"Wait result: {'Success' if success else 'Timeout'}")
    print(f"Final value: {value}")
    
    print("\n6. Wait for value in range")
    print("Waiting for value in range 75-100...")
    success = wait_for_telemetry_in_range(
        "SPACECRAFT", "HEALTH_TLM", "BATTERY", 
        min_value=75, max_value=100,
        timeout=5.0
    )
    print(f"Wait result: {'Success' if success else 'Timeout'}")
    
    print("\n7. Wait for multiple conditions")
    print("Waiting for multiple telemetry conditions...")
    conditions = [
        {
            'target': 'SPACECRAFT',
            'packet': 'HEALTH_TLM',
            'item': 'MODE',
            'value': 'SCIENCE',
            'name': 'science_mode'
        },
        {
            'target': 'SPACECRAFT',
            'packet': 'HEALTH_TLM',
            'item': 'BATTERY',
            'value': 90,
            'comparison': '>',
            'name': 'battery_good'
        }
    ]
    
    # Quick success check:
    overall_success, results = wait_multiple_telemetry(conditions)
    if overall_success:
        print("All good!")
    else:
        print("Something failed - need to investigate")    
    
    # detailed analysis based on overall fialure:
    overall_success, results = wait_multiple_telemetry(conditions)
    if not overall_success:
        failed_conditions = [name for name, success in results.items() if not success]
        print(f"Failed conditions: {failed_conditions}")
        
    # checking every return:
    _, results = wait_multiple_telemetry(conditions, timeout=5.0)
    print("Results:")
    for name, result in results.items():
        print(f"  {name}: {'Success' if result else 'Failed'}")
    
    # One-liner success check (do not care about detailed results)
    success, _ = wait_multiple_telemetry(conditions)  # Ignore detailed results
    if success:
        print("All good!")
    
    # Mock requirement tracker
    class MockReqTracker:
        def set_requirement(self, req_id, state, message):
            print(f"Setting requirement {req_id} to {state}: {message}")
            
    req_tracker = MockReqTracker()
    
    # This would normally be used with actual command and telemetry,
    # but we're using mocks for the example
    success, response_time = wait_for_telemetry_in_timing_range(
        "SPACECRAFT", "HEALTH_TLM", "MODE", "==", "SCIENCE",
        min_time=0.5,
        max_time=2.0,
        timeout=3.0,
        requirement_id="REQ-123",
        req_tracker=req_tracker
    )
    
    print(f"Requirement verification: {'Passed' if success else 'Failed'}")
    print(f"Response time: {response_time:.3f} seconds")
    
    print("\nExample complete!")

def setup_mock_functions():
    """Set up mock functions for this example."""
    
    # Create a mock get_tlm function that returns test values
    mock_tlm_values = {
        "SPACECRAFT HEALTH_TLM BATTERY": 95,
        "SPACECRAFT HEALTH_TLM TEMPERATURE": 25,
        "SPACECRAFT HEALTH_TLM COUNTER": 42,
        "SPACECRAFT HEALTH_TLM MODE": "SCIENCE",
        "SPACECRAFT HEALTH_TLM CCSDS_SEQUENCE": 123
    }
    
    def mock_get_tlm(tlm_string):
        return mock_tlm_values.get(tlm_string, 0)
    
    # Apply mocks to all wait functions
    for func_name in [
        'wait_for_telemetry_value',
        'wait_for_telemetry_expression',
        'wait_for_telemetry_change',
        'wait_for_sequence_count_change',
        'wait_check_telemetry',
        'wait_for_telemetry_in_range',
        'wait_multiple_telemetry'
    ]:
        # Get the real function
        real_func = globals()[func_name]
        
        # Create a wrapper that injects our mock
        def make_wrapper(f):
            def wrapper(*args, **kwargs):
                kwargs['get_tlm_func'] = mock_get_tlm
                # For demonstration purposes, make all functions return success
                if func_name == 'wait_check_telemetry':
                    return True, mock_get_tlm(f"{args[0]} {args[1]} {args[2]}")
                elif func_name == 'wait_multiple_telemetry':
                    return {cond.get('name', i): True for i, cond in enumerate(args[0])}
                else:
                    return True
            return wrapper
        
        # Replace the global function with our wrapper
        globals()[func_name] = make_wrapper(real_func)


if __name__ == "__main__":
    main()