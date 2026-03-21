"""Render a tree structure into a Unicode string."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dendron.walker import TreeNode

# Box-drawing characters
BRANCH = "├── "
LAST_BRANCH = "└── "
VERTICAL = "│   "
INDENT = "    "


def render_tree(root: TreeNode, show_root: bool = True) -> str:
    """Render a TreeNode into a Unicode tree string.

    Args:
        root: The root node of the tree.
        show_root: Whether to include the root directory name in output.

    Returns:
        A string containing the full rendered tree.
    """
    lines: list[str] = []
    if show_root:
        label = root.name + "/" if root.is_dir else root.name
        lines.append(label)
    _render_children(root.children, "", lines)
    return "\n".join(lines)


def _render_children(
    children: list[TreeNode], prefix: str, lines: list[str]
) -> None:
    """Recursively render child nodes with proper indentation."""
    for i, child in enumerate(children):
        is_last = i == len(children) - 1
        connector = LAST_BRANCH if is_last else BRANCH
        label = child.name + "/" if child.is_dir else child.name
        lines.append(f"{prefix}{connector}{label}")

        if child.children:
            extension = INDENT if is_last else VERTICAL
            _render_children(child.children, prefix + extension, lines)