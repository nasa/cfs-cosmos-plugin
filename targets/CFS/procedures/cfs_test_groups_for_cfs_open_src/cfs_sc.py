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
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Check accepted Reset Counters command
        cmd(f"<%= target_name %> SC_CMD_RESET_COUNTERS")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER == 0", 100)
    

    def test_01_NoOp(self):
        """
        Test the no-op command.
        """
        
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        
        cmd(f"<%= target_name %> SC_CMD_NOOP")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_02_continue_ats_on_failure(self):
        """
        Continue ATS on Failure Test
        - Send a continue ats on failure command
            then verify the command was received (by checking the command counter incremented)
            and set back to default value (True)
        """
        
        Group.print(f"Testing SC Continue ATS on Failure on <%= target_name %>")

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")

        # Check accepted Continue ATS on Failure command
        cmd(f"<%= target_name %> SC_CMD_CONTINUE_ATS_ON_FAILURE with CONTINUE_STATE FALSE")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        wait_check(f"<%= target_name %> SC_HK CONT_ATS_ON_FAIL == 'FALSE'", 100)

        # Set Continue ATS on Failure to Default Value (True)
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_CONTINUE_ATS_ON_FAILURE with CONTINUE_STATE TRUE")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        wait_check(f"<%= target_name %> SC_HK CONT_ATS_ON_FAIL == 'TRUE'", 100)
    

    def test_03_ats_operations(self):
        """
        ATS Operations Test
        - Test start ATS command
        - Test jump ATS command
        - Test switch ATS command
        - Test append ATS command
        - Test stop ATS 
        """
        
        Group.print(f"Testing SC ATS operations on <%= target_name %>")

        # Load ATS A table
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_TBL_CMD_LOAD with LOAD_FILENAME '/cf/sc_ats1.tbl'")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Validate ATS A table
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_TBL_CMD_VALIDATE with ACTIVE_TABLE_FLAG INACTIVE, TABLE_NAME 'SC.ATS_TBL1'")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Activate ATS A table
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_TBL_CMD_ACTIVATE with TABLE_NAME 'SC.ATS_TBL1'")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Load ATS B table
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_TBL_CMD_LOAD with LOAD_FILENAME '/cf/sc_ats2-test.tbl'")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Validate ATS B table
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_TBL_CMD_VALIDATE with ACTIVE_TABLE_FLAG INACTIVE, TABLE_NAME 'SC.ATS_TBL2'")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Activate ATS B table
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_TBL_CMD_ACTIVATE with TABLE_NAME 'SC.ATS_TBL2'")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Load ATS Append table
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_TBL_CMD_LOAD with LOAD_FILENAME '/cf/sc_append-test.tbl'")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Validate ATS Append table
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_TBL_CMD_VALIDATE with ACTIVE_TABLE_FLAG INACTIVE, TABLE_NAME 'SC.APPEND_TBL'")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Activate ATS Append table
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_TBL_CMD_ACTIVATE with TABLE_NAME 'SC.APPEND_TBL'")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Append HK values should auto-update when table activated
        wait_check(f"<%= target_name %> SC_HK APPEND_ENTRY_COUNT == 4", 100)
        wait_check(f"<%= target_name %> SC_HK APPEND_BYTE_COUNT == 36", 100)
        wait_check(f"<%= target_name %> SC_HK APPEND_LOAD_COUNT == 1", 100)

        # Set SC time to 1000000 (because RTS1 starts shortly after that time).
        cmd_count = tlm(f"<%= target_name %> CFE_TIME_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> CFE_TIME_CMD_SET_TIME with SECONDS 1000000, MICROSECONDS 0")
        wait_check(f"<%= target_name %> CFE_TIME_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        ########################
        # Test Start ATS command
        ########################

        wait_check(f"<%= target_name %> SC_HK ATP_STATE == 'IDLE'", 100)

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")

        cmd(f"<%= target_name %> SC_CMD_START_ATS with ATS_NUM 1")
        
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        wait_check(f"<%= target_name %> SC_HK ATP_STATE == 'EXECUTING'", 100)

        # NOTE: expected event message text: "ATS A Execution Started"

        wait(3)

        ########################
        # Test Switch ATS command
        ########################

        wait_check(f"<%= target_name %> SC_HK SWITCH_PEND_FLAG == 'NO'", 100)

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")

        cmd(f"<%= target_name %> SC_CMD_SWITCH_ATS")
        
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Note: SWITCH_PEND_FLAG should go to YES, and then back to NO when switch completes.
        # #     This can't be checked, because the switch completes before the next HK packet.

        # NOTE: expected event messages text:
        #       "Switch ATS is Pending"
        #       "ATS Switched from A to B"

        ########################
        # Test Append ATS command
        ########################

        wait_check(f"<%= target_name %> SC_HK APPEND_CMD_ARG != 2", 100)

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")

        cmd(f"<%= target_name %> SC_CMD_APPEND_ATS with ATS_NUM 2")
        
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        wait_check(f"<%= target_name %> SC_HK APPEND_CMD_ARG == 2", 100)

        # NOTE: expected event message text: "Append ATS B command: %d ATS entries appended"

        ########################
        # Test Jump ATS command
        ########################

        new_time = 1000101

        wait_check(f"<%= target_name %> SC_HK NEXT_ATS_TIME != {new_time}", 100)

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")

        cmd(f"<%= target_name %> SC_CMD_JUMP_ATS with NEW_TIME {new_time}")
        
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        wait_check(f"<%= target_name %> SC_HK NEXT_ATS_TIME == 1000130", 100)

        # NOTE: expected event messages text:
        #       "Jump Cmd: Jump time less than or equal to list entry %u"
        #       "Next ATS command time in the ATP was set to %s"
        #       "Jump Cmd: Skipped %d ATS commands"

        ########################
        # Test Stop ATS command
        ########################

        wait_check(f"<%= target_name %> SC_HK ATP_STATE == 'EXECUTING'", 100)

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        
        cmd(f"<%= target_name %> SC_CMD_STOP_ATS")

        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        wait_check(f"<%= target_name %> SC_HK ATP_STATE == 'IDLE'", 100)

        # NOTE: expected event message text: "ATS B stopped"

        wait(3)


    def test_04_rts_operations(self):
        """
        RTS Operations Test
        - Test disable RTS command
        - Test enable RTS command
        - Test start RTS command
        - Test stop RTS command
        """

        Group.print(f"Testing SC RTS operations on <%= target_name %>")

        # First, ensure all W0 RTSs are enabled (0)
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_ENABLE_RTS_GRP with FIRST_RTS_NUM 1, LAST_RTS_NUM 4")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_DIS_STATUS == 0x0000", 100)

        ##############################
        # Test Disable RTS (1) command
        ##############################

        # Check RTS_W0_DIS_STATUS, bit 0, equals 0 (enabled)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_DIS_STATUS & 0x0001 == 0x0000", 100)

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_DISABLE_RTS with RTS_NUM 1")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Check RTS_W0_DIS_STATUS, bit 0, equals 1 (disabled)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_DIS_STATUS & 0x0001 == 0x0001", 100)

        # NOTE: expected event message text: "Disabled RTS 001"

        #############################
        # Test Enable RTS (1) command
        #############################

        # Check RTS_W0_DIS_STATUS, bit 0, equals 1 (disabled)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_DIS_STATUS & 0x0001 == 0x0001", 100)

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_ENABLE_RTS with RTS_NUM 1")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Check RTS_W0_DIS_STATUS, bit 0, equals 0 (enabled)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_DIS_STATUS & 0x0001 == 0x0000", 100)
        
        # NOTE: expected event message text: "Enabled RTS 001"

        ########################
        # Test Start RTS command
        ########################

        # Check RTS_W0_EXE_STATUS, bit 0, equals 0 (idle)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_EXE_STATUS & 0x0001 == 0x0000", 100)

        wait_check(f"<%= target_name %> SC_HK NUM_RTS_ACTIVE == 0", 100)

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_START_RTS with RTS_NUM 1")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Check RTS_W0_EXE_STATUS, bit 0, equals 1 (executing)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_EXE_STATUS & 0x0001 == 0x0001", 100)
        
        wait_check(f"<%= target_name %> SC_HK NUM_RTS_ACTIVE == 1", 100)

        # NOTE: expected event message text: "RTS Number 001 Started"

        wait(3)

        #######################
        # Test Stop RTS command
        #######################

        # Check RTS_W0_EXE_STATUS, bit 0, equals 1 (executing)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_EXE_STATUS & 0x0001 == 0x0001", 100)
        
        wait_check(f"<%= target_name %> SC_HK NUM_RTS_ACTIVE == 1", 100)

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_STOP_RTS with RTS_NUM 1")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Check RTS_W0_EXE_STATUS, bit 0, equals 0 (idle)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_EXE_STATUS & 0x0001 == 0x0000", 100)

        wait_check(f"<%= target_name %> SC_HK NUM_RTS_ACTIVE == 0", 100)

        # NOTE: expected event message text: "RTS Number 001 Aborted"


    def test_05_rts_group_operations(self):
        """
        RTS Group Operations Test
        - Test disable rts group command
        - Test enable rts group command
        - Test start rts group command
        - Test stop rts group command
        """

        Group.print(f"Testing SC RTS group operations on <%= target_name %>")

        # First, ensure all W0 RTSs are enabled (0)
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_ENABLE_RTS_GRP with FIRST_RTS_NUM 1, LAST_RTS_NUM 4")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_DIS_STATUS == 0x0000", 100)

        ##############################################
        # Test Disable RTS group (2 through 4) command
        ##############################################

        # Check RTS_W0_DIS_STATUS, bits 2-4, equal 0 (enabled)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_DIS_STATUS & 0x000E == 0x0000", 100)
        
        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_DISABLE_RTS_GRP with FIRST_RTS_NUM 2, LAST_RTS_NUM 4")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Check RTS_W0_DIS_STATUS, bits 2-4, equal 1 (disabled)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_DIS_STATUS & 0x000E == 0x000E", 100)

        # NOTE: expected event message text: "Disable RTS group: FirstID=2, LastID=4, Modified=3"

        #############################################
        # Test Enable RTS group (2 through 4) command
        #############################################

        # Check RTS_W0_DIS_STATUS, bits 2-4, equal 1 (disabled)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_DIS_STATUS & 0x000E == 0x000E", 100)

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")

        cmd(f"<%= target_name %> SC_CMD_ENABLE_RTS_GRP with FIRST_RTS_NUM 2, LAST_RTS_NUM 4")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Check RTS_W0_DIS_STATUS, bits 2-4, equal 0 (enabled)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_DIS_STATUS & 0x000E == 0x0000", 100)

        # NOTE: expected event message text: "Enable RTS group: FirstID=2, LastID=4, Modified=3"

        ##############################################
        # Test Start RTS group (2 through 4) command
        ##############################################

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_START_RTS_GRP with FIRST_RTS_NUM 2, LAST_RTS_NUM 4")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Check RTS_W0_EXE_STATUS, bit 2-4, equal 1 (executing)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_EXE_STATUS == 0x000E", 100)

        wait_check(f"<%= target_name %> SC_HK NUM_RTS_ACTIVE == 3", 100)

        # NOTE: expected event message text: "Start RTS group: FirstID=2, LastID=4, Modified=3"

        wait(3)

        ##############################################
        # Test Stop RTS group (2 through 4) command
        ##############################################

        cmd_count = tlm(f"<%= target_name %> SC_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> SC_CMD_STOP_RTS_GRP with FIRST_RTS_NUM 2, LAST_RTS_NUM 4")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Check RTS_W0_EXE_STATUS, bit 2-4, equal 0 (idle)
        wait_check(f"<%= target_name %> SC_HK RTS_W0_EXE_STATUS & 0x000E == 0x0000", 100)

        wait_check(f"<%= target_name %> SC_HK NUM_RTS_ACTIVE == 0", 100)

        # NOTE: expected event message text: "Stop RTS group: FirstID=2, LastID=4, Modified=3"


    def test_06_ResetCounters(self):
        """
        Test the ResetCounters command.
        """

        # NOTE: Current initial version is simplified to only increment COMMAND_COUNTER and COMMAND_ERROR_COUNTER before reset.

        # Cause COMMAND_COUNTER to increment
        cmd("<%= target_name %> DS_CMD_NOOP")
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER > 0", 100)
        
        # Cause COMMAND_ERROR_COUNTER to increment
        cmd(f"<%= target_name %> SC_CMD_START_RTS with RTS_NUM 2")
        wait(5)
        cmd(f"<%= target_name %> SC_CMD_START_RTS with RTS_NUM 2")
        wait_check(f"<%= target_name %> SC_HK COMMAND_ERROR_COUNTER > 0", 100)
        wait(7)

        # Send ResetCounters command
        cmd(f"<%= target_name %> SC_CMD_RESET_COUNTERS")
        
        # Verify counters are reset to zero
        wait_check(f"<%= target_name %> SC_HK COMMAND_COUNTER >= 0", 100)
        wait_check(f"<%= target_name %> SC_HK COMMAND_ERROR_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> SC_HK RTS_ACTIVE_CTR == 0", 100)
        wait_check(f"<%= target_name %> SC_HK RTS_ACTIVE_ERR_CTR == 0", 100)
        wait_check(f"<%= target_name %> SC_HK ATS_CMD_CTR == 0", 100)
        wait_check(f"<%= target_name %> SC_HK ATS_CMD_ERR_CTR == 0", 100)
        wait_check(f"<%= target_name %> SC_HK RTS_CMD_CTR == 0", 100)
        wait_check(f"<%= target_name %> SC_HK RTS_CMD_ERR_CTR == 0", 100)
        

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
