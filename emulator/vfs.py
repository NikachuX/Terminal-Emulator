import os

class VFS:
    def __init__(self, vfs_path):
        self.root = os.path.abspath(vfs_path)
        self.curr = self.root
        self.vfs_root = self.build_vfs(vfs_path)
        self.vfs_curr = self.vfs_root

    def build_node(self, path):
        if os.path.isdir(path):
            node = {"type": "dir", "real_path": path, "children": {}}
            try:
                names = sorted(os.listdir(path))
            except PermissionError:
                names = []
            for name in names:
                node["children"][name] = self.build_node(os.path.join(path, name))
            return node
        else:
            return {"type": "file", "real_path": path}

    def build_vfs(self, root_path):
        root_path = os.path.abspath(root_path)
        if not os.path.exists(root_path):
            raise FileNotFoundError(root_path)
        return self.build_node(root_path)

    def resolve_path(self, path_str):
        if path_str == ".":
            return self._find_node_by_real_path(self.curr)

        elif path_str == "..":
            if self.curr == self.root:
                return self.vfs_root

            target_real_path = os.path.dirname(self.curr)
            return self._find_node_by_real_path(target_real_path)

        elif path_str == "/":
            return self.vfs_root

        elif path_str.startswith("/"):
            target_real_path = os.path.join(self.root, path_str[1:])
            if os.path.exists(target_real_path):
                return self._find_node_by_real_path(target_real_path)
            else:
                raise FileNotFoundError

        else:
            target_real_path = os.path.join(self.curr, path_str)
            if os.path.exists(target_real_path):
                return self._find_node_by_real_path(target_real_path)
            else:
                raise FileNotFoundError

    def _find_node_by_real_path(self, target_real_path):
        target_real_path = os.path.abspath(target_real_path)

        def search(node):
            if node.get("real_path") == target_real_path:
                return node

            if node["type"] == "dir":
                for child_node in node["children"].values():
                    found = search(child_node)
                    if found:
                        return found
            return None

        result = search(self.vfs_root)
        if result is None:
            raise FileNotFoundError(f"Path not found: {target_real_path}")
        return result


