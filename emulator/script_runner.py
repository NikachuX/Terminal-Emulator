import os

def load_script_lines(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            s = raw.rstrip("\n")
            if not s.strip():
                continue
            if s.lstrip().startswith("#"):
                lines.append(("comment", s.lstrip()))
            else:
                lines.append(("cmd", s))
    return lines

# функция запускает команды по очереди с отложенным вызовом
def run_script(shell, path, delay=200):
    items = load_script_lines(path)
    idx = 0
    def step():
        nonlocal idx
        if idx >= len(items):
            shell.show_output("=== Конец скрипта ===")
            return
        typ, content = items[idx]
        if typ == "cmd":
            shell.execute_command(command_line=content)
        idx += 1
        if shell.winfo_exists():
            shell.after(delay, step)
    step()
