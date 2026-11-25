"""Desktop controls for a simulated temperature logger."""

import argparse
from pathlib import Path
import subprocess


def encode_request(command, *, corrupt=False):
    payload = command.encode("ascii")
    checksum = 0
    for byte in payload:
        checksum ^= byte
        for _ in range(8):
            checksum = ((checksum << 1) ^ (0x07 if checksum & 0x80 else 0)) & 0xFF
    if corrupt:
        checksum ^= 1
    return f"{command} *{checksum:02X}\n"


class LoggerConnection:
    def __init__(self, executable):
        self.process = subprocess.Popen(
            [str(executable.resolve())], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            text=True, encoding="ascii",
        )

    def exchange(self, command, *, corrupt=False):
        self.process.stdin.write(encode_request(command, corrupt=corrupt))
        self.process.stdin.flush()
        reply = self.process.stdout.readline()
        if not reply:
            raise OSError("The simulator closed its output.")
        return reply.rstrip("\n")

    def __enter__(self):
        return self

    def __exit__(self, *_exception):
        try:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        finally:
            self.process.stdout.close()


def run_demo(connection):
    scenarios = [
        ("Read while idle", "READ", False, "ERR IDLE"),
        ("Start logging", "BEGIN", False, "OK RECORDING"),
        ("Read temperature", "READ", False, "OK TEMP 21.8"),
        ("Send corrupted stop frame", "END", True, "ERR FRAME"),
        ("Read after rejection", "READ", False, "OK TEMP 22.1"),
        ("Stop logging", "END", False, "OK IDLE"),
    ]
    for label, command, corrupt, expected in scenarios:
        reply = connection.exchange(command, corrupt=corrupt)
        print(f"{label}: {reply}")
        if reply != expected:
            raise RuntimeError(f"Expected {expected!r}, received {reply!r}")


def show_panel(connection):
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Serial Panel Lab")
    root.minsize(430, 230)
    content = ttk.Frame(root, padding=20)
    content.pack(fill="both", expand=True)

    ttk.Label(content, text="Temperature logger", font=("TkDefaultFont", 18)).pack(anchor="w")
    temperature = tk.StringVar(value="— °C")
    state = tk.StringVar(value="Idle")
    reply_text = tk.StringVar(value="Ready")
    ttk.Label(content, textvariable=temperature, font=("TkDefaultFont", 30)).pack(anchor="w", pady=(8, 0))
    ttk.Label(content, textvariable=state).pack(anchor="w")
    buttons = ttk.Frame(content)
    buttons.pack(anchor="w", pady=12)

    def send(command, corrupt=False):
        try:
            reply = connection.exchange(command, corrupt=corrupt)
        except OSError as error:
            reply_text.set(str(error))
            return
        reply_text.set(reply)
        if reply.startswith("OK TEMP "):
            temperature.set(f"{reply.split()[-1]} °C")
        elif reply == "OK RECORDING":
            state.set("Recording")
        elif reply == "OK IDLE":
            state.set("Idle")

    for label, command, corrupt in (
        ("Start", "BEGIN", False), ("Read", "READ", False),
        ("Stop", "END", False), ("Send bad frame", "END", True),
    ):
        ttk.Button(
            buttons, text=label, command=lambda c=command, b=corrupt: send(c, b)
        ).pack(side="left", padx=(0, 5))
    ttk.Label(content, textvariable=reply_text).pack(anchor="w")
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", type=Path, default=Path(__file__).resolve().parent / "build/temperature-node")
    parser.add_argument("--demo", action="store_true", help="Run the headless demo")
    options = parser.parse_args()
    try:
        with LoggerConnection(options.node) as connection:
            if options.demo:
                run_demo(connection)
            else:
                show_panel(connection)
    except (OSError, RuntimeError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
