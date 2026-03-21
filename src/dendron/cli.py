"""CLI entry point for dendron."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dendron import __version__
from dendron.renderer import render_tree
from dendron.walker import WalkConfig, walk


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dendron",
        description="Print a .gitignore-aware directory tree.",
    )
    p.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory to print (default: current directory)",
    )
    p.add_argument(
        "-d",
        "--depth",
        type=int,
        default=None,
        metavar="N",
        help="Max recursion depth",
    )
    p.add_argument(
        "-D",
        "--dirs-only",
        action="store_true",
        help="Show only directories",
    )
    p.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="show_hidden",
        help="Include hidden files and directories",
    )
    p.add_argument(
        "-g",
        "--no-gitignore",
        action="store_true",
        help="Disable .gitignore filtering",
    )
    p.add_argument(
        "-G",
        "--no-default-ignore",
        action="store_true",
        help="Disable hardcoded default ignore list",
    )
    p.add_argument(
        "-s",
        "--save",
        type=str,
        default=None,
        metavar="PATH",
        help="Save output to a file (wrapped in markdown code block)",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Append summary with file/dir counts",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    target = Path(args.path)
    if not target.exists():
        print(f"dendron: error: '{args.path}' does not exist", file=sys.stderr)
        sys.exit(1)
    if not target.is_dir():
        # Target is a file — just print its name
        print(target.name)
        sys.exit(0)

    config = WalkConfig(
        max_depth=args.depth,
        dirs_only=args.dirs_only,
        show_hidden=args.show_hidden,
        use_gitignore=not args.no_gitignore,
        use_default_ignores=not args.no_default_ignore,
    )

    root_node, stats = walk(target, config)
    output = render_tree(root_node)

    # Verbose summary
    if args.verbose:
        parts = [f"{stats.dirs} directories", f"{stats.files} files"]
        if stats.filtered > 0:
            parts.append(f"({stats.filtered} filtered)")
        output += "\n\n" + ", ".join(parts)

    # Output routing
    print(output)

    if args.save:
        save_path = Path(args.save)
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("```\n")
                f.write(output)
                f.write("\n```\n")
            print(f"\nSaved to {save_path}", file=sys.stderr)
        except OSError as e:
            print(f"dendron: error writing to '{args.save}': {e}", file=sys.stderr)
            sys.exit(1)