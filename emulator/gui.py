import tkinter as tk
import getpass, socket, shlex
from .commands import get_default_commands

class ShellEmulator(tk.Tk):
    def __init__(self, vfs):
        super().__init__()
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.title(f"Эмулятор - [{self.username}@{self.hostname}]")

        self.output = tk.Text(self, state="disabled", bg="black", fg="white")
        self.output.pack(fill="both", expand=True)
        self.entry = tk.Entry(self, bg="black", fg="white")
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", lambda e: self.execute_command())

        self.vfs = vfs

        # команды
        self.commands = get_default_commands()

    def show_output(self, text):
        self.output.config(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.config(state="disabled")


    def execute_command(self, event=None, command_line=None):
        if command_line is None:
            command_line = self.entry.get().strip()
            self.entry.delete(0, "end")
        if not command_line: return
        self.show_output(f"$ {command_line}")
        parts = shlex.split(command_line)
        cmd = parts[0]
        args = parts[1:]
        handler = self.commands.get(cmd)
        if handler:
            handler(self, self.vfs, args)
        else:
            self.show_output(f"Команда '{cmd}' не найдена")
