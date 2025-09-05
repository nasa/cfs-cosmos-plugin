from openc3.script.suite import Group

# Group class name should indicate what the scripts are testing
class cfs_reg_test_group_cfs_ci_lab(Group):
    """
    Test cases for checking FSW "aliveness"
    - Methods beginning with script_ or test_ are added to Script dropdown
    """

    def test_aliveness(self):
        """
        FSW Aliveness Test for standard cFS bundle apps
        - Send a no-op command to each cFS bundle app in the system
            then verify the command was received (by checking telemetry)
        - Reset the command counter
            then verify the command was received (by checking telemetry)
        """
        # Create a list of apps to test
        fsw_apps_to_test = ["CI_LAB"]

        # For each app in the list, verify its alive by sending a noop, then reset the hk counters
        for app_name in fsw_apps_to_test:
            Group.print(f"Testing {app_name} aliveness on <%= target_name %>")

            # Verify that we have a recent packet (by waiting for a new one to arrive)
            wait_check_packet(f"<%= target_name %>", f"{app_name}_HK", 1, 100)

            # Assuming no one else is sending commands, grab the latest command count
            cmd_count = tlm(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER")

            # Check accepted NOOP command proving application is up and running
            cmd(f"<%= target_name %> {app_name}_CMD_NOOP")
            wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

            # Check accepted Reset Counters command
            cmd(f"<%= target_name %> {app_name}_CMD_RESET_COUNTERS")
            wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == 0", 100)

    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        pass

    def teardown(self):
        """
        Test Group Setup
        - Runs when Group Teardown button is pressed
        - Runs after all scripts when Group Start is pressed
        """
        pass
