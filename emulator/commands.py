import os


def cmd_exit(shell, vfs, args):
    if args:
        shell.show_output("exit: не принимает аргументы")
        return
    shell.show_output("Выход...")
    shell.after(200, shell.destroy)


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


def cmd_cd(shell, vfs, args):
    if len(args) == 1:
        try:
            node = vfs.resolve_path(args[0])
            if node["type"] != "dir":
                shell.show_output(f"cd: {args[0]}: Not a directory")
                return

            vfs.curr = node["real_path"]
        except FileNotFoundError:
            shell.show_output(f"cd: {args[0]}: No such file or directory")
    else:
        shell.show_output("cd: too many arguments")


def cmd_tac(shell, vfs, args):
    if len(args) > 1:
        shell.show_output("too many arguments")
        return
    path = os.path.abspath(f"{vfs.curr}/{args[0]}")
    if not os.path.isdir(path):
        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as file:
                lines = [i.replace("\n", "") for i in file.readlines()]
                for line in reversed(lines):
                    shell.show_output(line)
        else:
            shell.show_output(f"tail: cannot open {args[0]} for reading: No such file or directory")
    else:
        shell.show_output(f"tail: error reading {args[0]}: Is a directory")


def cmd_tail(shell, vfs, args):
    n = 10
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
    path = os.path.abspath(f"{vfs.curr}/{args[ind_file]}")
    if not os.path.isdir(path):
        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as file:
                lines = [i.replace("\n", "") for i in file.readlines()[-n:]]
                for line in lines:
                    shell.show_output(line)
        else:
            shell.show_output(f"tail: cannot open {args[ind_file]} for reading: No such file or directory")
    else:
        shell.show_output(f"tail: error reading {args[ind_file]}: Is a directory")


def cmd_pwd(shell, vfs, args):
    if vfs.curr == vfs.root:
        path = "/"
    else:
        path = vfs.curr.replace(vfs.root, "").replace("\\", "/")
    shell.show_output(path)


def get_default_commands():
    return {
        "exit": cmd_exit,
        "ls": cmd_ls,
        "cd": cmd_cd,
        "tail": cmd_tail,
        "pwd": cmd_pwd,
        "tac": cmd_tac,
    }
