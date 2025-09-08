# examples/requirement_examples.py
"""
Examples showing how to use the RequirementTracker class for tracking
requirement verification status in COSMOS tests.

This file can be run directly to see the examples in action.
"""

from cosmos_test_utils import RequirementTracker
from openc3.script.suite import Group

def main():
    print("EXAMPLE: Basic RequirementTracker Usage")
    print("=====================================")
    
    # Create a requirement tracker
    req_tracker = RequirementTracker()
    
    # Initialize requirements
    print("\n1. Setting requirement states")
    req_tracker.set_requirement("SYS-001", "U", "System requirement")
    req_tracker.set_requirement("SYS-002", "U", "Another system requirement")
    req_tracker.set_requirement("SYS-003", "U", "Third system requirement")
    
    # Set requirements during testing
    print("\n2. Updating requirement states during testing")
    req_tracker.set_requirement("SYS-001", "P", "Verified by command test")
    req_tracker.set_requirement("SYS-002", "F", "Failed timeout condition")
    req_tracker.set_requirement("SYS-003", "I", "Needs visual inspection")
    
    # Generate a report
    print("\n3. Generating a basic report")
    print(req_tracker.generate_requirements_report())
    
    # Set multiple requirements at once using a list
    print("\n4. Setting multiple requirements at once using a list")
    req_tracker.set_multiple_requirements(
        ["PERF-001", "PERF-002", "PERF-003"],
        "P",
        "All performance requirements passed"
    )
    
    # Set multiple requirements at once using a comma-separated string
    print("\n5. Setting multiple requirements at once using a comma-separated string")
    req_tracker.set_multiple_requirements(
        "NET-001, NET-002, NET-003",
        "P",
        "All network requirements verified"
    )
    
    # Attempt invalid transitions
    print("\n6. Testing requirement state transition rules")
    req_tracker.set_requirement("SYS-002", "P", "Attempting to change from F to P")
    req_tracker.set_requirement("SYS-003", "P", "Attempting to change from I to P")
    
    # Print detailed report with event history
    print("\n7. Generating a detailed report with event history")
    # First enable debug mode for detailed output
    req_tracker.set_debug_mode(True)
    print(req_tracker.generate_requirements_report())
    # Turn debug mode back off
    req_tracker.set_debug_mode(False)
    
    # Different report style
    print("\n8. Generating a basic report with alternate report style")
    req_tracker.requirements_report()

    print("\n9. Generating a basic report with alternate report style using COSMOS Group.print")
    req_tracker.requirements_report(Group.print)

    print("\n10. Generating a detailed report with alternate report style")
    # First enable debug mode for detailed output
    req_tracker.set_debug_mode(True)
    req_tracker.requirements_report()
    # Turn debug mode back off
    req_tracker.set_debug_mode(False)
    
    print("\nExample complete!")

if __name__ == "__main__":
    main()