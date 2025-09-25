import os

class VFS:
    def __init__(self, vfs_path):
        self.root = vfs_path
        self.curr = self.root
        self.vfs_root = self.build_vfs(vfs_path)
        self.vfs_curr = self.vfs_root

    def build_node(self, path):
        if os.path.isdir(path):
            node = {"type": "dir", "name": os.path.basename(path), "children": {}}
            try:
                names = sorted(os.listdir(path))
            except PermissionError:
                names = []
            for name in names:
                node["children"][name] = self.build_node(os.path.join(path, name))
            return node
        else:
            return {"type": "file", "name": os.path.basename(path)}

    def build_vfs(self, root_path):
        root_path = os.path.abspath(root_path)
        if not os.path.exists(root_path):
            raise FileNotFoundError(root_path)
        return self.build_node(root_path)

    def resolve_path(self, path_str):
        if path_str == ".":
            return self.vfs_curr
        else:
            return self.build_vfs(os.path.join(self.curr, path_str))
