# Dendron

A `.gitignore`-aware directory tree printer for the terminal. Produces clean, human-readable Unicode tree output with sane defaults — hidden files excluded, junk directories filtered, and `.gitignore` patterns respected automatically.

## Installation

Requires Python 3.9+.

### Via pipx (recommended)

```bash
pipx install --editable /path/to/dendron
```

This registers `dendron` as a globally available command without polluting your system Python or any project environment. The `--editable` flag means changes to the source take effect immediately without reinstalling.

### Via pip (development)

```bash
pip install -e /path/to/dendron
```

## Usage

```bash
dendron [PATH] [OPTIONS]
```

`PATH` defaults to `.` (current directory).

### Examples

```bash
# Tree of current directory
dendron

# Tree of a specific directory
dendron ./src

# Limit depth to 3 levels
dendron -d 3

# Directories only
dendron -D

# Include hidden files
dendron -a

# Save to a markdown file
dendron -s tree.md

# Show summary stats
dendron -v

# Combine flags: shallow, dirs only, with hidden, saved to file
dendron -d 2 -Da -s structure.md

# Disable .gitignore filtering
dendron -g

# Disable hardcoded default ignores
dendron -G

# Everything — no filtering at all
dendron -agG
```

### Sample Output

```
dendron/
├── pyproject.toml
├── README.md
├── LICENSE
└── src/
    └── dendron/
        ├── __init__.py
        ├── cli.py
        ├── gitignore.py
        ├── renderer.py
        └── walker.py
```

With `-v`:

```
dendron/
├── pyproject.toml
├── README.md
├── LICENSE
└── src/
    └── dendron/
        ├── __init__.py
        ├── cli.py
        ├── gitignore.py
        ├── renderer.py
        └── walker.py

2 directories, 7 files (5 filtered)
```

## Flags

| Flag | Long | Description |
|------|------|-------------|
| `-d N` | `--depth N` | Max recursion depth |
| `-D` | `--dirs-only` | Show only directories |
| `-a` | `--all` | Include hidden files and directories |
| `-g` | `--no-gitignore` | Disable `.gitignore` filtering |
| `-G` | `--no-default-ignore` | Disable hardcoded default ignore list |
| `-s PATH` | `--save PATH` | Save output to file (wrapped in markdown code block) |
| `-v` | `--verbose` | Append summary with file/dir/filtered counts |
| | `--version` | Print version and exit |

## Default Behavior

Out of the box, `dendron` filters the following without any flags:

**Hidden files/directories** — anything starting with `.` is excluded. Use `-a` to include.

**`.gitignore` patterns** — if the target directory is inside a git repository, `.gitignore` files are discovered and respected automatically. Dendron walks up from the target directory to the repository root (identified by the presence of `.git/`), collecting `.gitignore` files at each level. Nested `.gitignore` files within the tree are also respected. Use `-g` to disable.

**Hardcoded default ignores** — common machine-generated directories and files are excluded even outside of git repositories:

```
__pycache__    .git           node_modules    .venv       venv
.tox           .mypy_cache    .pytest_cache   .ruff_cache .eggs
dist           build          .DS_Store       Thumbs.db   *.egg-info
```

Use `-G` to disable.

**Symlinks** — printed but never followed. This prevents infinite loops from circular symlinks and avoids duplicating content that exists elsewhere in the tree.

## Dependencies

One: [`pathspec`](https://pypi.org/project/pathspec/) — a pure-Python library for gitignore-style pattern matching. Zero transitive dependencies.

## License

This project is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.