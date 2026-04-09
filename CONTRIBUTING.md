# Contributing to GTFS 2 GIS

Thank you for your interest in contributing to **GTFS 2 GIS**! This guide will help you get started.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Release Process](#release-process)
- [License](#license)

---

## Code of Conduct

By participating in this project, you are expected to uphold a respectful and inclusive environment. Be kind, constructive, and welcoming to all contributors regardless of experience level.

---

## How to Contribute

There are many ways to contribute:

- 🐛 **Report bugs** — Open an [Issue](https://github.com/arrobaraujo/qgis_gtfs_plugin/issues) with steps to reproduce
- 💡 **Suggest features** — Describe the use case and expected behavior
- 📖 **Improve documentation** — Fix typos, clarify instructions, add examples
- 🔧 **Submit code** — Fix bugs or implement new features via Pull Requests
- 🌍 **Translate** — Help translate the UI or documentation to other languages
- 🧪 **Test** — Try the plugin with different GTFS feeds and report inconsistencies

---

## Development Setup

### Prerequisites

- **QGIS 3.44+** installed ([download](https://qgis.org/download/))
- **Python 3.10+** (bundled with QGIS)
- **Git**

### Installation for Development

1. **Clone the repository:**

   ```bash
   git clone https://github.com/arrobaraujo/qgis_gtfs_plugin.git
   cd qgis_gtfs_plugin
   ```

2. **Symlink the plugin to your QGIS plugins directory:**

   This avoids having to copy files every time you make a change.

   **Windows (PowerShell as Administrator):**
   ```powershell
   New-Item -ItemType SymbolicLink `
     -Path "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\qgis_gtfs_plugin" `
     -Target "$(Get-Location)\qgis_gtfs_plugin"
   ```

   **Linux:**
   ```bash
   ln -s "$(pwd)/qgis_gtfs_plugin" \
     ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis_gtfs_plugin
   ```

   **macOS:**
   ```bash
   ln -s "$(pwd)/qgis_gtfs_plugin" \
     ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/qgis_gtfs_plugin
   ```

3. **Enable the plugin in QGIS:**
   - Open QGIS
   - Go to **Plugins** → **Manage and Install Plugins**
   - Find **"GTFS 2 GIS"** and check the box to enable it

4. **Reload after changes:**
   - Use the **Plugin Reloader** plugin (install from QGIS Plugin Manager) to hot-reload during development
   - Or restart QGIS to pick up changes

### Useful QGIS Development Tools

- **Plugin Reloader** — Reloads your plugin without restarting QGIS
- **Python Console** — `Ctrl+Alt+P` in QGIS, useful for testing PyQGIS snippets
- **debugpy** — Attach VS Code to QGIS Python for breakpoint debugging

---

## Project Structure

```
qgis_gtfs_plugin/
├── __init__.py              ← classFactory() — QGIS entry point
├── plugin.py                ← GTFSLoader — Main plugin orchestrator
├── metadata.txt             ← Plugin registry metadata (version, description)
├── icon.png                 ← Toolbar icon
├── core/
│   ├── processor.py         ← GTFSProcessor — GTFS data parsing
│   ├── layer_factory.py     ← LayerFactory — Layer creation & styling
│   └── search_panel.py      ← GTFSSearchPanel — Analytics panel & tools
└── ui/
    ├── gtfs_dialog.py        ← GTFSDialog — File selection dialog
    ├── gtfs_dialog.ui        ← Qt Designer layout (file dialog)
    └── search_panel.ui       ← Qt Designer layout (analytics panel)
```

For a detailed architectural overview, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Coding Standards

### Python Style

- Follow **PEP 8** for all Python code
- Maximum line length: **120 characters**
- Use **type hints** for function signatures
- Use **docstrings** (Google style) for all public methods and classes

```python
def calculate_distance(point_a: QgsPointXY, point_b: QgsPointXY) -> float:
    """Calculates the ellipsoidal distance between two points.

    Args:
        point_a: The origin point.
        point_b: The destination point.

    Returns:
        The distance in meters.
    """
```

### Imports

Order imports following PEP 8:

```python
# 1. Standard library
import os
import csv

# 2. Third-party / QGIS
from qgis.core import QgsVectorLayer, QgsFeature
from qgis.PyQt import QtWidgets

# 3. Local
from .core.processor import GTFSProcessor
```

### Qt / UI

- Use `.ui` files designed in **Qt Designer** for layouts
- Load UI files with `uic.loadUiType()` — do not hand-code complex layouts
- Widget names in `.ui` files should use descriptive prefixes: `btn_`, `val_`, `filter_`, `list_`

### Layer Creation

When adding new analysis layers:

1. Create a `@staticmethod` method in `LayerFactory`
2. Use memory layers (`QgsVectorLayer("...", "LayerName", "memory")`)
3. Apply proper styling (colors, symbols, labels)
4. Add the layer to the project with `QgsProject.instance().addMapLayer()`
5. Optionally set default visibility via the layer tree node

---

## Commit Messages

Use the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, PEP8) — no logic change |
| `refactor` | Code restructuring — no feature or fix |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `ci` | CI/CD configuration |
| `chore` | Maintenance tasks |

### Examples

```
feat(processor): add support for frequencies.txt parsing
fix(layer_factory): correct symbol layer ordering for high-frequency routes
docs(readme): update installation instructions for QGIS 3.44
style(processor): resolve remaining PEP8 violations
ci(publish): fix OSGEO credential injection in workflow
```

---

## Pull Request Process

1. **Fork** the repository and create a feature branch:
   ```bash
   git checkout -b feat/my-new-feature
   ```

2. **Make your changes** following the coding standards above

3. **Test your changes** in QGIS:
   - Load at least one GTFS ZIP file and verify layers are created correctly
   - Check that existing functionality is not broken
   - If adding a new analysis tool, verify it produces correct output

4. **Update documentation** if needed:
   - Update `README.md` / `README.pt-BR.md` for user-facing changes
   - Update `ARCHITECTURE.md` for structural changes
   - Add a `CHANGELOG.md` entry

5. **Update `metadata.txt`** if changing the version

6. **Open a Pull Request** against the `main` branch:
   - Provide a clear description of what changed and why
   - Reference any related issues (e.g., `Closes #42`)
   - Include screenshots if the change affects the UI

7. **Wait for review** — maintainers will review and may request changes

### PR Checklist

- [ ] Code follows PEP 8
- [ ] Plugin loads without errors in QGIS ≥ 3.44
- [ ] GTFS loading and layer creation still work
- [ ] New features are documented
- [ ] `CHANGELOG.md` is updated
- [ ] `metadata.txt` version is bumped (if applicable)

---

## Reporting Bugs

When reporting a bug, please include:

1. **QGIS version** (Help → About QGIS)
2. **Plugin version** (from Plugin Manager or `metadata.txt`)
3. **Operating system** (Windows/Linux/macOS + version)
4. **Steps to reproduce** the issue
5. **Expected behavior** vs. **actual behavior**
6. **GTFS file** used (if possible, share a link to the feed or a minimal example)
7. **Error messages** from the QGIS Python console or log panel

Use the [Issue Tracker](https://github.com/arrobaraujo/qgis_gtfs_plugin/issues) to file bugs.

---

## Feature Requests

Feature requests are welcome! When suggesting a feature:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** — what problem does it solve?
3. **Provide examples** — GTFS feeds, screenshots, mockups
4. **Consider scope** — does it fit the plugin's mission of GTFS visualization and analysis?

---

## Release Process

Releases are automated via GitHub Actions. To publish a new version:

1. Update the version in `metadata.txt`:
   ```ini
   version=X.Y.Z
   ```

2. Add a changelog entry in `CHANGELOG.md`:
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD
   - Description of changes
   ```

3. Commit and tag:
   ```bash
   git add metadata.txt CHANGELOG.md
   git commit -m "chore: release vX.Y.Z"
   git tag X.Y.Z
   git push origin main --tags
   ```

4. The GitHub Actions workflow will automatically:
   - Create a GitHub Release with the changelog
   - Publish the plugin to the [official QGIS repository](https://plugins.qgis.org/)

> **Note:** The repository secrets `OSGEO_USER` and `OSGEO_PASSWORD` must be configured for publication to succeed.

---

## License

By contributing to this project, you agree that your contributions will be licensed under the **GNU General Public License v3.0** — the same license as the project.

See [LICENSE](LICENSE) for details.

---

**Thank you for helping make public transit data more accessible! 🚌🗺️**
