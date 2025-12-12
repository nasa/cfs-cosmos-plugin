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
Examples of using the telemetry utilities in the cosmos_test_utils package.

This file demonstrates various ways to track, analyze, and report telemetry
changes using the telemetry_utils module.
"""

from cosmos_test_utils import (
    report_telemetry,                    # Changed from report_telemetry_changes
    report_all_telemetry,               # Changed from report_all_telemetry_changes
    report_all_targets_telemetry        # Changed from report_all_targets_telemetry_changes
)

def main():
    """Run the telemetry examples."""
    print("\n===== TELEMETRY UTILITIES EXAMPLES =====\n")
    
    # Example 1: Basic telemetry change reporting
    print("\nEXAMPLE 1: Basic Telemetry Change Reporting")
    print("------------------------------------------")
    basic_telemetry_example()
    
    # Example 2: Multiple packet monitoring
    print("\nEXAMPLE 2: Multiple Packet Monitoring")
    print("-----------------------------------")
    multiple_packet_example()
    
    # Example 3: System-wide telemetry reporting
    print("\nEXAMPLE 3: System-wide Telemetry Reporting")
    print("-----------------------------------------")
    system_wide_example()
    
    # Example 4: Custom telemetry change detection
    print("\nEXAMPLE 4: Custom Telemetry Change Detection")
    print("------------------------------------------")
    custom_detection_example()
    
    print("\n===== END OF TELEMETRY EXAMPLES =====")

def basic_telemetry_example():
    """Demonstrate basic telemetry reporting for a single packet."""
    # Note: In an actual COSMOS environment, these would show real telemetry
    
    print("Let's report the current state of a telemetry packet:")
    # This will capture the current state and show it as "initial"
    report_telemetry("SPACECRAFT", "HEALTH_TLM")
    
    print("\nNow let's simulate some spacecraft operations...")
    # In a real script, commands would be sent here to change telemetry
    
    print("\nNow we'll report changes to the telemetry:")
    # This will show what telemetry values changed since the last report
    report_telemetry("SPACECRAFT", "HEALTH_TLM")
    
    print("\nWe can also show all telemetry values, not just changes:")
    # Level 1 shows all values, not just changes
    report_telemetry("SPACECRAFT", "HEALTH_TLM", level_of_detail=1)

def multiple_packet_example():
    """Demonstrate monitoring multiple telemetry packets."""
    print("Monitoring changes across multiple telemetry packets of a target:")
    
    # Report changes across all packets of the SPACECRAFT target
    report_all_telemetry(
        "SPACECRAFT",
        exclude_packets=["DEBUG_TLM", "MEMORY_DUMP"]  # Exclude noisy packets
    )
    
    print("\nWe can also filter to focus on specific types of packets:")
    # Only show critical packets
    report_all_telemetry(
        "SPACECRAFT",
        level_of_detail=0,  # Only show changes
        exclude_packets=["DEBUG_TLM", "MEMORY_DUMP", "DIAGNOSTIC_TLM"]
    )

def system_wide_example():
    """Demonstrate system-wide telemetry reporting."""
    print("For system diagnostics, we can report telemetry across all targets:")
    
    # This will show changes across all targets
    report_all_targets_telemetry(
        exclude_targets=["SIMULATOR", "TEST_TARGET"],  # Exclude non-essential targets
        exclude_packets=["DEBUG_TLM"]  # Exclude debug packets across all targets
    )
    
    print("\nFor detailed analysis, we can show all telemetry values:")
    # Show all values with maximum detail
    report_all_targets_telemetry(
        level_of_detail=2
    )

def custom_detection_example():
    """Demonstrate custom telemetry change detection."""
    print("Let's demonstrate custom analysis of telemetry changes...")
    
    # First, get an initial baseline by calling report_telemetry
    print("Capturing initial power telemetry state...")
    report_telemetry("SPACECRAFT", "POWER_TLM")
    
    print("\nLet's simulate a power system change...")
    # In a real script, commands would be sent here
    
    print("\nNow let's check for changes and do custom analysis...")
    # Get the changes by calling report_telemetry again
    report_telemetry("SPACECRAFT", "POWER_TLM")
    
    # For custom analysis, you would need to access the global telemetry data
    # This is more advanced usage and would typically be done by importing
    # the global variables from telemetry_utils if needed
    print("\nCustom analysis would typically be done by:")
    print("1. Using the report functions to see changes")
    print("2. If needed, accessing telemetry_utils.current_vals and telemetry_utils.prev_vals")
    print("3. Implementing custom logic based on the stored telemetry data")
    
    print("\nExample custom checks:")
    print("- Voltage trend analysis")
    print("- Power threshold monitoring") 
    print("- Rate of change calculations")

if __name__ == "__main__":
    main()