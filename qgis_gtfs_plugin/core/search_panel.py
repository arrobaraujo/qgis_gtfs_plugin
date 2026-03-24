# -*- coding: utf-8 -*-

import os
from typing import Dict, Any
from qgis.PyQt import uic, QtWidgets, QtCore
from qgis.core import QgsProject, QgsMapLayerProxyModel
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox

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
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_():
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
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_():
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
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_():
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
            if layer.name() in ["Stops", "Lines"]:
                layer.setSubsetString('')

        self.iface.mapCanvas().refresh()
