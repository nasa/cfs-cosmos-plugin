# Testing IDE integration to get rid of error and warning flags

# These imports should no longer show warnings
from openc3.script import cmd, tlm, wait
from openc3.script import subscribe_packets, get_packets
from openc3.script import stash_set, stash_get
from openc3.script.suite import Group

# Test that IDE recognizes the functions
def test_stubs():
    # These should have proper type hints now
    result = cmd("TARGET NOOP")  # Should show return type Dict[str, Any]
    value = tlm("TARGET PACKET ITEM")  # Should show return type Any
    success = wait("TARGET PACKET ITEM == 5")  # Should show return type bool
    Group.print("Test message")  # Should not show warnings