# -*- coding: utf-8 -*-

import os
from qgis.PyQt import QtWidgets
from .ui.gtfs_dialog import GTFSDialog
from .core.processor import GTFSProcessor
from .core.layer_factory import LayerFactory

class GTFSLoader:
    """Main Class for the QGIS GTFS Loader Plugin."""

    def __init__(self, iface):
        """Constructor."""
        self.iface = iface
        self.action = None

    def initGui(self):
        """Create the menu entries and toolbar icons in QGIS."""
        self.action = QtWidgets.QAction(
            "Load GTFS...", 
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&GTFS 2 GIS", self.action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        if self.action:
            self.iface.removePluginMenu("&GTFS 2 GIS", self.action)

    def run(self):
        """Main execution loop of the plugin."""
        dialog = GTFSDialog(self.iface.mainWindow())
        
        if dialog.exec_():
            zip_path = dialog.get_selected_file()
            
            if not zip_path or not os.path.exists(zip_path):
                QtWidgets.QMessageBox.warning(
                    self.iface.mainWindow(), 
                    "Error", 
                    "Please select a valid ZIP file."
                )
                return
            
            try:
                self.process_gtfs(zip_path)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self.iface.mainWindow(), 
                    "Fatal Error", 
                    f"Failed to process GTFS: {str(e)}"
                )

    def process_gtfs(self, zip_path: str):
        """Coordinates the parsing and layer creation."""
        # 1. Process GTFS data
        processor = GTFSProcessor(zip_path)
        processor.process()

        # 2. Create Layers
        LayerFactory.create_shape_layer(
            processor.trips,
            processor.shapes,
            processor.routes,
            processor.agencies,
            processor.route_to_price
        )
        
        LayerFactory.create_stop_layer(
            processor.stops,
            processor.stop_to_routes,
            processor.stop_to_pf_routes,
            processor.routes
        )
