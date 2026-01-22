from openc3.script.suite import Group

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfe_tbl(Group):
    """
    - Methods beginning with script_ or test_ are added to Script dropdown
    """

    def test_aliveness(self):
        """
        FSW Aliveness Test
        - Send a no-op command
            then verify the command was received (by checking the command counter incremented)
        - Reset the command counter
            then verify the command was received (by checking the command counter was cleared)
        """
        app_name = "CFE_TBL"

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

    def test_load_validate_table(self):
        """
        Test Load Table
        - Send a load command
            then verify the command was received (by checking the command counter incremented)
            and then send a validate command
        """
        app_name = "CFE_TBL"

        Group.print(f"Testing {app_name} Load and Validate Table on <%= target_name %>")

        # Restart MD to load table without buffer error
        cmd(f"<%= target_name %> CFE_ES_CMD_RESTART_APP with APPLICATION 'MD'")
        wait(10)

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"{app_name}_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER")

        # Check accepted Load command
        cmd(f"<%= target_name %> {app_name}_CMD_LOAD with LOAD_FILENAME '/cf/md_dw04.tbl'")
        wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Check accepted Validate command
        # Makes MD table active
        cmd_count = tlm(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> {app_name}_CMD_VALIDATE with ACTIVE_TABLE_FLAG INACTIVE, TABLE_NAME 'MD.DWELL_TABLE4'")
        wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Check accepted Validate command
        cmd_count = tlm(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER")
        cmd(f"<%= target_name %> {app_name}_CMD_VALIDATE with ACTIVE_TABLE_FLAG ACTIVE, TABLE_NAME 'MD.DWELL_TABLE4'")
        wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

    def test_abort_table(self):
        """
        Test Abort Table
        - Send a load command
            then verify the command was received (by checking the command counter incremented)
        - Send a abort command
            then verify the command was received (by checking the command counter incremented)
        """
        app_name = "CFE_TBL"

        Group.print(f"Testing {app_name} Abort Table on <%= target_name %>")
        # Restart MD to load table without buffer error
        cmd(f"<%= target_name %> CFE_ES_CMD_RESTART_APP with APPLICATION 'MD'")
        wait(10)

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"{app_name}_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER")

        # Check accepted Load command
        cmd(f"<%= target_name %> {app_name}_CMD_LOAD with LOAD_FILENAME '/cf/md_dw04.tbl'")
        wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Check accepted Abort command
        cmd_count = tlm(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER")
        cmd("<%= target_name %> CFE_TBL_CMD_ABORT_LOAD with TABLE_NAME 'MD.DWELL_TABLE4'")
        wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

    def test_dump_table_registry(self):
        """
        Test Dump Table Registry
        - Send a dump registry command
            then verify the command was received (by checking the command counter incremented)
        """
        app_name = "CFE_TBL"

        Group.print(f"Testing {app_name} Dump Table Registry on <%= target_name %>")

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"{app_name}_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER")

        # Check accepted Dump Registry command
        cmd(f"<%= target_name %> {app_name}_CMD_DUMP_REGISTRY with DUMP_FILENAME 'dump_registry.dat'")
        wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

    def test_send_table_registry(self):
        """
        Test Send Table Registry
        - Send a send registry command
            then verify the command was received (by checking the command counter incremented)
        """
        app_name = "CFE_TBL"

        Group.print(f"Testing {app_name} Send Table Registry on <%= target_name %>")

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"{app_name}_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER")

        # Check accepted Send Registry command
        cmd(f"<%= target_name %> {app_name}_CMD_SEND_REGISTRY with TABLE_NAME 'MD.DWELL_TABLE4'")
        wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

    def test_delete_cds(self):
        """
        Test Delete CDS Registry
        - Send a delete cds command
            then verify the command was received (by checking the command counter incremented)
        """
        app_name = "CFE_TBL"

        Group.print(f"Testing {app_name} Send Delete CDS on <%= target_name %>")

        # Verify that we have a recent packet (by waiting for a new one to arrive)
        wait_check_packet(f"<%= target_name %>", f"{app_name}_HK", 1, 100)

        # Assuming no one else is sending commands, grab the latest command count
        cmd_count = tlm(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER")

        # Stop MD
        cmd(f"<%= target_name %> CFE_ES_CMD_STOP_APP with APPLICATION 'MD'")
        wait(10)

        # Check accepted Delete CDS command
        cmd(f"<%= target_name %> {app_name}_CMD_DELETE_CDS with TABLE_NAME 'MD.DWELL_TABLE4'")
        wait_check(f"<%= target_name %> {app_name}_HK COMMAND_COUNTER == {cmd_count + 1}", 100)

        # Start MD
        cmd(f"<%= target_name %> CFE_ES_CMD_START_APP with APPLICATION 'MD', APP_ENTRY_POINT 'MD_AppMain', APP_FILE_NAME '/cf/md.so'")
        wait(10)
        cmd(f"<%= target_name %> CFE_ES_CMD_RESTART_APP with APPLICATION 'MD'")
        wait(10)

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
