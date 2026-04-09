# -*- coding: utf-8 -*-

import time
from datetime import datetime
from qgis.PyQt import QtCore
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPointXY, QgsField, QgsMessageLog, Qgis
)
from .rt_processor import GTFSRTProcessor
from .layer_factory import LayerFactory
from .utils import build_field


class RTManager(QtCore.QObject):
    """Manages the Real-time GTFS lifecycle and map updates."""

    status_changed = QtCore.pyqtSignal(str)  # Status message for the UI

    def __init__(self, iface, url: str, interval_seconds: int = 30):
        super().__init__()
        self.iface = iface
        self.url = url
        self.interval = interval_seconds
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_rt_data)

        self.processor = GTFSRTProcessor(url)
        self.layer = None

    def set_url(self, url: str):
        """Updates the feed URL and re-initializes the processor."""
        if self.url != url:
            self.url = url
            self.processor = GTFSRTProcessor(url)
            # Optional: Clear layer if switching sources entirely?
            # For now we just update the processor.

    def start(self):
        """Starts the real-time tracking."""
        if not self._is_layer_valid():
            self.layer = self._create_rt_layer()

        self.update_rt_data()

        # Ensure no overlapping timers
        self.timer.stop()
        self.timer.start(self.interval * 1000)
        self.status_changed.emit(f"Active (every {self.interval}s)")

    def stop(self):
        """Stops the real-time tracking."""
        self.timer.stop()
        self.status_changed.emit("Stopped")

    def _is_layer_valid(self) -> bool:
        """Checks if the layer still exists and is not deleted."""
        if not self.layer:
            return False
        return QgsProject.instance().mapLayer(self.layer.id()) is not None

    def _create_rt_layer(self) -> QgsVectorLayer:
        """Creates a memory layer for vehicle positions."""
        # Find if layer already exists
        existing = QgsProject.instance().mapLayersByName("GTFS Real-time Vehicles")
        if existing:
            return existing[0]

        uri = "Point?crs=EPSG:4326"
        layer = QgsVectorLayer(uri, "GTFS Real-time Vehicles", "memory")

        # Add fields
        pr = layer.dataProvider()
        pr.addAttributes([
            build_field("vehicle_id", QtCore.QVariant.String),
            build_field("route_id", QtCore.QVariant.String),
            build_field("trip_id", QtCore.QVariant.String),
            build_field("bearing", QtCore.QVariant.Double),
            build_field("speed", QtCore.QVariant.Double),
            build_field("last_update", QtCore.QVariant.String)
        ])
        layer.updateFields()

        # Apply symbology via LayerFactory
        LayerFactory.apply_rt_symbology(layer)

        QgsProject.instance().addMapLayer(layer)
        return layer

    def update_rt_data(self):
        """Fetches new data and updates the layer features."""
        try:
            vehicles = self.processor.fetch_vehicle_positions()

            if not self._is_layer_valid():
                # Try to recover the layer reference or recreate if it was deleted
                self.layer = self._create_rt_layer()

            if not self.layer:
                return

            pr = self.layer.dataProvider()

            # Start editing
            self.layer.startEditing()

            # Clear existing features (simple approach for real-time)
            # Alternatively, update existing ones to preserve selection/style
            self.layer.dataProvider().truncate()

            new_features = []
            now_str = datetime.now().strftime("%H:%M:%S")

            for v in vehicles:
                feat = QgsFeature(self.layer.fields())
                feat.setGeometry(
                    QgsGeometry.fromPointXY(
                        QgsPointXY(
                            v['lon'],
                            v['lat'])))
                feat.setAttributes([
                    v['vehicle_id'],
                    v['route_id'],
                    v['trip_id'],
                    float(v['bearing']),
                    float(v['speed']),
                    now_str
                ])
                new_features.append(feat)

            pr.addFeatures(new_features)
            self.layer.commitChanges()

            # Update status
            self.status_changed.emit(
                f"Last update: {now_str} ({
                    len(vehicles)} vehicles)")
            self.iface.mapCanvas().refresh()

        except Exception as e:
            QgsMessageLog.logMessage(
                f"RT Error: {
                    str(e)}",
                "GTFS",
                Qgis.Warning)
            self.status_changed.emit(f"Error: {time.strftime('%H:%M:%S')}")
            # Don't stop the timer, try again next interval
