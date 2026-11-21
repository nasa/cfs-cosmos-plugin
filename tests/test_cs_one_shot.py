"""Offline checks for the one-shot procedure's command and telemetry sequencing."""

import ast
from pathlib import Path
import re
from types import ModuleType
import unittest
from unittest.mock import patch


PROCEDURE = Path(__file__).resolve().parents[1] / (
    "targets/CFS/procedures/cfs_test_groups_for_cfs_open_src/cfs_cs.py"
)


class OneShotTarget:
    """Model delayed HK delivery and a one-byte-per-cycle child, without real hardware."""

    def __init__(self, address=0x123456780, count=0, complete=True):
        self.address = address
        self.complete = complete
        self.commands = []
        self.checks = []
        self.events = []
        self.remaining = 0
        self.fail_size_check = False
        self.reject_lookup = False
        self.actual = {
            "MM_HK": {"COMMAND_COUNTER": count, "LAST_ACTION": "NO_ACTION", "ADDRESS": 0},
            "CS_HK": {
                "COMMAND_COUNTER": count, "COMMAND_ERROR_COUNTER": 0,
                "RECOMPUTE_IN_PROGRESS": 0, "ONE_SHOT_IN_PROGRESS": 0,
                "LAST_ONE_SHOT_ADDRESS": 0, "LAST_ONE_SHOT_SIZE": 0,
                "LAST_ONE_SHOT_MAX_BYTES_PER_CYCLE": 0,
            },
        }
        self.telemetry = {packet: dict(values) for packet, values in self.actual.items()}

    def publish(self):
        if self.remaining and self.complete:
            self.remaining -= 1
            if not self.remaining:
                self.actual["CS_HK"]["ONE_SHOT_IN_PROGRESS"] = 0
        self.telemetry = {packet: dict(values) for packet, values in self.actual.items()}

    def tlm(self, query):
        target, packet, field = query.split()
        assert target in ("CFS-1", "CFS-2")
        return self.telemetry[packet][field]

    def cmd(self, command):
        self.commands.append(command)
        self.events.append(command)
        _, name, *rest = command.split()
        if name == "MM_CMD_LOOKUP_SYM":
            assert "SYMNAME 'SAMPLE_LIB_Buffer'" in command
            if not self.reject_lookup:
                hk = self.actual["MM_HK"]
                hk.update(COMMAND_COUNTER=(hk["COMMAND_COUNTER"] + 1) % 256,
                          LAST_ACTION="SYM_LOOKUP", ADDRESS=self.address)
        elif name == "CS_CMD_ONE_SHOT":
            match = re.search(r"ADDRESS (\d+), SIZE (\d+), MAX_BYTES_PER_CYCLE (\d+)", command)
            assert match is not None
            address, size, per_cycle = map(int, match.groups())
            assert address == self.address and address != 0
            assert size == 16 and per_cycle == 1
            hk = self.actual["CS_HK"]
            assert not hk["ONE_SHOT_IN_PROGRESS"] and not hk["RECOMPUTE_IN_PROGRESS"]
            hk.update(COMMAND_COUNTER=(hk["COMMAND_COUNTER"] + 1) % 256,
                      ONE_SHOT_IN_PROGRESS=1, LAST_ONE_SHOT_ADDRESS=address,
                      LAST_ONE_SHOT_SIZE=size, LAST_ONE_SHOT_MAX_BYTES_PER_CYCLE=per_cycle)
            self.remaining = size
        elif name == "CS_SEND_HK_CMD":
            self.publish()
        elif name == "CS_CMD_CANCEL_ONE_SHOT":
            hk = self.actual["CS_HK"]
            assert hk["ONE_SHOT_IN_PROGRESS"], "Cancel sent after the one-shot already finished"
            hk["COMMAND_COUNTER"] = (hk["COMMAND_COUNTER"] + 1) % 256
            hk["ONE_SHOT_IN_PROGRESS"] = 0
            self.remaining = 0
        else:
            raise AssertionError(f"Unexpected command: {command}")

    def wait_check_packet(self, target, packet, count, timeout):
        self.publish()

    def wait_check(self, expression, timeout):
        self.checks.append(expression)
        self.events.append(expression)
        query, expected = expression.split(" == ")
        if self.fail_size_check and query.endswith("LAST_ONE_SHOT_SIZE"):
            raise AssertionError("injected size-check failure")
        expected = ast.literal_eval(expected)
        for _ in range(timeout + 1):
            if self.tlm(query) == expected:
                return
            self.publish()
        raise AssertionError(f"Timed out: {expression}")

    def group(self, target="CFS-1"):
        modules = {name: ModuleType(name) for name in ["openc3", "openc3.script", "openc3.script.suite"]}
        modules["openc3.script.suite"].Group = object
        namespace = {name: getattr(self, name) for name in ["tlm", "cmd", "wait_check", "wait_check_packet"]}
        source = PROCEDURE.read_text().replace("<%= target_name %>", target)
        with patch.dict("sys.modules", modules):
            exec(compile(source, str(PROCEDURE), "exec"), namespace)
        return namespace["cfs_test_group_cfs_cs"]()


