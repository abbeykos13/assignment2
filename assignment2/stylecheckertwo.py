import ast
import os
import re
from typing import List, Tuple
from pathlib import Path

def read_source_file(file_path: str) -> Tuple[str, List[str]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    return source, source.splitlines()

def parse_ast(source: str) -> ast.AST:
    return ast.parse(source)

def get_imports(tree: ast.AST) -> List[str]:
    return sorted(set(
        node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ))

def get_classes(tree: ast.AST) -> List[str]:
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

def get_functions(tree: ast.AST) -> List[str]:
    return [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and not isinstance(getattr(node, 'parent', None), ast.ClassDef)
    ]

def get_docstrings(tree: ast.AST) -> List[str]:
    docstring_info = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            if isinstance(node, ast.FunctionDef) and is_special_method(node.name):
                continue
            doc = ast.get_docstring(node)
            if doc:
                docstring_info.append(f"{node.name}:\n{doc}")
            else:
                docstring_info.append(f"{node.name}: DocString not found.")
    return docstring_info

def get_type_annotation_issues(tree: ast.AST) -> List[str]:
    missing = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if is_special_method(node.name):
                continue
            has_annotations = all(arg.annotation for arg in node.args.args)
            if not has_annotations or not node.returns:
                missing.append(node.name)
    return missing

def check_class_naming(classes: List[str]) -> List[str]:
    return [cls for cls in classes if not re.match(r'^[A-Z][A-Za-z0-9]*$', cls)]

def check_function_naming(tree: ast.AST) -> List[str]:
    bad_names = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if is_special_method(node.name):
                continue
            if not re.match(r'^([a-z]+_?)*[a-z]+$', node.name):
                bad_names.append(node.name)
    return bad_names

def get_special_methods(tree: ast.AST) -> List[str]:
    return [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and is_special_method(node.name)
    ]

def is_special_method(name: str) -> bool:
    return name.startswith('__') and name.endswith('__')

def add_parents(tree: ast.AST) -> ast.AST:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree

def write_report(report_path: str, data: dict) -> None:
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"File Structure\n---------------\n")
        f.write(f"Total lines of code: {data['lines']}\n")
        f.write("\nImports:\n" + "\n".join(data['imports']) + "\n\n")
        f.write("Classes:\n" + "\n".join(data['classes']) + "\n\n")
        f.write("Functions:\n" + "\n".join(data['functions']) + "\n\n")
        f.write("Other (Special) Methods:\n" + "\n".join(data['special_methods']) + "\n\n")

        f.write("DocStrings:\n---------------\n")
        f.write("\n\n".join(data['docstrings']) + "\n\n")

        f.write("Type Annotations Check:\n---------------\n")
        if data['missing_annotations']:
            f.write("Missing type annotations:\n" + "\n".join(data['missing_annotations']) + "\n\n")
        else:
            f.write("All functions and methods have type annotations.\n\n")

        f.write("Naming Convention Check:\n---------------\n")
        if data['bad_class_names']:
            f.write("Bad class names:\n" + "\n".join(data['bad_class_names']) + "\n\n")
        else:
            f.write("All class names follow CamelCase.\n\n")

        if data['bad_func_names']:
            f.write("Bad function/method names:\n" + "\n".join(data['bad_func_names']) + "\n\n")
        else:
            f.write("All function/method names follow snake_case.\n\n")

def main():
    file_path = input("Enter the path to the Python file: ").strip()
    if not os.path.isfile(file_path) or not file_path.endswith('.py'):
        print("Invalid file. Please provide a valid .py file path.")
        return

    source, lines = read_source_file(file_path)
    tree = parse_ast(source)
    tree = add_parents(tree)

    imports = get_imports(tree)
    classes = get_classes(tree)
    functions = get_functions(tree)
    docstrings = get_docstrings(tree)
    missing_annotations = get_type_annotation_issues(tree)
    bad_class_names = check_class_naming(classes)
    bad_func_names = check_function_naming(tree)
    special_methods = get_special_methods(tree)

    report_data = {
        'lines': len(lines),
        'imports': imports,
        'classes': classes,
        'functions': functions,
        'docstrings': docstrings,
        'missing_annotations': missing_annotations,
        'bad_class_names': bad_class_names,
        'bad_func_names': bad_func_names,
        'special_methods': special_methods
    }

    source_filename = Path(file_path).stem
    report_path = os.path.join(os.path.dirname(file_path), f"style_report_{source_filename}.txt")
    write_report(report_path, report_data)
    print(f"Report written to {report_path}")

if __name__ == '__main__':
    main()
