import tkinter as tk
import getpass
import socket
import shlex
import argparse
import os

class TerminalEmulator(tk.Tk):
    def __init__(self, vfs_path, script_path):
        super().__init__()
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.title(f"Эмулятор - [{self.username}@{self.hostname}]")
        self.geometry("800x450")

        # Текстовое поле для вывода
        self.output = tk.Text(self, wrap="word", bg="black", fg="white", insertbackground="white", state="disabled")
        self.output.pack(fill="both", expand=True)

        # Поле ввода команд
        self.entry = tk.Entry(self, bg="black", fg="white", insertbackground="white")
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", self.execute_command)

        # Таблица команд
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }

        if vfs_path:
            self.show_output("[DEBUG] Путь к VFS: " + str(vfs_path))

        if script_path:
            self.show_output("[DEBUG] Путь к стартовому скрипту: " + str(script_path))
            self.run_script(script_path)

    def show_output(self, text: str):
        """Вывод текста в эмулятор"""
        self.output.config(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.config(state="disabled")

    def execute_command(self, event=None, command_line=None):
        if command_line is None:
            command_line = self.entry.get().strip()
        if not command_line:
            return
        self.show_output(f"$ {command_line}")
        if event:
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


    def run_script(self, script_path):
        """Чтение и выполнение скрипта"""
        if not os.path.exists(script_path):
            self.show_output(f"[ERROR] Скрипт '{script_path}' не найден")
            return

        with open(script_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                self.execute_command(command_line=line)

    # ==== Команды ====
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
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--vfs", help="Путь к виртуальной файловой системе", required=True)
    parser.add_argument("--script", help="Путь к стартовому скрипту", required=False)
    args = parser.parse_args()

    app = TerminalEmulator(vfs_path=args.vfs, script_path=args.script)
    app.mainloop()