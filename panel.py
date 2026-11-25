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

    violet = "#5750D8"
    navy = "#1F2246"
    muted = "#51567C"
    card_background = "#F8F7FF"

    root = tk.Tk()
    root.title("Serial Panel Lab")
    root.configure(background=violet)
    root.minsize(590, 390)

    body_font = ("TkDefaultFont", 11)
    label_font = ("TkDefaultFont", 11, "bold")

    content = tk.Frame(root, background=violet, padx=26, pady=22)
    content.pack(fill="both", expand=True)
    tk.Label(
        content, text="Temperature logger", font=("TkDefaultFont", 25, "bold"),
        background=violet, foreground="#FFFFFF",
    ).pack(anchor="w")
    tk.Label(
        content, text="Serial Panel Lab simulator", font=body_font,
        background=violet, foreground="#F2EFFF",
    ).pack(anchor="w", pady=(0, 16))

    dashboard = tk.Frame(content, background=card_background, padx=18, pady=15)
    dashboard.pack(fill="both", expand=True)

    temperature = tk.StringVar(value="— °C")
    state = tk.StringVar(value="Idle")
    reply_text = tk.StringVar(value="Ready")

    metrics = tk.Frame(dashboard, background=card_background)
    metrics.pack(fill="x")
    metrics.columnconfigure((0, 1), weight=1, uniform="metrics")

    for column, (caption, value, background, size) in enumerate((
        ("TEMPERATURE", temperature, "#E4F2FF", 31),
        ("LOGGER STATUS", state, "#DEF3E5", 24),
    )):
        tile = tk.Frame(metrics, background=background, padx=14, pady=8)
        tile.grid(row=0, column=column, sticky="nsew", padx=(0, 8) if column == 0 else (8, 0))
        tk.Label(
            tile, text=caption, background=background, foreground=muted, font=label_font,
        ).pack(anchor="w")
        tk.Label(
            tile, textvariable=value, background=background, foreground=navy,
            font=("TkDefaultFont", size, "bold"),
        ).pack(anchor="w")

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Panel.TFrame", background=card_background)
    buttons = ttk.Frame(dashboard, style="Panel.TFrame")
    buttons.pack(fill="x", pady=16)
    buttons.columnconfigure((0, 1, 2, 3), weight=1)

    tk.Label(
        dashboard, text="SIMULATOR RESPONSE", background=card_background,
        foreground=muted, font=label_font,
    ).pack(anchor="w")
    response = tk.Label(
        dashboard, textvariable=reply_text, anchor="w", padx=12, pady=8,
        background="#ECE9FB", foreground=navy, font=("TkFixedFont", 11),
    )
    response.pack(fill="x", pady=(4, 0))

    def send(command, corrupt=False):
        try:
            reply = connection.exchange(command, corrupt=corrupt)
        except OSError as error:
            reply_text.set(str(error))
            response.configure(background="#FFE4DB")
            return
        reply_text.set(reply)
        response.configure(background="#FFE4DB" if reply.startswith("ERR ") else "#DEF3E5")
        if reply.startswith("OK TEMP "):
            temperature.set(f"{reply.split()[-1]} °C")
        elif reply == "OK RECORDING":
            state.set("Recording")
        elif reply == "OK IDLE":
            state.set("Idle")

    for column, (label, command, corrupt, background, active) in enumerate((
        ("Start", "BEGIN", False, "#FFC64F", "#FFDA85"),
        ("Read", "READ", False, "#85C9F5", "#ADE0FF"),
        ("Stop", "END", False, "#FFA18E", "#FFC3B6"),
        ("Send bad frame", "END", True, "#E7DFFF", "#F4EEFF"),
    )):
        button_style = f"Panel{column}.TButton"
        style.configure(
            button_style, background=background, foreground=navy,
            bordercolor=violet, focuscolor=navy, font=label_font, padding=(10, 9),
        )
        style.map(button_style, background=[("pressed", active), ("active", active)])
        ttk.Button(
            buttons, style=button_style, text=label,
            command=lambda c=command, b=corrupt: send(c, b),
        ).grid(row=0, column=column, sticky="ew", padx=3)
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
