import os

# Завершение работы эмулятора
def cmd_exit(shell, vfs, args):
    if args:
        shell.show_output("exit: не принимает аргументы")
        return
    shell.show_output("Выход...")
    shell.after(300, shell.destroy)


# Показ содержимого каталога
def cmd_ls(shell, vfs,  args):
    targets = args if args else ["."]
    for t in targets:
        try:
            node = vfs.resolve_path(t)
        except FileNotFoundError:
            shell.show_output(f"ls: cannot access '{t}': No such file or directory")
            continue
        if node["type"] == "dir":
            for name in sorted(node["children"].keys()):
                child = node["children"][name]
                mark = "/" if child["type"] == "dir" else ""
                shell.show_output(f"{name}{mark}")
        else:
            shell.show_output("(file)")


# Смена текущей директори
def cmd_cd(shell, vfs, args):
    if len(args) == 1:
        try:
            node = vfs.resolve_path(args[0])
            if node["type"] != "dir":
                shell.show_output(f"cd: {args[0]}: Not a directory")
                return

            # обновляем текущий путь
            vfs.curr = node["path"]
        except FileNotFoundError:
            shell.show_output(f"cd: {args[0]}: No such file or directory")
    else:
        shell.show_output("cd: too many arguments")


# Вывод содержимого файла в обратном порядке строк
def cmd_tac(shell, vfs, args):
    if len(args) > 1:
        shell.show_output("too many arguments")
        return
    try:
        node = vfs.resolve_path(args[0])
    except FileNotFoundError:
        shell.show_output(f"tac: cannot open {args[0]} for reading: No such file or directory")
        return

    path = node["real_path"]
    if not os.path.isdir(path):
        # читаем строки и переворачиваем порядок
        with open(path, "r", encoding='utf-8') as file:
            lines = [i.replace("\n", "") for i in file.readlines()]
            for line in reversed(lines):
                shell.show_output(line)
    else:
        shell.show_output(f"tac: error reading {args[0]}: Is a directory")


# Вывод последних N строк файла
def cmd_tail(shell, vfs, args):
    n = 10 # по умолчанию 10 строк
    ind_file = 0
    if len(args) > 3:
        shell.show_output("too many arguments")
        return
    if len(args) == 2:
        shell.show_output("wrong args")
        return
    if len(args) == 3:
        ind_file = 2
        if args[0] == "-n":
            try:
                n = int(args[1])
            except:
                shell.show_output(f"wrong args {args[1]}")
                return
        else:
            shell.show_output(f"tail: wrong arg {args[0]}")
            return
    try:
        node = vfs.resolve_path(args[ind_file])
    except FileNotFoundError:
        shell.show_output(f"tail: cannot open {args[ind_file]} for reading: No such file or directory")
        return

    path = node["real_path"]
    if not os.path.isdir(path):
            with open(path, "r", encoding='utf-8') as file:
                lines = [i.replace("\n", "") for i in file.readlines()[-n:]]
                for line in lines:
                    shell.show_output(line)
    else:
        shell.show_output(f"tail: error reading {args[ind_file]}: Is a directory")


# Показать текущую рабочую директорию
def cmd_pwd(shell, vfs, args):
    if vfs.curr == vfs.root:
        path = "/"
    else:
        path = vfs.curr.replace(vfs.root, "").replace("\\", "/")
    shell.show_output(path)


# Создание пустого файла
def cmd_touch(shell, vfs, args):
    if not args:
        shell.show_output("touch: missing file operand")
        return

    for arg in args:
        directory, separator, filename = arg.rpartition("/")
        try:
            node = vfs.resolve_path(directory)
        except FileNotFoundError:
            shell.show_output(f"touch: cannot touch {arg}: No such file or directory")
            return
        # создаём новый узел-файл
        new_node = {"type": "file", "path": os.path.join(node["path"], filename), "real_path": os.path.join(node["path"], filename)}
        node["children"][filename] = new_node


# Перемещение/переименование файлов и директорий
def cmd_mv(shell, vfs, args):
    if len(args) != 2:
        shell.show_output("mv: requires exactly two arguments")
        return
    directory, _, filename = args[0].rpartition("/")
    try:
        vfs.resolve_path(args[0]) # проверяем, существует ли источник
    except FileNotFoundError:
        shell.show_output(f"mv: cannot stat '{args[0]}': No such file or directory")
        return
    directory = directory or "."
    source_node = vfs.resolve_path(directory)["children"].pop(filename)
    try:
        target_node = vfs.resolve_path(args[1]) # пробуем найти цель
        new_target_path = target_node["path"]
        if target_node["type"] == "dir":
            # перемещаем внутрь директории
            target_node["children"][filename] = source_node
        else:
            if source_node["type"] == "file" and target_node["type"] == "file":
                # замена файла файлом
                target_node["real_path"] = source_node["real_path"]
                return
            else:
                shell.show_output(f"mv: cannot overwrite non-directory {args[1]} with directory {args[0]}")
                vfs.resolve_path(directory)["children"][filename] = source_node
                return

    except FileNotFoundError:
        # если цель не существует — создаём новый файл
        try:
            target_directory, _, target_filename =  args[1].rpartition("/")
            target_node = vfs.resolve_path(target_directory)
        except FileNotFoundError:
            shell.show_output(f"mv: cannot stat '{args[1]}': No such file or directory")
            return
        if source_node["type"] == "file":
            cmd_touch(shell, vfs, [args[1]])
            target_node["children"][target_filename]["real_path"] = source_node["real_path"]
            return
        else:
            shell.show_output(f"mv: cannot overwrite non-directory {args[1]} with directory {args[0]}")
            vfs.resolve_path(directory)["children"][filename] = source_node
            return

    # обновляем пути рекурсивно для директорий
    def update_paths_recursive(node, change_path, name="", where=""):
        new_path = str(os.path.join(change_path, filename))
        if where == "recurs":
            new_path = os.path.join(new_path, name)
        node["path"] = new_path
        if node["type"] == "dir":
            for child_name, child_node in node["children"].items():
                update_paths_recursive(child_node, change_path, child_name, "recurs")

    # Обновляем пути рекурсивно
    update_paths_recursive(source_node, new_target_path)
    shell.show_output(f"Moved {args[0]} to {args[1]}")


# Список доступных команд по умолчанию
def get_default_commands():
    return {
        "exit": cmd_exit,
        "ls": cmd_ls,
        "cd": cmd_cd,
        "tail": cmd_tail,
        "pwd": cmd_pwd,
        "tac": cmd_tac,
        "mv": cmd_mv,
        "touch": cmd_touch,
    }
