import os

class VFS:
    def __init__(self, vfs_path):
        self.vfs_path = vfs_path
        self.root = os.path.abspath(vfs_path) # корень VFS
        self.curr = self.root # текущая директория
        self.vfs_root = self._build_vfs(vfs_path) # дерево VFS

    def build_node(self, path):
        if os.path.isdir(path):
            # создаём узел для директории
            node = {"type": "dir", "path": path, "children": {}}
            try:
                names = sorted(os.listdir(path))
            except PermissionError:
                names = []
            for name in names:
                node["children"][name] = self.build_node(os.path.join(path, name))
            return node
        else:
            # создаём узел для файла
            return {"type": "file", "path": path, "real_path": path}

    def _build_vfs(self, root_path):
        root_path = os.path.abspath(root_path)
        if not os.path.exists(root_path):
            raise FileNotFoundError(root_path)
        # строим дерево с корня
        return self.build_node(root_path)

    def resolve_path(self, path_str):
        if path_str == ".":
            # текущая директория
            return self.find_node_by_real_path(self.curr)

        elif path_str == "..":
            # родительская директория
            if self.curr == self.root:
                return self.vfs_root

            target_real_path = os.path.dirname(self.curr)
            return self.find_node_by_real_path(target_real_path)

        elif path_str == "/":
            # корень VFS
            return self.vfs_root

        elif path_str.startswith("/"):
            # абсолютный путь
            target_path = os.path.join(self.root, path_str[1:])
            if self.find_node_by_real_path(target_path) is None:
                raise FileNotFoundError
            else:
                return self.find_node_by_real_path(target_path)

        else:
            # относительный путь
            target_path = os.path.join(self.curr, path_str)
            if self.find_node_by_real_path(target_path) is None:
                raise FileNotFoundError
            else:
                return self.find_node_by_real_path(target_path)


    def find_node_by_real_path(self, target_path):
        target_path = os.path.abspath(target_path)

        def search(node):
            if node.get("path") == target_path:
                return node

            if node["type"] == "dir":
                for child_node in node["children"].values():
                    found = search(child_node)
                    if found:
                        return found
            return None

        # поиск узла по реальному пути
        result = search(self.vfs_root)
        return result
