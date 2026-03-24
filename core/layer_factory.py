# -*- coding: utf-8 -*-

from qgis.PyQt import QtCore, QtGui
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
    QgsTextBufferSettings,
    QgsProperty,
    QgsSymbolLayer,
    QgsFontMarkerSymbolLayer,
    QgsMarkerSymbol,
    QgsSingleSymbolRenderer
)
from typing import Dict, List, Set, Any

class LayerFactory:
    """Handles the creation and styling of QGIS layers from processed GTFS data."""

    @staticmethod
    def create_shape_layer(trips: List[Dict[str, Any]], 
                           shapes: Dict[str, List[Dict[str, Any]]], 
                           routes: Dict[str, Dict[str, Any]], 
                           agencies: Dict[str, str], 
                           route_to_price: Dict[str, str]) -> None:
        if not shapes:
            return

        shape_to_trip = {}
        for t in trips:
            sid = t['shape_id']
            if sid and sid not in shape_to_trip:
                shape_to_trip[sid] = t

        layer = QgsVectorLayer("LineString?crs=epsg:4326", "Lines", "memory")
        pr = layer.dataProvider()
        
        pr.addAttributes([
            QgsField("shape_id", QtCore.QVariant.String),
            QgsField("route_id", QtCore.QVariant.String),
            QgsField("service", QtCore.QVariant.String),
            QgsField("line", QtCore.QVariant.String),
            QgsField("route_desc", QtCore.QVariant.String),
            QgsField("agency", QtCore.QVariant.String),
            QgsField("destination", QtCore.QVariant.String),
            QgsField("direction", QtCore.QVariant.String),
            QgsField("transit_type", QtCore.QVariant.String),
            QgsField("fare", QtCore.QVariant.String),
            QgsField("color", QtCore.QVariant.String)
        ])
        layer.updateFields()

        features = []
        for sid, points in shapes.items():
            trip = shape_to_trip.get(sid, {'route_id': '', 'headsign': '', 'short_name': '', 'direction': ''})
            
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
                sid, route_id, route_name, route_long_name, route_desc,
                agency_name, trip_name, trip['direction'], transit_type,
                route_to_price.get(route_id, ''), color
            ])
            features.append(feat)

        pr.addFeatures(features)
        layer.updateExtents()
        
        # Styling
        symbol = layer.renderer().symbol()
        if symbol:
            for i in range(symbol.symbolLayerCount()):
                sl = symbol.symbolLayer(i)
                sl.setDataDefinedProperty(QgsSymbolLayer.PropertyStrokeColor, QgsProperty.fromField("color"))
        
        # Labeling
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = "service"
        label_settings.placement = QgsPalLayerSettings.Line
        
        text_format = QgsTextFormat()
        text_format.setSize(8)
        text_format.setColor(QtGui.QColor(0, 0, 0))
        
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QtGui.QColor(255, 255, 255))
        text_format.setBuffer(buffer_settings)
        
        layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        layer.setDisplayExpression("service")
        
        QgsProject.instance().addMapLayer(layer)

    @staticmethod
    def create_stop_layer(stops: Dict[str, Dict[str, Any]], 
                           stop_to_routes: Dict[str, Set[str]], 
                           stop_to_pf_routes: Dict[str, Set[str]], 
                           routes: Dict[str, Dict[str, Any]]) -> None:
        if not stops:
            return

        layer = QgsVectorLayer("Point?crs=epsg:4326", "Stops", "memory")
        pr = layer.dataProvider()
        
        pr.addAttributes([
            QgsField("stop_id", QtCore.QVariant.String),
            QgsField("name", QtCore.QVariant.String),
            QgsField("location_type", QtCore.QVariant.String),
            QgsField("parent_station", QtCore.QVariant.String),
            QgsField("stop_code", QtCore.QVariant.String),
            QgsField("platform", QtCore.QVariant.String),
            QgsField("lines", QtCore.QVariant.String),
            QgsField("terminal", QtCore.QVariant.String),
            QgsField("lines_terminal", QtCore.QVariant.String),
            QgsField("stop_desc", QtCore.QVariant.String),
            QgsField("lat", QtCore.QVariant.Double),
            QgsField("lon", QtCore.QVariant.Double)
        ])
        layer.updateFields()

        features = []
        for stop_id, s in stops.items():
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(s['lon'], s['lat'])))
            
            # General routes
            route_ids = stop_to_routes.get(stop_id, [])
            route_names = []
            for rid in route_ids:
                rinfo = routes.get(rid, {})
                route_names.append(rinfo.get('short_name') or rinfo.get('long_name') or rid)
            route_names_str = ", ".join(sorted(list(set(route_names))))

            # Terminal routes
            pf_route_ids = stop_to_pf_routes.get(stop_id, [])
            pf_route_names = []
            for rid in pf_route_ids:
                rinfo = routes.get(rid, {})
                pf_route_names.append(rinfo.get('short_name') or rinfo.get('long_name') or rid)
            pf_route_names_str = ", ".join(sorted(list(set(pf_route_names))))
            is_pf = "yes" if pf_route_names_str else ""

            feat.setAttributes([
                stop_id, s['name'], s['location_type'], s['parent_station'],
                s['stop_code'], s.get('platform_code', ''), route_names_str,
                is_pf, pf_route_names_str, s['stop_desc'], s['lat'], s['lon']
            ])
            features.append(feat)

        pr.addFeatures(features)
        layer.updateExtents()
        
        # Styling
        font_marker = QgsFontMarkerSymbolLayer()
        font_marker.setCharacter('🚏')
        # Use a common font that supports emoji if possible, or leave default
        # font_marker.setFontFamily('Segoe UI Emoji') 
        font_marker.setSize(2.5)
        font_marker.setColor(QtGui.QColor(0, 0, 0))
        
        symbol = QgsMarkerSymbol()
        symbol.changeSymbolLayer(0, font_marker)
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))

        # Labeling
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = "name"
        text_format = QgsTextFormat()
        text_format.setSize(8)
        label_settings.setFormat(text_format)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        layer.setDisplayExpression("name")

        QgsProject.instance().addMapLayer(layer)
