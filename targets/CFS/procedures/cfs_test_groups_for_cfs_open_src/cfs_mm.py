from openc3.script.suite import Group

_app_name = "MM"

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfs_mm(Group):
    """
    - Methods beginning with script_ or test_ are added to Script dropdown
    """

    def test_0_aliveness(self):
        """
        FSW Aliveness Test
        - Send a no-op command
            then verify the command was received (by checking the command counter incremented)
        - Reset the command counter
            then verify the command was received (by checking the command counter was cleared)
        """

        Group.print(f"Testing {_app_name} aliveness on <%= target_name %>")

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"{_app_name}_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> {_app_name}_HK COMMAND_COUNTER")

        # Check accepted NOOP command proving application is up and running
        cmd(f"<%= target_name %> {_app_name}_CMD_NOOP")
        wait_check(f"<%= target_name %> {_app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Check accepted Reset Counters command
        cmd(f"<%= target_name %> {_app_name}_CMD_RESET_COUNTERS")
        wait_check(f"<%= target_name %> {_app_name}_HK COMMAND_COUNTER == 0", 100)


    def test_1_LookupSym_test(self):
        
        Group.print(f"Testing {_app_name} MM_CMD_LOOKUPSYM command on <%= target_name %>")
        
        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"{_app_name}_HK", 1, 100)
        
        cmd_count = tlm(f"<%= target_name %> {_app_name}_HK COMMAND_COUNTER")
        
        # Check accepted MM_CMD_LOOKUPSYM command and LASTACTION set correctly
        cmd(f"<%= target_name %> MM_CMD_LOOKUPSYM with SYMNAME 'SAMPLE_LIB_Buffer'")
        wait_check(f"<%= target_name %> {_app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        wait_check(f"<%= target_name %> {_app_name}_HK LASTACTION == 'SYM_LOOKUP'", 100) 
        
        # Check accepted Reset Counters command
        cmd(f"<%= target_name %> {_app_name}_CMD_RESET_COUNTERS")
        wait_check(f"<%= target_name %> {_app_name}_HK COMMAND_COUNTER == 0", 100)


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
