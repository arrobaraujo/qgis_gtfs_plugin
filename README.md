# GTFS 2 GIS

QGIS plugin for visualizing and analyzing public transit networks from GTFS ZIP files.

## 🚀 Key Features

- **Optimized Shapes**: Groups trips by `shape_id` to avoid overlapping lines, with frequency-based line widths.
- **Stop Intelligence**:
    - Lists all lines passing through a stop.
    - Identifies terminal stops and which lines terminate there.
    - Transit-type icons (🚌 Bus, 🚇 Subway, 🚄 Rail, 🚃 Tram, ⛴️ Ferry).
- **Financial Data**: Extracts fare prices linked to routes.
- **Automatic Styling**: Applies official route colors from GTFS data.
- **Analytics Dashboard**: Real-time stats panel with total km, stop density, routes, trips, agencies, and fleet breakdown.
- **Period Filtering**: Filter lines by time period (Morning Peak, Midday, Evening Peak, Night).

## 🔧 Analysis Tools

- **Frequency Heatmap**: Generates a graduated layer showing route frequency intensity.
- **Population Coverage**: Calculates population served within walking reach using IBGE census data.
- **Transit Desert Finder**: Identifies populated areas with no or minimal transit access.
- **Walking Reach**: Creates 400m buffer zones around all stops.
- **Real Isochrones**: Network-based service area analysis using road layers.

## 🛠 Installation

1. Ensure all plugin files are inside a folder named **`qgis_gtfs_plugin`**.
2. Copy this folder to the QGIS plugins directory:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS and enable it in **Plugins** -> **Manage and Install Plugins**.

## 📖 Usage

1. Use the menu **Plugins** -> **GTFS 2 GIS** -> **Load GTFS...**.
2. Select a GTFS ZIP file.
3. The "Lines" and "Stops" layers are created with all metadata.
4. Use the **GTFS Analytics** panel for filtering, statistics, and analysis tools.

## ⚙ Requirements

- QGIS >= 3.4

## ⚖ License

GNU GPL v3.
