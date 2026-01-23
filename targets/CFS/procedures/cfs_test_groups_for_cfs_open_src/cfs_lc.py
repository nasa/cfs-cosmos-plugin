from openc3.script.suite import Group

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfs_lc(Group):
    """
    - Methods beginning with script_ or test_ are added to Script dropdown
    """

    def test_00_aliveness(self):
        """
        FSW Aliveness Test
        - Send a no-op command
            then verify the command was received (by checking the command counter incremented)
        - Reset the command counter
            then verify the command was received (by checking the command counter was cleared)
        """
        Group.print(f"Testing LC aliveness on <%= target_name %>")

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"LC_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> LC_HK COMMAND_COUNTER")

        # Check accepted NOOP command proving application is up and running
        cmd(f"<%= target_name %> LC_CMD_NOOP")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Check accepted Reset Counters command
        cmd(f"<%= target_name %> LC_CMD_RESET_COUNTERS")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == 0", 100)

    def test_01_set_app_state(self):
        """
        FSW App State Test
        - Send Set App State Command for ACTIVE, PASSIVE, and DISABLED
            then verify the command was received (by checking the command counter
            incremented and state was set)
        - Send Set App State Command with invalid state
            then verify the command was received (by checking the command error counter)
        """
        Group.print(f"Testing LC set app state command on <%= target_name %>")
        
        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"LC_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> LC_HK COMMAND_COUNTER")
        
        # Assuming no one else is sending commands, grab the latest command err count
        cmd_err_count = tlm(f"<%= target_name %> LC_HK COMMAND_ERROR_COUNTER")
        
        # Check accepted Set App State = 1 command
        cmd(f"<%= target_name %> LC_CMD_SET_APP_STATE with NEW_STATE ACTIVE")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        wait_check(f"<%= target_name %> LC_HK APP_STATE == 'ACTIVE'", 100)
        
        # Check accepted Set App State = 2 command
        cmd(f"<%= target_name %> LC_CMD_SET_APP_STATE with NEW_STATE PASSIVE")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 2}", 100)
        wait_check(f"<%= target_name %> LC_HK APP_STATE == 'PASSIVE'", 100)
        
        # Check accepted Set App State = 3 command
        cmd(f"<%= target_name %> LC_CMD_SET_APP_STATE with NEW_STATE DISABLED")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 3}", 100)
        wait_check(f"<%= target_name %> LC_HK APP_STATE == 'DISABLED'", 100)
        
        # Check accepted Set App State = 4 (invalid) command
        cmd(f"<%= target_name %> LC_CMD_SET_APP_STATE with NEW_STATE 4")
        wait_check(f"<%= target_name %> LC_HK COMMAND_ERROR_COUNTER == {cmd_err_count + 1}", 100)
    
    def disabled_test_02_set_ap_state(self):
        """
        FSW AP State Test
        - Send Set AP State Command for ACTIVE, PASSIVE, DISABLED, and PERM_OFF
            then verify the command was received (by checking the command counter
            incremented and state was set)
        - Send Set App State Command with invalid state
            then verify the command was received (by checking the command error counter)
        """
        
        Group.print(f"Testing LC set ap state command on <%= target_name %>")
        
        # Load table for test
        # cmd(f"<%= target_name %> CFE_TBL_CMD_LOAD with LOAD_FILENAME '/cf/lc_def_adt.tbl'")
        # cmd(f"<%= target_name %> CFE_TBL_CMD_VALIDATE with ACTIVE_TABLE_FLAG ACTIVE, TABLE_NAME 'LC.LC_ADT'")
        
        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"LC_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> LC_HK COMMAND_COUNTER")
        
        # Assuming no one else is sending commands, grab the latest command err count
        cmd_err_count = tlm(f"<%= target_name %> LC_HK COMMAND_ERROR_COUNTER")
        
        # Check accepted Set AP State = 1 command
        cmd(f"<%= target_name %> LC_CMD_SET_AP_STATE with AP_ID 0, NEW_STATE ACTIVE")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        wait_check(f"<%= target_name %> LC_HK AP_1_STATE == 'ACTIVE'", 100)
        
        # Check accepted Set AP State = 2 command
        cmd(f"<%= target_name %> LC_CMD_SET_AP_STATE with AP_ID 0, NEW_STATE PASSIVE")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 2}", 100)
        wait_check(f"<%= target_name %> LC_HK AP_1_STATE == 'PASSIVE'", 100)
        
        # Check accepted Set App State = 3 command
        cmd(f"<%= target_name %> LC_CMD_SET_AP_STATE with AP_ID 0, NEW_STATE DISABLED")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 3}", 100)
        wait_check(f"<%= target_name %> LC_HK AP_1_STATE == 'DISABLED'", 100)
        
        # Check accepted Set App State = 4 command
        cmd(f"<%= target_name %> LC_CMD_SET_AP_STATE with AP_ID 0, NEW_STATE PERM_OFF")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 4}", 100)
        wait_check(f"<%= target_name %> LC_HK AP_1_STATE == 'PERM_OFF'", 100)
        
        # Check accepted Set App State = 5 (invalid) command
        cmd(f"<%= target_name %> LC_CMD_SET_AP_STATE with AP_ID 0, NEW_STATE 5")
        wait_check(f"<%= target_name %> LC_HK COMMAND_ERROR_COUNTER == {cmd_err_count + 1}", 100)

    def disabled_test_03_set_ap_perm_off(self):
        """
        FSW AP Perm Off Test
        - Send Set AP Perm Off Command with AP_ID 0
            then verify the command was received (by checking the command counter
            incremented)
        """
        
        Group.print(f"Testing LC set ap perm off command on <%= target_name %>")
        
        # Load table for test
        # cmd(f"<%= target_name %> CFE_TBL_CMD_LOAD with LOAD_FILENAME '/cf/lc_def_adt.tbl'")
        # cmd(f"<%= target_name %> CFE_TBL_CMD_VALIDATE with ACTIVE_TABLE_FLAG ACTIVE, TABLE_NAME 'LC.LC_ADT'")
        
        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"LC_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> LC_HK COMMAND_COUNTER")
        
        # Assuming no one else is sending commands, grab the latest command err count
        cmd_err_count = tlm(f"<%= target_name %> LC_HK COMMAND_ERROR_COUNTER")
        
        # Check accepted Set AP Perm Off Command
        cmd(f"<%= target_name %> LC_CMD_SET_AP_PERM_OFF with AP_ID 0")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        
    def test_04_reset_ap_stats(self):
        """
        FSW AP Stats Test
        - Send Reset AP Stats Command for AP_ID 0
            then verify the command was received (by checking the command counter
            incremented)
        """
        
        Group.print(f"Testing LC reset ap stats command on <%= target_name %>")
        
        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"LC_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> LC_HK COMMAND_COUNTER")
        
        # Assuming no one else is sending commands, grab the latest command err count
        cmd_err_count = tlm(f"<%= target_name %> LC_HK COMMAND_ERROR_COUNTER")
        
        # Check accepted Reset AP Stats Command
        cmd(f"<%= target_name %> LC_CMD_RESET_AP_STATS with AP_ID 0")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

    def test_05_reset_wp_stats(self):
        """
        FSW WP Stats Test
        - Send Reset WP Stats Command for AP_ID 0
            then verify the command was received (by checking the command counter
            incremented)
        """
        
        Group.print(f"Testing LC reset wp stats command on <%= target_name %>")
        
        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"LC_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> LC_HK COMMAND_COUNTER")
        
        # Assuming no one else is sending commands, grab the latest command err count
        cmd_err_count = tlm(f"<%= target_name %> LC_HK COMMAND_ERROR_COUNTER")
        
        # Check accepted Reset WP Stats Command
        cmd(f"<%= target_name %> LC_CMD_RESET_WP_STATS with WP_ID 0")
        wait_check(f"<%= target_name %> LC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

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
