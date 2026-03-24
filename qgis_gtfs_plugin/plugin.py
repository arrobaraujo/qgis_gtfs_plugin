# -*- coding: utf-8 -*-

import os
from qgis.PyQt import QtWidgets, QtCore
from .ui.gtfs_dialog import GTFSDialog
from .core.processor import GTFSProcessor
from .core.layer_factory import LayerFactory
from .core.search_panel import GTFSSearchPanel


class GTFSLoader:
    """Main Class for the QGIS GTFS Loader Plugin."""

    def __init__(self, iface):
        """Constructor."""
        self.iface = iface
        self.action = None
        self.search_action = None
        self.search_panel = None

    def initGui(self):
        """Create the menu entries and toolbar icons in QGIS."""
        self.action = QtWidgets.QAction(
            "Load GTFS...",
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)

        self.search_action = QtWidgets.QAction(
            "Show Menu Panel",
            self.iface.mainWindow()
        )
        self.search_action.triggered.connect(self.toggle_search_panel)

        self.iface.addPluginToMenu("&GTFS 2 GIS", self.action)
        self.iface.addPluginToMenu("&GTFS 2 GIS", self.search_action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        if self.action:
            self.iface.removePluginMenu("&GTFS 2 GIS", self.action)
        if self.search_action:
            self.iface.removePluginMenu("&GTFS 2 GIS", self.search_action)
        if self.search_panel:
            self.iface.mainWindow().removeDockWidget(self.search_panel)

    def run(self):
        """Main execution loop of the plugin."""
        dialog = GTFSDialog(self.iface.mainWindow())

        if dialog.exec_():
            zip_path = dialog.get_selected_file()
            service_day = dialog.get_service_day()

            if not zip_path or not os.path.exists(zip_path):
                QtWidgets.QMessageBox.warning(
                    self.iface.mainWindow(),
                    "Error",
                    "Please select a valid ZIP file."
                )
                return

            try:
                self.process_gtfs(zip_path, service_day)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self.iface.mainWindow(),
                    "Fatal Error",
                    f"Failed to process GTFS: {str(e)}"
                )

    def process_gtfs(self, zip_path: str, service_day: str = 'All'):
        """Coordinates the parsing and layer creation."""
        # 1. Process GTFS data
        processor = GTFSProcessor(zip_path)
        processor.process(service_day)

        # 2. Create Layers
        LayerFactory.create_shape_layer(
            processor.trips,
            processor.shapes,
            processor.routes,
            processor.agencies,
            processor.route_to_price,
            processor.shape_frequencies,
            processor.shape_time_ranges
        )

        stop_layer = LayerFactory.create_stop_layer(
            processor.stops,
            processor.stop_to_routes,
            processor.stop_to_pf_routes,
            processor.stop_route_counts,
            processor.routes,
            processor.stop_route_types
        )

        # 3. Create Walking Reach layer (400m buffer)
        LayerFactory.create_walking_reach(stop_layer)

        # 4. Update Stats in Search Panel
        stats = processor.get_stats()
        if not self.search_panel:
            self.initialize_search_panel()
        self.search_panel.update_stats(stats)

    def initialize_search_panel(self):
        """Creates the search panel but keep it hidden by default."""
        if not self.search_panel:
            self.search_panel = GTFSSearchPanel(self.iface, self.iface.mainWindow())
            self.iface.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.search_panel)
            self.search_panel.setVisible(False)

    def toggle_search_panel(self):
        """Shows or creates the search panel."""
        if not self.search_panel:
            self.initialize_search_panel()
            self.search_panel.setVisible(True)
        else:
            # Toggle visibility
            self.search_panel.setVisible(not self.search_panel.isVisible())
