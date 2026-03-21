"""Directory traversal with filtering."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import pathspec

from dendron.gitignore import collect_ancestor_gitignores, is_ignored, load_gitignore

# Directories and files filtered by default.
# Disabled with -G / --no-default-ignore.
DEFAULT_IGNORES = {
    "__pycache__",
    ".git",
    "node_modules",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".eggs",
    "dist",
    "build",
    ".DS_Store",
    "Thumbs.db",
}

# Glob patterns for default ignores that need suffix matching
DEFAULT_IGNORE_GLOBS = {"*.egg-info"}


@dataclass
class TreeNode:
    """A node in the directory tree."""

    name: str
    is_dir: bool
    children: list[TreeNode] = field(default_factory=list)


@dataclass
class WalkStats:
    """Counters accumulated during traversal."""

    dirs: int = 0
    files: int = 0
    filtered: int = 0


@dataclass
class WalkConfig:
    """Configuration for directory traversal."""

    max_depth: int | None = None
    dirs_only: bool = False
    show_hidden: bool = False
    use_gitignore: bool = True
    use_default_ignores: bool = True


def walk(root: Path, config: WalkConfig) -> tuple[TreeNode, WalkStats]:
    """Walk a directory tree and return a TreeNode structure.

    Args:
        root: The directory to walk.
        config: Filtering and traversal options.

    Returns:
        A tuple of (root TreeNode, WalkStats).
    """
    root = root.resolve()
    stats = WalkStats()

    # Phase 1: collect ancestor .gitignore files
    gi_matchers: dict[Path, pathspec.PathSpec] = {}
    if config.use_gitignore:
        gi_matchers = collect_ancestor_gitignores(root)

    root_node = TreeNode(name=root.name, is_dir=True)
    _walk_recursive(root, root_node, config, gi_matchers, stats, depth=0)
    return root_node, stats


def _walk_recursive(
    dir_path: Path,
    node: TreeNode,
    config: WalkConfig,
    gi_matchers: dict[Path, pathspec.PathSpec],
    stats: WalkStats,
    depth: int,
) -> None:
    """Recursively populate a TreeNode's children."""
    # Depth check
    if config.max_depth is not None and depth >= config.max_depth:
        return

    # Phase 2: check for .gitignore in this directory
    if config.use_gitignore:
        local_spec = load_gitignore(dir_path)
        if local_spec is not None:
            gi_matchers = {**gi_matchers, dir_path: local_spec}

    # Read directory entries
    try:
        entries = list(os.scandir(dir_path))
    except PermissionError:
        node.children.append(TreeNode(name="[permission denied]", is_dir=False))
        return

    # Sort: directories first, then alphabetical (case-insensitive)
    entries.sort(key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower()))

    for entry in entries:
        entry_path = Path(entry.path)
        is_dir = entry.is_dir(follow_symlinks=False)
        is_symlink = entry.is_symlink()

        # Filter: hidden files
        if not config.show_hidden and entry.name.startswith("."):
            stats.filtered += 1
            continue

        # Filter: default ignores (exact name match)
        if config.use_default_ignores and entry.name in DEFAULT_IGNORES:
            stats.filtered += 1
            continue

        # Filter: default ignores (glob patterns like *.egg-info)
        if config.use_default_ignores:
            if any(entry_path.match(g) for g in DEFAULT_IGNORE_GLOBS):
                stats.filtered += 1
                continue

        # Filter: .gitignore patterns
        if config.use_gitignore and gi_matchers:
            if is_ignored(entry_path, dir_path, gi_matchers):
                stats.filtered += 1
                continue

        # Filter: dirs-only mode
        if config.dirs_only and not is_dir:
            continue

        # Count
        if is_dir:
            stats.dirs += 1
        else:
            stats.files += 1

        # Build child node
        child = TreeNode(name=entry.name, is_dir=is_dir)
        node.children.append(child)

        # Recurse into directories (but not symlinks)
        if is_dir and not is_symlink:
            _walk_recursive(
                entry_path, child, config, gi_matchers, stats, depth + 1
            )