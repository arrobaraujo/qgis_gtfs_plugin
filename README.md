# GTFS 2 GIS

QGIS plugin focused on the technical visualization of transport networks from GTFS ZIP files.

## 🚀 Key Features

- **Optimized Shapes**: Groups trips by `shape_id` to avoid hundreds of overlapping lines.
- **Stop Intelligence**: 
    - Lists all lines passing through a stop (`lines`).
    - Identifies if a stop is a terminal (**terminal**) for any line.
    - Lists which lines terminate at that location (`lines_terminal`).
- **Financial Data**: Extracts fare prices (`fare`) linked to routes.
- **Localized Interface**: Attributes now in English (`service`, `line`, `agency`, `destination`, `direction`, `platform`, etc.).
- **Automatic Styling**: Applies official route colors and allows label configuration.

## 🛠 Installation

1. Ensure all plugin files are inside a folder named **`qgis_gtfs_plugin`**.
2. Copy this folder to the QGIS plugins directory according to your system:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles\default\python\plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

3. Restart QGIS and enable it in **Plugins** -> **Manage and Install Plugins**.

## 📖 Usage

1. Use the menu **Plugins** -> **GTFS 2 GIS** -> **Load GTFS...**.
2. Select the GTFS ZIP file.
3. The "Lines" and "Stops" layers will be created with all metadata.

## ⚙ Label Configuration

Labels are disabled by default to keep the map clean. To enable them, edit the layer properties in QGIS or modify the `core/layer_factory.py` file.

## ⚖ License

GNU GPL v3.
