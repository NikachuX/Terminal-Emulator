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
        except Exception:
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
        if args[0] == '/':
            vfs.vfs_curr = vfs.vfs_root
            vfs.curr = vfs.root
            return
        elif args[0][0] == '/':
            try:
                curr = f'{vfs.root}/{args[0][1:]}'
                vfs.vfs_curr = vfs.build_vfs(curr)
                vfs.curr = curr
            except FileNotFoundError:
                shell.show_output(f"cd: {args[0]}: No such file or directory")
        else:
            try:
                curr = f'{vfs.curr}/{args[0]}'
                vfs.vfs_curr = vfs.build_vfs(curr)
                vfs.curr = curr
            except FileNotFoundError:
                shell.show_output(f"cd: {args[0]}: No such file or directory")
    else:
        shell.show_output("cd: too many arguments")


def get_default_commands():
    return {
        "exit": cmd_exit,
        "ls": cmd_ls,
        "cd": cmd_cd,
    }