class OneShotProcedureTests(unittest.TestCase):
    def test_natural_completion_and_target_selection(self):
        for target in ["CFS-1", "CFS-2"]:
            with self.subTest(target=target):
                model = OneShotTarget()
                model.group(target).test_02_OneShot()
                self.assertTrue(any("ONE_SHOT_IN_PROGRESS == 1" in check for check in model.checks))
                self.assertFalse(any("CANCEL_ONE_SHOT" in command for command in model.commands))
                self.assertFalse(model.actual["CS_HK"]["ONE_SHOT_IN_PROGRESS"])

    def test_cancel_follows_observed_start(self):
        model = OneShotTarget()
        model.group().test_03_CancelOneShot()
        self.assertEqual(sum("CANCEL_ONE_SHOT" in command for command in model.commands), 1)
        self.assertLess(model.events.index("CFS-1 CS_HK ONE_SHOT_IN_PROGRESS == 1"),
                        model.events.index("CFS-1 CS_CMD_CANCEL_ONE_SHOT"))
        self.assertFalse(model.actual["CS_HK"]["ONE_SHOT_IN_PROGRESS"])

    def test_command_counters_wrap(self):
        for method in ["test_02_OneShot", "test_03_CancelOneShot"]:
            for count in [254, 255]:
                with self.subTest(method=method, count=count):
                    model = OneShotTarget(count=count)
                    getattr(model.group(), method)()

    def test_zero_address_never_starts_checksum(self):
        model = OneShotTarget(address=0)
        with self.assertRaisesRegex(RuntimeError, "usable address"):
            model.group().test_02_OneShot()
        self.assertFalse(any("CS_CMD_ONE_SHOT" in command for command in model.commands))

    def test_failed_lookup_never_starts_checksum(self):
        model = OneShotTarget()
        model.reject_lookup = True
        with self.assertRaisesRegex(AssertionError, "Timed out"):
            model.group().test_02_OneShot()
        self.assertFalse(any("CS_CMD_ONE_SHOT" in command for command in model.commands))

    def test_failed_check_cancels_owned_child(self):
        model = OneShotTarget()
        model.fail_size_check = True
        with self.assertRaisesRegex(AssertionError, "injected size-check failure"):
            model.group().test_02_OneShot()
        self.assertFalse(model.actual["CS_HK"]["ONE_SHOT_IN_PROGRESS"])
        self.assertEqual(sum("CANCEL_ONE_SHOT" in command for command in model.commands), 1)

    def test_completion_timeout_cancels_owned_child(self):
        model = OneShotTarget(complete=False)
        with self.assertRaisesRegex(AssertionError, "Timed out"):
            model.group().test_02_OneShot()
        self.assertFalse(model.actual["CS_HK"]["ONE_SHOT_IN_PROGRESS"])


if __name__ == "__main__":
    unittest.main()
