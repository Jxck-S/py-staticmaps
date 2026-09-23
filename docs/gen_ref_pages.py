"""Generate the code reference pages, index and navigation."""

import ast
import typing
from pathlib import Path

import mkdocs_gen_files

TOP_LEVEL_NAME = "staticmaps"
DIRECTORY = "reference"
SRC = "staticmaps"


def public_names(path: Path) -> typing.Tuple[typing.List[str], typing.List[str]]:
    """Return the public classes and functions a module defines

    The module is parsed rather than imported, so the index builds without
    the optional dependencies some modules need.

    Parameters:
        path (Path): module to read

    Returns:
        tuple: class names, function names
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return [], []
    classes, functions = [], []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            functions.append(node.name)
    return classes, functions


def write_index(modules: typing.List[typing.Tuple[str, Path]]) -> None:
    """Write the reference landing page

    The navigation links to the directory, so it needs an index -- and a page
    that only says "here are the modules" is no use, so it lists what each one
    defines.

    Parameters:
        modules (typing.List[typing.Tuple[str, Path]]): module name and path
    """
    with mkdocs_gen_files.open(f"{DIRECTORY}/index.md", "w") as index_file:
        index_file.write("# Code Reference\n\n")
        index_file.write(
            f"Every public module of `{TOP_LEVEL_NAME}`, generated from its docstrings.\n"
            "Follow a module for the full signatures, parameters and source.\n\n"
        )
        index_file.write("| Module | Defines |\n|---|---|\n")
        for module, path in modules:
            classes, functions = public_names(path)
            defined = ", ".join(f"`{n}`" for n in classes + functions) or "—"
            index_file.write(f"| [{module}]({module}.md) | {defined} |\n")


def main() -> None:
    """
    main entry point
    """

    nav = mkdocs_gen_files.Nav()
    modules: typing.List[typing.Tuple[str, Path]] = []

    for path in sorted(Path(SRC).rglob("*.py")):
        module_path = path.relative_to(SRC).with_suffix("")

        doc_path = path.relative_to(SRC).with_suffix(".md")
        full_doc_path = Path(DIRECTORY, doc_path)

        parts = list(module_path.parts)
        # omit __init__, __main__, cli.py
        if parts[-1] in ["__init__", "__main__", "cli"]:
            continue

        if not parts:
            continue

        nav[tuple(parts)] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as file_handle:
            ident = ".".join(parts)
            file_handle.write(f"::: {ident}")

        mkdocs_gen_files.set_edit_path(full_doc_path, path)
        modules.append((".".join(parts), path))
        # mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)

    write_index(modules)

    with mkdocs_gen_files.open(f"{DIRECTORY}/SUMMARY.md", "w") as nav_file:
        nav_file.writelines(nav.build_literate_nav())


main()
