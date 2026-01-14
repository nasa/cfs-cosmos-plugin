from openc3.script.suite import Group

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfs_sc(Group):
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

        Group.print(f"Testing SC aliveness on <%= target_name %>")

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"SC_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")

        # Check accepted NOOP command proving application is up and running
        cmd(f"<%= target_name %> SC_CMD_NOOP")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Check accepted Reset Counters command
        cmd(f"<%= target_name %> SC_CMD_RESET_COUNTERS")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == 0", 100)

    def test_01_continue_ats_on_failure(self):
        """
        Continue ATS on Failure Test
        - Send a continue ats on failure command
            then verify the command was received (by checking the command counter incremented)
            and set back to default value (True)
        """
        
        Group.print(f"Testing SC Continue ATS on Failure on <%= target_name %>")

        # Verify we have a recent packet
        wait_check_packet(f"<%= target_name %>", f"SC_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")

        # Check accepted Continue ATS on Failure command
        cmd(f"<%= target_name %> SC_CMD_CONTINUE_ATS_ON_FAILURE with CONTINUE_STATE FALSE")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        wait_check(f"<%= target_name %> SC_HK CONT_ATS_ON_FAIL == 'FALSE'", 100)

        # Set Continue ATS on Failure to Default Value (True)
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_CONTINUE_ATS_ON_FAILURE with CONTINUE_STATE TRUE")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        wait_check(f"<%= target_name %> SC_HK CONT_ATS_ON_FAIL == 'TRUE'", 100)

    def test_02_rts_operations(self):
        """
        RTS Operations Test
        - Send an enable rts command
            then verify the command was received (by checking the command counter incremented)
        - Send a start rts command
            then verify the command was received (by checking the command counter incremented)
        - Send a stop rts command
            then verify the command was received (by checking the command counter incremented)
        - Send a disable rts command
            then verify the command was received (by checking the command counter incremented)
        """

        Group.print(f"Testing SC rts operations on <%= target_name %>")

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"SC_HK", 1, 100)

        # Enable RTS 1
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_ENABLE_RTS with RTS_ID 1")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Test Start RTS command
        # Expect the SC cmd count to increase by 1 for this SC_CMD_START_RTS command,
        # plus 3 for the commands in the RTS1 (SC No-Op, SC Enable RTS 2, SC Start RTS 2)
        # plus 3 for the commands in the RTS2 (three SC No-Ops)
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        expected_num_sc_cmd_count = cmd_count + 1 + 6
        cmd(f"<%= target_name %> SC_CMD_START_RTS with RTS_ID 1")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {expected_num_sc_cmd_count}", 100)

        wait(3)

        # Check accepted Stop RTS command
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_STOP_RTS with RTS_ID 1")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Check accepted Disable RTS command
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_DISABLE_RTS with RTS_ID 1")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

    def test_03_rts_group_operations(self):
        """
        RTS Group Operations Test
        - Send an enable rts group command
            then verify the command was received (by checking the command counter incremented)
        - Send a start rts group command
            then verify the command was received (by checking the command counter incremented)
        - Send a stop rts group command
            then verify the command was received (by checking the command counter incremented)
        - Send a disable rts group command
            then verify the command was received (by checking the command counter incremented)
        """

        Group.print(f"Testing SC rts group operations on <%= target_name %>")

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"SC_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")

        # Check accepted Enable RTS Group command
        cmd(f"<%= target_name %> SC_CMD_ENABLE_RTS_GROUP with FIRST_RTS_ID 2, LAST_RTS_ID 4")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Check accepted Start RTS Group command
        # Expect the cmd count to increase by 1 for this SC_CMD_START_RTS_GROUP command,
        # plus 9 for the commands in the RTSs (three SC no-ops per RTS)
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        expected_num_sc_cmd_count = cmd_count + 1 + (3 * 3)
        cmd(f"<%= target_name %> SC_CMD_START_RTS_GROUP with FIRST_RTS_ID 2, LAST_RTS_ID 4")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {expected_num_sc_cmd_count}", 100)

        wait(3)

        # Check accepted Stop RTS Group command
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_STOP_RTS_GROUP with FIRST_RTS_ID 2, LAST_RTS_ID 4")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Check accepted Disable RTS Group command
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_DISABLE_RTS_GROUP with FIRST_RTS_ID 2, LAST_RTS_ID 4")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        pass

    def teardown(self):
        """
        Test Group Teardown
        - Runs when Group Teardown button is pressed
        - Runs after all scripts when Group Start is pressed
        """
        pass
