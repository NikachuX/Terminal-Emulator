import tkinter as tk
import getpass
import socket
import shlex

class TerminalEmulator(tk.Tk):
    def __init__(self):
        super().__init__()
        username = getpass.getuser()
        hostname = socket.gethostname()
        self.title(f"Эмулятор - [{username}@{hostname}]")
        self.geometry("800x450")

        self.output = tk.Text(self, wrap="word", bg="black", fg="white", insertbackground="white", state="disabled")
        self.output.pack(fill="both", expand=True)

        self.entry = tk.Entry(self, bg="black", fg="white", insertbackground="white")
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", self.execute_command)

        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }

    def show_output(self, text: str):
        """Вывод текста в эмулятор"""
        self.output.config(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.config(state="disabled")

    def execute_command(self, event):
        command_line = self.entry.get().strip()
        if not command_line:
            return
        self.show_output(f"$ {command_line}")
        self.entry.delete(0, tk.END)

        try:
            parts = shlex.split(command_line)
        except ValueError as e:
            self.show_output(f"Ошибка парсинга команды: {e}")
            return

        cmd = parts[0]
        args = parts[1:]

        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            self.show_output(f"Команда '{cmd}' не найдена")


    def cmd_ls(self, args):
        self.show_output(f"Выполнена команда: ls, аргументы: {args}")

    def cmd_cd(self, args):
        self.show_output(f"Выполнена команда: cd, аргументы: {args}")

    def cmd_exit(self, args):
        if args:
            self.show_output("exit: команда не принимает аргументы")
            return
        self.destroy()


if __name__ == "__main__":
    app = TerminalEmulator()
    app.mainloop()