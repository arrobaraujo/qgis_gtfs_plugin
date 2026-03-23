# -*- coding: utf-8 -*-

import os
import zipfile
import csv
import io
from qgis.PyQt import QtCore, QtGui, QtWidgets
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsField,
    QgsPalLayerSettings,
    QgsVectorLayerSimpleLabeling,
    QgsTextFormat,
    QgsFields,
    QgsSymbol,
    QgsSymbolLayer,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer,
    QgsProperty
)

from .gtfs_loader_dialog import GTFSLoaderDialog

class GTFSLoader:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.action = QtWidgets.QAction("Carregar Shapes & Paradas GTFS", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&Carregador GTFS", self.action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu("&Carregador GTFS", self.action)

    def run(self):
        """Run method that performs all the real work"""
        dialog = GTFSLoaderDialog()
        if dialog.exec_():
            zip_path = dialog.get_selected_file()
            if not zip_path or not os.path.exists(zip_path):
                QtWidgets.QMessageBox.warning(self.iface.mainWindow(), "Error", "Please select a valid ZIP file.")
                return
            
            try:
                self.process_gtfs(zip_path)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.iface.mainWindow(), "Error", f"Failed to process GTFS: {str(e)}")

    def process_gtfs(self, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as z:
            files = z.namelist()
            
            # 0. Parse Agency
            agencies = {}
            if 'agency.txt' in files:
                with z.open('agency.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                    for row in reader:
                        aid = row.get('agency_id', '')
                        agencies[aid] = row['agency_name']
                        # If no agency_id, use as default
                        if not aid:
                            agencies['DEFAULT'] = row['agency_name']
            
            # 1. Parse Routes
            routes = {}
            if 'routes.txt' in files:
                with z.open('routes.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                    for row in reader:
                        routes[row['route_id']] = {
                            'short_name': row.get('route_short_name', ''),
                            'long_name': row.get('route_long_name', ''),
                            'desc': row.get('route_desc', ''),
                            'agency_id': row.get('agency_id', ''),
                            'type': row.get('route_type', '3'), # Default 3 (Bus)
                            'color': row.get('route_color', '000000')
                        }

            # 1.5 Parse Fares
            fares = {}
            if 'fare_attributes.txt' in files:
                with z.open('fare_attributes.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                    for row in reader:
                        fares[row['fare_id']] = row.get('price', '0.00')

            route_to_price = {}
            if 'fare_rules.txt' in files:
                with z.open('fare_rules.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                    for row in reader:
                        rid = row['route_id']
                        fid = row['fare_id']
                        if fid in fares:
                            # Just take the first price found for a route for simplicity
                            if rid not in route_to_price:
                                route_to_price[rid] = fares[fid]

            # 2. Parse Trips
            trips = []
            if 'trips.txt' in files:
                with z.open('trips.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                    for row in reader:
                        trips.append({
                            'trip_id': row['trip_id'],
                            'route_id': row['route_id'],
                            'shape_id': row.get('shape_id', ''),
                            'headsign': row.get('trip_headsign', ''),
                            'short_name': row.get('trip_short_name', ''),
                            'direction': row.get('direction_id', '')
                        })

            # 3. Parse Shapes
            shapes = {}
            if 'shapes.txt' in files:
                with z.open('shapes.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                    for row in reader:
                        sid = row['shape_id']
                        if sid not in shapes:
                            shapes[sid] = []
                        shapes[sid].append({
                            'lat': float(row['shape_pt_lat']),
                            'lon': float(row['shape_pt_lon']),
                            'seq': int(row['shape_pt_sequence'])
                        })

            # 4. Parse Stops
            stops = []
            if 'stops.txt' in files:
                with z.open('stops.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                    for row in reader:
                        stops.append({
                            'id': row['stop_id'],
                            'name': row.get('stop_name', row['stop_id']),
                            'lat': float(row['stop_lat']),
                            'lon': float(row['stop_lon']),
                            'location_type': row.get('location_type', '0'),
                            'parent_station': row.get('parent_station', ''),
                            'stop_code': row.get('stop_code', ''),
                            'platform_code': row.get('platform_code', ''),
                            'stop_desc': row.get('stop_desc', '')
                        })

            # Create Layers
            self.create_shape_layer(trips, shapes, routes, agencies, route_to_price)
            self.create_stop_layer(stops)

    def create_shape_layer(self, trips, shapes, routes, agencies, route_to_price):
        if not shapes:
            return

        # 1. Map shape_id to a representative trip (the first one found)
        shape_to_trip = {}
        for t in trips:
            sid = t['shape_id']
            if sid and sid not in shape_to_trip:
                shape_to_trip[sid] = t

        # Create memory layer
        layer = QgsVectorLayer("LineString?crs=epsg:4326", "GTFS Shapes", "memory")
        pr = layer.dataProvider()
        
        # Add attributes
        pr.addAttributes([
            QgsField("shape_id", QtCore.QVariant.String),
            QgsField("route_id", QtCore.QVariant.String),
            QgsField("linha", QtCore.QVariant.String),
            QgsField("nome", QtCore.QVariant.String),
            QgsField("route_desc", QtCore.QVariant.String),
            QgsField("operador", QtCore.QVariant.String),
            QgsField("destino", QtCore.QVariant.String),
            QgsField("sentido", QtCore.QVariant.String),
            QgsField("transit_type", QtCore.QVariant.String),
            QgsField("tarifa", QtCore.QVariant.String),
            QgsField("color", QtCore.QVariant.String)
        ])
        layer.updateFields()

        features = []
        for sid, points in shapes.items():
            # Get representative trip for this shape
            trip = shape_to_trip.get(sid)
            if not trip:
                # Still add it if it exists in shapes.txt even if no trip links to it
                trip = {'route_id': '', 'headsign': '', 'short_name': '', 'direction': ''}
            
            # Sort points by sequence
            sorted_pts = sorted(points, key=lambda x: x['seq'])
            qgs_points = [QgsPointXY(p['lon'], p['lat']) for p in sorted_pts]
            
            if len(qgs_points) < 2:
                continue

            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPolylineXY(qgs_points))
            
            route_id = trip['route_id']
            route_info = routes.get(route_id, {})
            route_name = route_info.get('short_name', '') or route_info.get('long_name', '')
            route_long_name = route_info.get('long_name', '')
            route_desc = route_info.get('desc', '')
            agency_id = route_info.get('agency_id', '')
            agency_name = agencies.get(agency_id) or agencies.get('DEFAULT', '')
            
            transit_type = route_info.get('type', '3')
            color = route_info.get('color', '000000')
            if not color.startswith('#'):
                color = '#' + color
                
            trip_name = trip['headsign'] or trip['short_name'] or ''

            feat.setAttributes([
                sid,
                route_id, 
                route_name, 
                route_long_name,
                route_desc,
                agency_name,
                trip_name,
                trip['direction'],
                transit_type,
                route_to_price.get(route_id, ''),
                color
            ])
            features.append(feat)

        pr.addFeatures(features)
        layer.updateExtents()
        
        # Apply data-defined color styling to each symbol layer
        symbol = layer.renderer().symbol()
        if symbol:
            for i in range(symbol.symbolLayerCount()):
                sl = symbol.symbolLayer(i)
                sl.setDataDefinedProperty(QgsSymbolLayer.PropertyStrokeColor, QgsProperty.fromField("color"))
        
        # Add to project
        QgsProject.instance().addMapLayer(layer)

    def create_stop_layer(self, stops):
        if not stops:
            return

        layer = QgsVectorLayer("Point?crs=epsg:4326", "GTFS Stops", "memory")
        pr = layer.dataProvider()
        
        pr.addAttributes([
            QgsField("stop_id", QtCore.QVariant.String),
            QgsField("nome", QtCore.QVariant.String),
            QgsField("location_type", QtCore.QVariant.String),
            QgsField("parent_station", QtCore.QVariant.String),
            QgsField("stop_code", QtCore.QVariant.String),
            QgsField("plataforma", QtCore.QVariant.String),
            QgsField("stop_desc", QtCore.QVariant.String),
            QgsField("lat", QtCore.QVariant.Double),
            QgsField("lon", QtCore.QVariant.Double)
        ])
        layer.updateFields()

        features = []
        for s in stops:
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(s['lon'], s['lat'])))
            feat.setAttributes([
                s['id'], 
                s['name'], 
                s['location_type'], 
                s['parent_station'],
                s['stop_code'],
                s['platform_code'],
                s['stop_desc'],
                s['lat'],
                s['lon']
            ])
            features.append(feat)

        pr.addFeatures(features)
        layer.updateExtents()
        
        # Labeling (Optional but good)
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = "nome"
        text_format = QgsTextFormat()
        text_format.setSize(8)
        label_settings.setFormat(text_format)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        layer.setLabelsEnabled(True)

        QgsProject.instance().addMapLayer(layer)
