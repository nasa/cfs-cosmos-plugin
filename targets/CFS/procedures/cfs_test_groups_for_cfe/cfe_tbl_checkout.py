from openc3.script.suite import Group

# Group class name should indicate what the scripts are testing
class cfs_test_group_cfe_tbl_checkout(Group):
    """
    - Methods beginning with script_ or test_ are added to Script dropdown
    """

    def test_cfe_tbl_checkout(self):
        """
        CFE TBL Checkout Test
        -Send all TBL commands as quickly as possible, then verify all were accepted
        """

        set_line_delay(0.0)

        Group.print(f"CFE_TBL checkout test on <%= target_name %>")

        # Save initial command counts
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")
        cmd_err_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_ERROR_COUNTER")

        set_line_delay(0.15)  # 0.15 is about as fast as it can go.  0.1 causes a missed cmd.

        cmd(f"<%= target_name %> CFE_TBL_CMD_NOOP")
        test_table_name = "DS.FILE_TBL"
        test_table_filename = "/cf/ds_file_tbl.tbl"
        cmd(f"<%= target_name %> CFE_TBL_CMD_LOAD with LOAD_FILENAME '{test_table_filename}'")
        cmd(f"<%= target_name %> CFE_TBL_CMD_VALIDATE with ACTIVE_TABLE_FLAG INACTIVE, TABLE_NAME '{test_table_name}'")
        cmd(f"<%= target_name %> CFE_TBL_CMD_ACTIVATE with TABLE_NAME '{test_table_name}'")
        test_table_name = "HK.CopyTable"
        test_table_filename = "/cf/hk_cpy_tbl.tbl"
        cmd(f"<%= target_name %> CFE_TBL_CMD_LOAD with LOAD_FILENAME '{test_table_filename}'")
        cmd(f"<%= target_name %> CFE_TBL_CMD_VALIDATE with ACTIVE_TABLE_FLAG INACTIVE, TABLE_NAME '{test_table_name}'")
        test_table_name = "TO_LAB.Subscriptions"
        test_table_filename = "/cf/to_lab_sub_bad.tbl"
        cmd(f"<%= target_name %> CFE_TBL_CMD_LOAD with LOAD_FILENAME '{test_table_filename}'")
        cmd(f"<%= target_name %> CFE_TBL_CMD_VALIDATE with ACTIVE_TABLE_FLAG INACTIVE, TABLE_NAME '{test_table_name}'")
        cmd(f"<%= target_name %> CFE_TBL_CMD_ABORT_LOAD with TABLE_NAME '{test_table_name}'")
        cmd(f"<%= target_name %> CFE_TBL_CMD_DUMP_REGISTRY with DUMP_FILENAME 'dump_registry.dat'")
        cmd(f"<%= target_name %> CFE_TBL_CMD_SEND_REGISTRY with TABLE_NAME 'MD.DWELL_TABLE4'")
        cmd(f"<%= target_name %> CFE_ES_CMD_STOP_APP with APPLICATION 'MD'")
        wait(10)
        cmd(f"<%= target_name %> CFE_TBL_CMD_DELETE_CDS with TABLE_NAME 'MD.DWELL_TABLE4'")

        set_line_delay(0.0)
        
        # Check final command count has incremented by the number of commands sent
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER >= {cmd_count} + 12", 12)
        check(f"<%= target_name %> CFE_TBL_HK COMMAND_ERROR_COUNTER == {cmd_err_count}")

        cmd(f"<%= target_name %> CFE_TBL_CMD_RESET_COUNTERS")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER == 0", 12)


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
