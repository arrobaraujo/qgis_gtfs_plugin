# GTFS 2 GIS

**English** | [Português](README.pt-BR.md)

[![QGIS Version](https://img.shields.io/badge/QGIS-3.4+-green.svg)](https://qgis.org/) 
[![Version](https://img.shields.io/badge/version-0.3.8-blue.svg)](https://plugins.qgis.org/plugins/qgis_gtfs_plugin/)
[![License](https://img.shields.io/badge/License-GPL%20v3-red.svg)](LICENSE)

**GTFS 2 GIS** is a QGIS plugin designed for visualizing and analyzing public transit networks from GTFS (General Transit Feed Specification) ZIP files.

---

## 🚀 Key Features

- **Optimized Shapes**: Groups trips by `shape_id` to avoid overlapping lines, with frequency-based line widths and automatic calculation of `shape_ext` (ellipsoidal distance in meters).
- **Stop Intelligence**:
    - Lists all lines passing through a stop.
    - Identifies terminals and which lines terminate there.
    - Icons by transit type (🚌 Bus, 🚇 Subway, 🚄 Rail, ⛴️ Ferry).
- **Financial Data**: Extracts fare prices linked to routes.
- **Automatic Styling**: Applies official route colors defined in GTFS data.
- **Analytics Dashboard**: Real-time statistics panel (total km, stop density, fleets, etc.).
- **Period Filtering**: Filter lines by time slots (Morning Peak, Midday, Evening Peak, Night).

---

## 🔧 Analysis Tools

- **Frequency Heatmap**: Graduated layers showing frequency intensity.
- **Population Coverage**: Calculates population served within walking reach (using IBGE census data for Brazil).
- **Transit Deserts**: Identifies populated areas with little to no transit access.
- **Accessibility**: Creates 400m buffers and real-world network-based isochrones.

---

## 🛠 Installation

### Via Official QGIS Repository (Recommended)
1. In QGIS, go to **Plugins** -> **Manage and Install Plugins**.
2. Search for **"GTFS 2 GIS"** and click **Install**.

### Manual Installation
1. Download this repository's code.
2. Ensure the plugin content is inside a folder named `qgis_gtfs_plugin`.
3. Copy the folder to your QGIS plugins directory:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles\default\python\plugins\`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
4. Enable the plugin in the Plugin Manager.

---

## 📖 How to Use

1. Go to **Plugins** -> **GTFS 2 GIS** -> **Load GTFS...**.
2. Select a GTFS `.zip` file.
3. Lines and stops layers will be created with all metadata.
4. Use the **GTFS Analytics** panel for advanced filtering and tools.

---

## 🤖 Development and CI/CD

This project uses **GitHub Actions** for automated publication.
- Every new **Tag** (e.g., `0.3.8`) triggers a workflow that validates metadata and automatically publishes to the official QGIS repository.

If you wish to contribute, feel free to open a **Pull Request** or report bugs in the [Issue Tracker](https://github.com/arrobaraujo/qgis_gtfs_plugin/issues).

---

## ⚖ License

GNU GPL v3.

Developed by **[Erick Araujo - @arrobaraujo](https://github.com/arrobaraujo)**.
