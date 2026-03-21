""".gitignore discovery and pattern matching."""

from __future__ import annotations

from pathlib import Path

import pathspec


def load_gitignore(directory: Path) -> pathspec.PathSpec | None:
    """Load and compile a .gitignore file from a directory.

    Returns None if no .gitignore exists or it can't be read.
    """
    gi_path = directory / ".gitignore"
    if not gi_path.is_file():
        return None
    try:
        text = gi_path.read_text(encoding="utf-8", errors="replace")
        return pathspec.PathSpec.from_lines("gitwildmatch", text.splitlines())
    except (OSError, UnicodeDecodeError):
        return None


def collect_ancestor_gitignores(target: Path) -> dict[Path, pathspec.PathSpec]:
    """Walk from target up to repo root (or filesystem root), collecting .gitignore files.

    Stops early if a .git/ directory is found (repo root boundary).
    Returns a dict mapping each directory to its compiled .gitignore PathSpec.
    """
    matchers: dict[Path, pathspec.PathSpec] = {}
    current = target.resolve()

    while True:
        spec = load_gitignore(current)
        if spec is not None:
            matchers[current] = spec

        # Stop if we found the repo root
        if (current / ".git").is_dir():
            break

        parent = current.parent
        # Stop if we've hit filesystem root
        if parent == current:
            break
        current = parent

    return matchers


def is_ignored(
    path: Path,
    rel_to: Path,
    matchers: dict[Path, pathspec.PathSpec],
) -> bool:
    """Check if a path should be ignored by any applicable .gitignore.

    Args:
        path: The absolute path to check.
        rel_to: The base directory to compute relative paths from (for pattern matching).
        matchers: Dict mapping directories to their compiled .gitignore specs.

    Returns:
        True if the path matches any applicable ignore pattern.
    """
    for matcher_dir, spec in matchers.items():
        try:
            rel = path.relative_to(matcher_dir)
        except ValueError:
            # path is not under this matcher's directory — skip
            continue
        # pathspec expects forward-slash strings
        rel_str = rel.as_posix()
        # Append trailing slash for directories so dir-only patterns match
        if path.is_dir():
            rel_str += "/"
        if spec.match_file(rel_str):
            return True
    return False