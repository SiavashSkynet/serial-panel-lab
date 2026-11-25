from pathlib import Path
import subprocess
import unittest

from panel import LoggerConnection, encode_request


NODE = Path(__file__).resolve().parents[1] / "build/temperature-node"


class LoggerTests(unittest.TestCase):
    def test_crc8_reference_vector(self):
        self.assertEqual(encode_request("123456789"), "123456789 *F4\n")

    def test_invalid_commands_and_state_transitions(self):
        with LoggerConnection(NODE) as logger:
            self.assertEqual(logger.exchange("READ"), "ERR IDLE")
            self.assertEqual(logger.exchange("BEGIN"), "OK RECORDING")
            self.assertEqual(logger.exchange("READ"), "OK TEMP 21.8")
            self.assertEqual(logger.exchange("END", corrupt=True), "ERR FRAME")
            self.assertEqual(logger.exchange("READ"), "OK TEMP 22.1")
            self.assertEqual(logger.exchange("UNKNOWN"), "ERR COMMAND")
            self.assertEqual(logger.exchange("END"), "OK IDLE")
            self.assertEqual(logger.exchange("READ"), "ERR IDLE")

    def test_malformed_lines_do_not_swallow_next_request(self):
        request = "x" * 100 + "\n" + "bad\0frame\n" + encode_request("BEGIN") + "partial"
        result = subprocess.run(
            [str(NODE)], input=request, text=True, capture_output=True, check=True, timeout=2,
        )
        self.assertEqual(
            result.stdout.splitlines(), ["ERR FRAME", "ERR FRAME", "OK RECORDING", "ERR FRAME"],
        )


if __name__ == "__main__":
    unittest.main()
