import argparse
from .gui import ShellEmulator
from .script_runner import run_script
from .vfs import VFS

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vfs","-v", required=True)
    parser.add_argument("--script","-s")
    args = parser.parse_args()

    vfs = VFS(args.vfs)
    app = ShellEmulator(vfs)
    if args.script:
        app.after(150, lambda: run_script(app, args.script))
    app.mainloop()

if __name__ == "__main__":
    main()
