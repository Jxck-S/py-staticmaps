"""Generate the examples gallery from examples/ and its rendered output.

Pages are built from the example scripts themselves, so adding an example is
all it takes to document it. Images are read from examples/build, which
examples/run_examples.py fills; this script never runs an example, so a
documentation build stays offline and needs no api keys. An example whose
output is missing still gets a page, carrying its source alone.
"""

import json
import pathlib
import typing

import mkdocs_gen_files

DIRECTORY = "examples"
SOURCE = pathlib.Path("examples")
BUILD = SOURCE / "build"
EXCLUDED = {"run_examples.py"}
MANIFEST = BUILD / "manifest.json"
IMAGE_SUFFIXES = (".png", ".svg")


def title_of(script: pathlib.Path) -> str:
    """Return a human readable title for an example

    Parameters:
        script (pathlib.Path): example script

    Returns:
        str: title derived from the file name
    """
    return script.stem.replace("_", " ").replace(".", " ").title()


def summary_of(script: pathlib.Path) -> str:
    """Return the example's module docstring, minus the library prefix

    Parameters:
        script (pathlib.Path): example script

    Returns:
        str: description, or an empty string when there is no docstring
    """
    text = script.read_text(encoding="utf-8")
    start = text.find('"""')
    if start < 0:
        return ""
    end = text.find('"""', start + 3)
    if end < 0:
        return ""
    doc = text[start + 3 : end].strip()
    prefix = "py-staticmaps - "
    if doc.startswith(prefix):
        doc = doc[len(prefix) :]
    return doc


def load_manifest() -> typing.Dict[str, typing.List[str]]:
    """Return what each example produced, as recorded by the runner

    Returns:
        typing.Dict[str, typing.List[str]]: example file name to output names
    """
    if not MANIFEST.is_file():
        return {}
    try:
        with open(MANIFEST, encoding="utf-8") as handle:
            return typing.cast(typing.Dict[str, typing.List[str]], json.load(handle))
    except (OSError, ValueError):
        return {}


def images_for(script: pathlib.Path, manifest: typing.Dict[str, typing.List[str]]) -> typing.List[pathlib.Path]:
    """Return the rendered output belonging to an example

    The runner records which files each example wrote, because an example's
    output is not always named after it: tile_providers.py writes one file
    per provider.

    Parameters:
        script (pathlib.Path): example script
        manifest (typing.Dict[str, typing.List[str]]): runner output record

    Returns:
        typing.List[pathlib.Path]: image paths, sorted by name
    """
    if not BUILD.is_dir():
        return []
    if script.name in manifest:
        named = [BUILD / name for name in manifest[script.name]]
        return sorted(p for p in named if p.is_file() and p.suffix in IMAGE_SUFFIXES)
    # no manifest: fall back to matching on the example's name
    return sorted(p for p in BUILD.iterdir() if p.suffix in IMAGE_SUFFIXES and p.name.startswith(script.stem))


def main() -> None:
    """Write a page per example plus the gallery index"""
    scripts = sorted(p for p in SOURCE.glob("*.py") if p.name not in EXCLUDED)
    manifest = load_manifest()
    nav = mkdocs_gen_files.Nav()
    index_rows = []

    for script in scripts:
        images = images_for(script, manifest)
        doc_path = pathlib.Path(DIRECTORY, f"{script.stem}.md")
        nav[(title_of(script),)] = doc_path.name

        with mkdocs_gen_files.open(doc_path, "w") as page:
            page.write(f"# {title_of(script)}\n\n")
            summary = summary_of(script)
            if summary:
                page.write(f"{summary}\n\n")
            if images:
                page.write("## Output\n\n")
                for image in images:
                    # copy the rendered file in beside the page
                    with mkdocs_gen_files.open(f"{DIRECTORY}/{image.name}", "wb") as out:
                        out.write(image.read_bytes())
                    page.write(f"![{image.name}]({image.name})\n\n")
            else:
                page.write(
                    "!!! note\n\n"
                    "    No rendered output is available for this example. Run\n"
                    "    `python examples/run_examples.py` to generate it.\n\n"
                )
            page.write("## Source\n\n")
            page.write(f'```python title="examples/{script.name}"\n')
            page.write(script.read_text(encoding="utf-8"))
            page.write("```\n")

        mkdocs_gen_files.set_edit_path(doc_path, script)
        index_rows.append((title_of(script), script.stem, len(images)))

    with mkdocs_gen_files.open(f"{DIRECTORY}/index.md", "w") as page:
        page.write("# Examples\n\n")
        page.write("Every script in `examples/`, with the output it renders.\n\n")
        page.write("| Example | Rendered files |\n|---|---|\n")
        for title, stem, count in index_rows:
            page.write(f"| [{title}]({stem}.md) | {count or '-'} |\n")

    with mkdocs_gen_files.open(f"{DIRECTORY}/SUMMARY.md", "w") as nav_file:
        nav_file.writelines(nav.build_literate_nav())


main()
