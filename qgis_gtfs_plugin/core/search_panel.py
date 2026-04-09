# -*- coding: utf-8 -*-

import os
# Force pure-Python implementation to avoid "Descriptors cannot be created directly" error in newer protobuf versions
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from typing import Dict, Any
from qgis.PyQt import uic, QtWidgets, QtCore
from qgis.core import QgsProject, QgsMapLayerProxyModel
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox
# from .rt_manager import RTManager  <-- Moved to lazy import

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'search_panel.ui'))


class GTFSSearchPanel(QtWidgets.QDockWidget, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(GTFSSearchPanel, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface

        self.btn_apply.clicked.connect(self.apply_filters)
        self.btn_clear.clicked.connect(self.clear_filters)
        self.btn_pop_analysis.clicked.connect(self.run_population_analysis)
        self.btn_desert_finder.clicked.connect(self.run_desert_finder)

        self.btn_frequency_heatmap.clicked.connect(self.run_frequency_heatmap)
        self.btn_real_isochrones.clicked.connect(self.run_real_isochrones)

        # Real-time Tracker
        self.rt_manager = None
        self.btn_start_rt.clicked.connect(self.start_rt_tracking)
        self.btn_stop_rt.clicked.connect(self.stop_rt_tracking)
        self.btn_install_deps.clicked.connect(self.install_dependencies)

        # Check dependencies on startup
        self.check_rt_dependencies()

    @staticmethod
    def _exec_dialog(dialog: QtWidgets.QDialog) -> int:
        """Executes a modal dialog in a way that works in Qt5 and Qt6."""
        if hasattr(dialog, "exec"):
            return dialog.exec()
        return dialog.exec_()

    @staticmethod
    def _horizontal_orientation():
        """Returns horizontal orientation enum compatible with Qt5 and Qt6."""
        return getattr(QtCore.Qt, "Horizontal", QtCore.Qt.Orientation.Horizontal)

    @staticmethod
    def _ok_cancel_buttons():
        """Returns OK/Cancel button flags compatible with Qt5 and Qt6."""
        standard_button = getattr(QtWidgets.QDialogButtonBox, "StandardButton", None)
        if standard_button is not None:
            return standard_button.Ok | standard_button.Cancel
        return QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

    def update_stats(self, stats: Dict[str, Any]):
        """Updates the dashboard labels with calculated statistics."""
        self.val_total_km.setText(f"{stats.get('total_km', 0):.1f} km")
        self.val_stop_density.setText(f"{stats.get('stop_density', 0):.2f} /km²")
        self.val_routes.setText(str(stats.get('routes_count', 0)))

        # New stats
        self.val_trips.setText(str(stats.get('trips_count', 0)))
        self.val_avg_len.setText(f"{stats.get('avg_shape_len', 0):.1f} km")
        self.val_agencies.setText(str(stats.get('agencies_count', 0)))
        self.val_total_stops.setText(str(stats.get('stops_count', 0)))
        self.val_area.setText(f"{stats.get('area_km2', 0):.2f} km²")

        # Agency Fleet
        self.list_agency_fleet.clear()
        agency_trips = stats.get('agency_trips', {})
        for agency, trips in sorted(agency_trips.items(), key=lambda x: x[1], reverse=True):
            self.list_agency_fleet.addItem(f"{agency}: {trips} trips")

    def run_population_analysis(self):
        """Opens a dialog to select Census layer and field, then calculates coverage."""
        dialog = QtWidgets.QDialog(self.iface.mainWindow())
        dialog.setWindowTitle("Population Coverage Analysis")
        layout = QtWidgets.QVBoxLayout(dialog)

        layout.addWidget(QtWidgets.QLabel("Select Census Layer (IBGE):"))
        layer_combo = QgsMapLayerComboBox(dialog)
        layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        layout.addWidget(layer_combo)

        layout.addWidget(QtWidgets.QLabel("Select Population Field (V0001):"))
        field_combo = QgsFieldComboBox(dialog)
        field_combo.setLayer(layer_combo.currentLayer())
        layout.addWidget(field_combo)
        layer_combo.layerChanged.connect(field_combo.setLayer)

        layout.addWidget(QtWidgets.QLabel("Select Reach Layer (Walking/Network):"))
        reach_combo = QgsMapLayerComboBox(dialog)
        reach_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        for layer in QgsProject.instance().mapLayers().values():
            if "reach" in layer.name().lower() or "Walking Reach" in layer.name():
                reach_combo.setLayer(layer)
                break
        layout.addWidget(reach_combo)

        buttons = QtWidgets.QDialogButtonBox(
            self._ok_cancel_buttons(),
            self._horizontal_orientation(), dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if self._exec_dialog(dialog):
            census_layer = layer_combo.currentLayer()
            pop_field = field_combo.currentField()
            walking_layer = reach_combo.currentLayer()

            if not census_layer or not pop_field or not walking_layer:
                return

            from .layer_factory import LayerFactory
            total_pop = LayerFactory.calculate_population_coverage(
                walking_layer, census_layer, pop_field
            )

            QtWidgets.QMessageBox.information(
                self.iface.mainWindow(),
                "Analysis Result",
                f"Total estimated population within reach:\n\n"
                f"<b>{total_pop:,.0f} people</b>"
            )

    def run_desert_finder(self):
        """Opens a dialog to select Census layer and field, then identifies transit deserts."""
        dialog = QtWidgets.QDialog(self.iface.mainWindow())
        dialog.setWindowTitle("Transit Desert Finder")
        layout = QtWidgets.QVBoxLayout(dialog)

        layout.addWidget(QtWidgets.QLabel("Select Census Layer (IBGE):"))
        layer_combo = QgsMapLayerComboBox(dialog)
        layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        layout.addWidget(layer_combo)

        layout.addWidget(QtWidgets.QLabel("Select Population Field (V0001):"))
        field_combo = QgsFieldComboBox(dialog)
        field_combo.setLayer(layer_combo.currentLayer())
        layout.addWidget(field_combo)
        layer_combo.layerChanged.connect(field_combo.setLayer)

        layout.addWidget(QtWidgets.QLabel("Select Reach Layer (Walking/Network):"))
        reach_combo = QgsMapLayerComboBox(dialog)
        reach_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        for layer in QgsProject.instance().mapLayers().values():
            if "reach" in layer.name().lower() or "Walking Reach" in layer.name():
                reach_combo.setLayer(layer)
                break
        layout.addWidget(reach_combo)

        buttons = QtWidgets.QDialogButtonBox(
            self._ok_cancel_buttons(),
            self._horizontal_orientation(), dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if self._exec_dialog(dialog):
            census_layer = layer_combo.currentLayer()
            pop_field = field_combo.currentField()
            walking_layer = reach_combo.currentLayer()

            if not census_layer or not pop_field or not walking_layer:
                return

            # Create desert layer
            from .layer_factory import LayerFactory
            desert_layer = LayerFactory.create_transit_deserts_layer(
                walking_layer, census_layer, pop_field
            )

            if desert_layer:
                count = desert_layer.featureCount()
                QtWidgets.QMessageBox.information(
                    self.iface.mainWindow(),
                    "Desert Finder Result",
                    f"Analysis complete!\n\n"
                    f"Identified <b>{count}</b> sectors with population but NO transit reach.\n"
                    f"Layer 'Transit Deserts' has been added to the map."
                )

    def run_frequency_heatmap(self):
        """Applies a graduated frequency-based renderer to the Lines layer."""
        lines_layer = None
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name().endswith("Lines"):
                lines_layer = layer
                break

        if not lines_layer:
            QtWidgets.QMessageBox.warning(self, "Error", "Lines layer not found. Load a GTFS first.")
            return

        from .layer_factory import LayerFactory
        LayerFactory.create_frequency_heatmap_layer(lines_layer)
        QtWidgets.QMessageBox.information(self, "Success", "Layer 'lines - heatmap' created.")

    def run_real_isochrones(self):
        """Opens a dialog to select a road layer and walking time, then generates network reach."""
        dialog = QtWidgets.QDialog(self.iface.mainWindow())
        dialog.setWindowTitle("Real Network Isochrones")
        layout = QtWidgets.QVBoxLayout(dialog)

        layout.addWidget(QtWidgets.QLabel("Select Road/Street Network Layer:"))
        layer_combo = QgsMapLayerComboBox(dialog)
        layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        layout.addWidget(layer_combo)

        layout.addWidget(QtWidgets.QLabel("Walking Time (minutes):"))
        time_input = QtWidgets.QSpinBox(dialog)
        time_input.setRange(1, 30)
        time_input.setValue(5)
        layout.addWidget(time_input)

        layout.addWidget(QtWidgets.QLabel("Walking Speed (km/h):"))
        speed_input = QtWidgets.QDoubleSpinBox(dialog)
        speed_input.setRange(1.0, 10.0)
        speed_input.setSingleStep(0.5)
        speed_input.setValue(5.0)
        layout.addWidget(speed_input)

        buttons = QtWidgets.QDialogButtonBox(
            self._ok_cancel_buttons(),
            self._horizontal_orientation(), dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if self._exec_dialog(dialog):
            road_layer = layer_combo.currentLayer()
            walk_time = time_input.value()
            walk_speed = speed_input.value()

            if not road_layer:
                return

            # Distance in meters
            distance = (walk_speed * 1000 / 60) * walk_time

            stops_layer = None
            for layer in QgsProject.instance().mapLayers().values():
                if layer.name().endswith("Stops"):
                    stops_layer = layer
                    break

            if not stops_layer:
                QtWidgets.QMessageBox.warning(self, "Error", "Stops layer not found.")
                return

            from .layer_factory import LayerFactory
            LayerFactory.create_network_isochrones(road_layer, stops_layer, distance)
            QtWidgets.QMessageBox.information(self, "Success", f"Network reach layer created for {walk_time} min walk.")

    def apply_filters(self):
        """Applies filters to the visible layers."""
        period = self.filter_period.currentText()
        layers = QgsProject.instance().mapLayers().values()

        # 1. Filter Stops (Removed name search)
        stop_layers = [layer for layer in layers if layer.name() == "Stops"]
        for layer in stop_layers:
            layer.setSubsetString('')

        # 2. Filter Lines (by Period)
        line_layers = [layer for layer in layers if layer.name() == "Lines"]
        for layer in line_layers:
            if period != "All Periods":
                layer.setSubsetString(f'"start_period" = \'{period}\'')
            else:
                layer.setSubsetString('')

        self.iface.mapCanvas().refresh()

    def clear_filters(self):
        """Removes all subsets from layers."""
        self.filter_period.setCurrentIndex(0)

        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            lname = layer.name().lower()
            layer_fields = {field.name() for field in layer.fields()}
            is_gtfs_line = "lines" in lname and "start_period" in layer_fields
            is_gtfs_stop = "stops" in lname and "stop_id" in layer_fields
            if is_gtfs_line or is_gtfs_stop:
                layer.setSubsetString('')

        self.iface.mapCanvas().refresh()

    def start_rt_tracking(self):
        """Initializes and starts the real-time tracker."""
        # Lazy import to prevent startup crash if protobuf is missing
        try:
            from .rt_manager import RTManager
            from .rt_processor import HAS_PROTOBUF
        except ImportError:
            HAS_PROTOBUF = False

        if not HAS_PROTOBUF:
            self.install_dependencies()
            return

        url = self.txt_rt_url.text().strip()
        if not url:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter a valid GTFS-RT URL.")
            return

        interval = self.spin_rt_interval.value()
        
        if not self.rt_manager:
            # Re-import here to ensure it's in scope if HAS_PROTOBUF is True
            from .rt_manager import RTManager
            self.rt_manager = RTManager(self.iface, url, interval)
            self.rt_manager.status_changed.connect(self.update_rt_status)
            
        self.rt_manager.interval = interval
        self.rt_manager.start()
        
        self.btn_start_rt.setEnabled(False)
        self.btn_stop_rt.setEnabled(True)
        self.lbl_rt_status.setStyleSheet("font-weight: bold; color: green;")

    def stop_rt_tracking(self):
        """Stops the real-time tracker."""
        if self.rt_manager:
            self.rt_manager.stop()
            
        self.btn_start_rt.setEnabled(True)
        self.btn_stop_rt.setEnabled(False)
        self.lbl_rt_status.setStyleSheet("font-weight: bold; color: gray;")

    def update_rt_status(self, message: str):
        """Callback from RTManager to update the UI status label."""
        self.lbl_rt_status.setText(f"Status: {message}")

    def check_rt_dependencies(self):
        """Hides the install button if protobuf is already present."""
        try:
            from .rt_processor import HAS_PROTOBUF
        except ImportError:
            HAS_PROTOBUF = False
        
        self.btn_install_deps.setVisible(not HAS_PROTOBUF)

    def install_dependencies(self):
        """Attempts to install protobuf using pip within the QGIS environment."""
        self.lbl_rt_status.setText("Status: Installing dependencies...")
        self.lbl_rt_status.setStyleSheet("font-weight: bold; color: blue;")
        QtWidgets.QApplication.processEvents()
        
        try:
            import sys
            import os
            import subprocess
            
            # 1. Identify the correct Python executable
            # If sys.executable is the QGIS binary (e.g., qgis-bin.exe), it will try to open args as layers.
            # We must find the companion python.exe.
            py_exe = sys.executable
            if "qgis" in os.path.basename(py_exe).lower():
                bin_dir = os.path.dirname(py_exe)
                # Candidates for OSGeo4W / Windows installs
                for candidate in ["python3.exe", "python.exe", "pythonw.exe"]:
                    path = os.path.join(bin_dir, candidate)
                    if os.path.exists(path):
                        py_exe = path
                        break
            
            # 2. Run installation
            # Using CREATE_NO_WINDOW (0x08000000) on Windows to keep it silent
            creation_flags = 0
            if os.name == 'nt':
                creation_flags = 0x08000000

            subprocess.check_call(
                [py_exe, "-m", "pip", "install", "protobuf"],
                creationflags=creation_flags
            )
            
            QtWidgets.QMessageBox.information(
                self, "Success", 
                "Dependencies installed successfully!\n"
                "Please restart QGIS to apply changes correctly."
            )
            self.check_rt_dependencies()
            self.lbl_rt_status.setText("Status: Restart Required")
            self.lbl_rt_status.setStyleSheet("font-weight: bold; color: orange;")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Installation Failed", 
                f"Failed to install 'protobuf' using {py_exe}\n\n"
                f"Error: {str(e)}\n\n"
                "Please try manual installation via 'OSGeo4W Shell' if available."
            )
            self.lbl_rt_status.setText("Status: Install Failed")
            self.lbl_rt_status.setStyleSheet("font-weight: bold; color: red;")
