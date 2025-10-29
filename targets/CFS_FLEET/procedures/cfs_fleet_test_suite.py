from openc3.script.suite import Suite, Group

# Load the cFE Fleet Test Groups
load_utility("<%= target_name %>/procedures/cfs_fleet_test_group_aliveness.py")

class cfs_test_suite(Suite):
    def __init__(self):
        # Add each test group
        # ------------------------------------------------------------------------
        # The order that we add these test groups affects the order
        # they're listed in the COSMOS Script Runner drop-down menu
        # To make it easier to find tests using the drop-down,
        # these are added in alphabetical order
        # ------------------------------------------------------------------------
        self.add_group(cfs_fleet_test_group_aliveness)

    def setup(self):
        # Run when Suite Setup button is pressed
        # Run before all groups when Suite Start is pressed

        # Create a list of fsw targets
        num_cfs_targets = <%= $cfs_fleet_globals_num_cfs_targets %>
        Group.print(f"Starting cFS Fleet Test Suite against {num_cfs_targets} target(s).")
        fsw_targets_to_test = []
        for cpu_index in range(num_cfs_targets):
            cfs_target_name = f"CFS-{cpu_index + 1}"
            fsw_targets_to_test.append(cfs_target_name)
            Group.print(f"cFS Target Name: {cfs_target_name}")

        # Determine the correct IP address for FSW to send telemetry to
        # cosmos_ip_addr = ask("Enter the COSMOS IP address (that FSW nodes should send telemetry to):",
        #                     "127.0.0.1", False)
        cosmos_ip_addr = "127.0.0.1"

        # Enable Telemetry for all FSW nodes
        for fsw_target in fsw_targets_to_test:
            Group.print(f"Sending TO_LAB_CMD_ENABLE_OUTPUT command to {fsw_target} with DEST_IP '{cosmos_ip_addr}'")
            cmd(f"{fsw_target} TO_LAB_CMD_ENABLE_OUTPUT with DEST_IP '{cosmos_ip_addr}'")
            wait_check_packet(f"{fsw_target}", "TO_LAB_HK", 1, 100)

    def teardown(self):
        # Run when Suite Teardown button is pressed
        # Run after all groups when Suite Start is pressed
        pass
