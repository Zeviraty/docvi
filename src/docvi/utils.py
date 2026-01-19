import ast
from pathlib import Path

def parse_python_file(file_path: Path) -> dict:
    tree = ast.parse(file_path.read_text(encoding="utf-8"))

    functions = []
    classes = []
    constants = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "methods": [
                    n.name for n in node.body
                    if isinstance(n, ast.FunctionDef)
                ]
            })

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append(target.id)

    return {
        "path": str(file_path),
        "functions": functions,
        "classes": classes,
        "constants": constants,
    }

def module_data(path: str | Path) -> dict:
    path = Path(path).resolve()

    data = {
        "path": str(path),
        "submodules": [],
        "functions": [],
        "classes": [],
        "constants": [],
    }

    if path.is_file() and path.suffix == ".py":
        parsed = parse_python_file(path)
        data.update(parsed)
        return data

    if not path.is_dir():
        return {}

    src_dir = path / "src"

    if src_dir.is_dir():
        packages = [
            p for p in src_dir.iterdir()
            if p.is_dir() and (p / "__init__.py").exists()
        ]

        if len(packages) == 1:
            return module_data(packages[0])
        else:
            data["submodules"] = [module_data(p) for p in packages]
            return data

    init_file = path / "__init__.py"

    if init_file.exists():
        parsed = parse_python_file(init_file)
        data.update(parsed)

    for item in path.iterdir():
        if item.name.startswith("__"):
            continue

        if item.is_dir() and (item / "__init__.py").exists():
            data["submodules"].append(module_data(item))

        elif item.is_file() and item.suffix == ".py":
            data["submodules"].append(parse_python_file(item))

    return data
