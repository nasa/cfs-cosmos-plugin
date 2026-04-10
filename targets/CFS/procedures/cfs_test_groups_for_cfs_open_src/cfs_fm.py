from openc3.script.suite import Group
# Verify FM commands work properly.  Not testing error cases.

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfs_fm(Group):
    """
    - Methods beginning with script_ or test_ are added to Script dropdown
    """
    
    def test_00_Aliveness(self):
        """
        FSW Aliveness Test
        - Send a no-op command
            then verify the command was received (by checking the command counter incremented)
        - Reset the command counter
            then verify the command was received (by checking the command counter was cleared)
        """
        
        Group.print("Testing FM aliveness on <%= target_name %>")
        
        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", "FM_HK", 1, 20)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")

        # Check accepted NOOP command proving application is up and running
        cmd(f"<%= target_name %> FM_CMD_NOOP")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER == {cmd_count + 1}", 20)

        # Check accepted Reset Counters command
        cmd(f"<%= target_name %> FM_CMD_RESET_COUNTERS")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER == 0", 20)
    
    
    def test_01_NoOp(self):
        """
        Test the no-op command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        cmd("<%= target_name %> FM_CMD_NOOP")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_02_CopyFile(self):
        """
        Test the CopyFile command.
        """
        
        # First, create the file to be copied
        # ###################################
        cmd_count = tlm(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER")

        # Send CFE_SB_CMD_WRITE_ROUTING_INFO command
        cmd(f"<%= target_name %> CFE_SB_CMD_WRITE_ROUTING_INFO with FILENAME '/cf/file_rt.dat'")

        # Verify the command was successful
        wait_check(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        # ###################################

        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_COPY_FILE with OVERWRITE OVERWRITE, SOURCE_PATH '/cf/file_rt.dat', TARGET_PATH '/cf/file_rt-cp.dat'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Cleanup: Delete the files that were created
        # ############################################
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with PATH '/cf/file_rt.dat'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with PATH '/cf/file_rt-cp.dat'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    
    
    def test_03_MoveFile(self):
        """
        Test the MoveFile command.
        """

        # First, create the file to be moved
        # ###################################
        cmd_count = tlm(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER")

        # Send CFE_SB_CMD_WRITE_ROUTING_INFO command
        cmd(f"<%= target_name %> CFE_SB_CMD_WRITE_ROUTING_INFO with FILENAME '/cf/file_rt.dat'")

        # Verify the command was successful
        wait_check(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        # ###################################
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_MOVE_FILE with OVERWRITE OVERWRITE, SOURCE_PATH '/cf/file_rt.dat', TARGET_PATH '/cf/file_rt-mv.dat'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Cleanup: Delete the file that was created/moved
        # ###############################################
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with PATH '/cf/file_rt-mv.dat'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_04_RenameFile(self):
        """
        Test the RenameFile command.
        """
        # First, create the file to be renamed
        # ####################################
        cmd_count = tlm(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER")

        # Send CFE_SB_CMD_WRITE_ROUTING_INFO command
        cmd(f"<%= target_name %> CFE_SB_CMD_WRITE_ROUTING_INFO with FILENAME '/cf/file_rt.dat'")

        # Verify the command was successful
        wait_check(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        # ####################################

        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_RENAME_FILE with SOURCE_PATH '/cf/file_rt.dat', TARGET_PATH '/cf/file_rt-rnm.dat'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Cleanup: Delete the file that was created/renamed
        # ###############################################
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with PATH '/cf/file_rt-rnm.dat'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_05_DeleteFile(self):
        """
        Test the DeleteFile command.
        """
        # First, create the file to be deleted
        # ####################################
        cmd_count = tlm(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER")

        # Send CFE_SB_CMD_WRITE_ROUTING_INFO command
        cmd(f"<%= target_name %> CFE_SB_CMD_WRITE_ROUTING_INFO with FILENAME '/cf/file_rt.dat'")

        # Verify the command was successful
        wait_check(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        # ####################################

        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with PATH '/cf/file_rt.dat'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_06_DeleteAllFiles(self):
        """
        Test the DeleteAllFiles command.
        """
        # First, create the files to be deleted
        # ####################################
        cmd_count = tlm(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER")

        # Send CFE_SB_CMD_WRITE_ROUTING_INFO command
        cmd(f"<%= target_name %> CFE_SB_CMD_WRITE_ROUTING_INFO with FILENAME '/cf/file_rt1.dat'")

        # Verify the command was successful
        wait_check(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        cmd_count = tlm(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER")

        # Send CFE_SB_CMD_WRITE_ROUTING_INFO command
        cmd(f"<%= target_name %> CFE_SB_CMD_WRITE_ROUTING_INFO with FILENAME '/cf/file_rt2.dat'")

        # Verify the command was successful
        wait_check(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        # ####################################
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_DELETE_ALL_FILES with PATH '/cf/'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_07_DecompressFile(self):
        """
        Test the DecompressFile command.
        """

        # FIXME: This can't be tested until we have COSMOS CFDP working.
        
        # cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # # Send the command under test
        # cmd("<%= target_name %> FM_CMD_DECOMPRESS_FILE with SOURCE_PATH 'source.txt', TARGET_PATH 'target.txt'")
        
        # # Verify command count incremented
        # wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_08_ConcatFiles(self):
        """
        Test the ConcatFiles command.
        """

        # First, create the files to be concatenated
        # ####################################
        cmd_count = tlm(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER")

        # Send CFE_SB_CMD_WRITE_ROUTING_INFO command
        cmd(f"<%= target_name %> CFE_SB_CMD_WRITE_ROUTING_INFO with FILENAME '/cf/file_rt1.dat'")

        # Verify the command was successful
        wait_check(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        cmd_count = tlm(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER")

        # Send CFE_SB_CMD_WRITE_ROUTING_INFO command
        cmd(f"<%= target_name %> CFE_SB_CMD_WRITE_ROUTING_INFO with FILENAME '/cf/file_rt2.dat'")

        # Verify the command was successful
        wait_check(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        # ####################################
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_CONCAT_FILES with SOURCE_PATH1 '/cf/file_rt1.dat', SOURCE_PATH2 '/cf/file_rt2.dat', TARGET_PATH '/cf/file_rt3.dat'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Cleanup: Delete the files that were created
        # ############################################
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with PATH '/cf/file_rt1.dat'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with PATH '/cf/file_rt2.dat'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with PATH '/cf/file_rt3.dat'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_09_GetFileInfo(self):
        """
        Test the GetFileInfo command.
        """

        # First, create the file
        # ######################
        cmd_count = tlm(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER")

        # Send CFE_SB_CMD_WRITE_ROUTING_INFO command
        cmd(f"<%= target_name %> CFE_SB_CMD_WRITE_ROUTING_INFO with FILENAME '/cf/file_rt.dat'")

        # Verify the command was successful
        wait_check(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        # ######################
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_GET_FILE_INFO with PATH '/cf/file_rt.dat', CRC_METHOD CRC_NONE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Cleanup: Delete the file that was created
        # #########################################
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with PATH '/cf/file_rt.dat'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_10_GetOpenFiles(self):
        """
        Test the GetOpenFiles command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_GET_OPEN_FILES")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_11_CreateAndDeleteDirectory(self):
        """
        Test the CreateDirectory command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the CreateDirectory command
        cmd("<%= target_name %> FM_CMD_CREATE_DIRECTORY with PATH '/cf/new-directory'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the DeleteDirectory command
        cmd("<%= target_name %> FM_CMD_DELETE_DIRECTORY with PATH '/cf/new-directory'")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_12_GetDirListFile(self):
        """
        Test the GetDirListFile command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_GET_DIR_LIST_FILE with DIRECTORY_PATH '/cf/', OUTPUT_FILE_PATH 'dirlist.txt', GET_SIZE_TIME_MODE FALSE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_13_GetDirListPkt(self):
        """
        Test the GetDirListPkt command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_GET_DIR_LIST_PKT with PATH '/cf/', OFFSET 0, GET_SIZE_TIME_MODE FALSE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
    

    def test_14_MonitorFilesystemSpace(self):
        """
        Test the MonitorFilesystemSpace command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_MONITOR_FILESYSTEM_SPACE")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_15_SetTableState(self):
        """
        Test the SetTableState command.
        """
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_SET_TABLE_STATE with INDEX 0, STATE DISABLED")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_16_SetPermissions(self):
        """
        Test the SetPermissions command.
        """

        # First, create the file
        # ######################
        cmd_count = tlm(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER")

        # Send CFE_SB_CMD_WRITE_ROUTING_INFO command
        cmd(f"<%= target_name %> CFE_SB_CMD_WRITE_ROUTING_INFO with FILENAME '/cf/file_rt.dat'")

        # Verify the command was successful
        wait_check(f"<%= target_name %> CFE_SB_HK COMMAND_COUNTER == {cmd_count + 1}", 100)
        # ######################
        
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        
        # Send the command under test
        cmd("<%= target_name %> FM_CMD_SET_PERMISSIONS with PATH '/cf/file_rt.dat', PERMISSIONS 777")
        
        # Verify command count incremented
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)

        # Cleanup: Delete the file that was created
        # #########################################
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        cmd("<%= target_name %> FM_CMD_DELETE_FILE with PATH '/cf/file_rt.dat'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)


    def test_17_ResetCounters(self):
        """
        Test the ResetCounters command.
        """

        # Increment COMMAND_COUNTER and CHILD_COMMAND_COUNTER by sending CreateDirectory command
        cmd("<%= target_name %> FM_CMD_CREATE_DIRECTORY with PATH '/cf/new-directory'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER > 0", 100)
        wait_check(f"<%= target_name %> FM_HK CHILD_COMMAND_COUNTER > 0", 100)

        # Delete the created directory, for cleanup
        cmd_count = tlm(f"<%= target_name %> FM_HK COMMAND_COUNTER")
        cmd("<%= target_name %> FM_CMD_DELETE_DIRECTORY with PATH '/cf/new-directory'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER >= {cmd_count + 1}", 100)
        
        # Cause COMMAND_ERROR_COUNTER and CHILD_COMMAND_ERROR_COUNTER to increment,
        # by sending a DeleteDirectory command with a non-existant directory. 
        cmd("<%= target_name %> FM_CMD_DELETE_DIRECTORY with PATH '/ram/non-existant'")
        wait_check(f"<%= target_name %> FM_HK COMMAND_ERROR_COUNTER > 0", 100)
        wait_check(f"<%= target_name %> FM_HK CHILD_COMMAND_ERROR_COUNTER > 0", 100)

        # Cause CHILD_COMMAND_WARNING_COUNTER to increment,
        # by sending a DirListPkt command with an extremely-long directory/file path.
        cmd("<%= target_name %> FM_CMD_GET_DIR_LIST_PKT with PATH '/ram/path-too-long-path-too-long-path-too-long-path-too-long', OFFSET 0, GET_SIZE_TIME_MODE FALSE")
        wait_check(f"<%= target_name %> FM_HK CHILD_COMMAND_WARNING_COUNTER > 0", 100)

        # Send ResetCounters command
        cmd(f"<%= target_name %> FM_CMD_RESET_COUNTERS")
        
        # Verify counters are reset to zero
        wait_check(f"<%= target_name %> FM_HK COMMAND_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> FM_HK COMMAND_ERROR_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> FM_HK CHILD_COMMAND_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> FM_HK CHILD_COMMAND_ERROR_COUNTER == 0", 100)
        wait_check(f"<%= target_name %> FM_HK CHILD_COMMAND_WARNING_COUNTER == 0", 100)


    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        # Wait for a new housekeeping packet, to ensure we're using its latest status info
        wait_check_packet(f"<%= target_name %>", "FM_HK", 1, 100)

        # Ensure that FM events are enabled
        cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_APP_EVENTS with APP_NAME 'FM'")
        wait(1)
        
        # Ensure that DEBUG and INFO events are enabled
        cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_EVENT_TYPE with BIT_MASK DEBUG")
        cmd("<%= target_name %> CFE_EVS_CMD_ENABLE_EVENT_TYPE with BIT_MASK INFO")
        wait(1)
        pass


    def teardown(self):
        """
        Test Group Setup
        - Runs when Group Teardown button is pressed
        - Runs after all scripts when Group Start is pressed
        """
        pass
