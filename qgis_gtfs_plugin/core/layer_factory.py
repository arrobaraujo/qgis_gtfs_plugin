# -*- coding: utf-8 -*-

import datetime
from qgis.PyQt import QtCore, QtGui
from qgis.PyQt.QtCore import QMetaType, QVariant
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
    QgsSimpleMarkerSymbolLayer,
    QgsSingleSymbolRenderer,
    QgsRuleBasedRenderer,
    QgsFeatureRequest,
    Qgis,
    QgsLineSymbol,
    QgsFillSymbol,
    QgsRendererRange,
    QgsGraduatedSymbolRenderer,
    QgsMessageLog,
    QgsApplication,
    QgsCoordinateTransform
)
from typing import Dict, List, Set, Any, Tuple, Optional


def _qmeta_type_from_qvariant(qvariant_type):
    """Returns a QMetaType enum value compatible with both Qt5/Qt6 APIs."""
    type_name_by_variant = {
        QVariant.String: "QString",
        QVariant.Int: "Int",
        QVariant.Double: "Double",
    }
    type_name = type_name_by_variant.get(qvariant_type)
    if not type_name:
        return None

    enum_container = getattr(QMetaType, "Type", None)
    if enum_container and hasattr(enum_container, type_name):
        return getattr(enum_container, type_name)
    if hasattr(QMetaType, type_name):
        return getattr(QMetaType, type_name)
    return None


def _build_field(name: str, qvariant_type) -> QgsField:
    """Creates QgsField with a modern type API and a safe backward fallback."""
    qmeta_type = _qmeta_type_from_qvariant(qvariant_type)
    if qmeta_type is not None:
        try:
            return QgsField(name, qmeta_type)
        except TypeError:
            pass
    return QgsField(name, qvariant_type)


class LayerFactory:
    """Handles the creation and styling of QGIS layers from processed GTFS data."""

    @staticmethod
    def create_shape_layer(
            trips: List[Dict[str, Any]],
            shapes: Dict[str, List[Dict[str, Any]]],
            routes: Dict[str, Dict[str, Any]],
            agencies: Dict[str, str],
            route_to_price: Dict[str, str],
            shape_frequencies: Dict[str, int],
            shape_time_ranges: Dict[str, Tuple[str, str]]) -> None:
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
            _build_field("shape_id", QVariant.String),
            _build_field("route_id", QVariant.String),
            _build_field("line", QVariant.String),
            _build_field("name", QVariant.String),
            _build_field("route_desc", QVariant.String),
            _build_field("agency", QVariant.String),
            _build_field("destination", QVariant.String),
            _build_field("direction", QVariant.String),
            _build_field("transit_type", QVariant.String),
            _build_field("fare", QVariant.String),
            _build_field("color", QVariant.String),
            _build_field("frequency", QVariant.Int),
            _build_field("shape_ext", QVariant.Int),
            _build_field("start_time", QVariant.String),
            _build_field("end_time", QVariant.String),
            _build_field("start_period", QVariant.String)
        ])
        layer.updateFields()

        import math
        # Distance calculator for shape_ext (ellipsoidal distance in meters)
        from qgis.core import QgsDistanceArea
        d_area = QgsDistanceArea()
        d_area.setEllipsoid('WGS84')

        features = []
        for sid, points in shapes.items():
            trip = shape_to_trip.get(sid, {'route_id': '', 'headsign': '', 'short_name': '', 'direction': ''})

            sorted_pts = sorted(points, key=lambda x: x['seq'])
            qgs_points = [QgsPointXY(p['lon'], p['lat']) for p in sorted_pts]

            if len(qgs_points) < 2:
                continue

            length_m = d_area.measureLine(qgs_points)
            length_int = int(math.ceil(length_m))

            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPolylineXY(qgs_points))

            route_id = trip['route_id']
            route_info = routes.get(route_id, {})
            route_name = route_info.get('short_name', '') or route_info.get('long_name', '')
            route_long_name = route_info.get('long_name', '')
            route_desc = route_info.get('desc', '')
            agency_id = route_info.get('agency_id', '')
            agency_data = agencies.get(agency_id, '')

            if isinstance(agency_data, dict):
                agency_name = agency_data.get('name', '')
            else:
                agency_name = agency_data or agencies.get('DEFAULT', '')

            transit_type = route_info.get('type', '3')
            color = route_info.get('color', '000000')
            if not color.startswith('#'):
                color = '#' + color

            trip_name = trip.get('headsign', '') or trip.get('short_name', '') or ''

            time_range = shape_time_ranges.get(sid, ('00:00:00', '23:59:59'))

            def format_gtfs_time(t_str):
                # Simple conversion for temporal controller (using today as base date)
                try:
                    h, m, s = map(int, t_str.split(':'))
                    base = datetime.date.today()
                    extra_days = 0
                    if h >= 24:
                        extra_days = h // 24
                        h = h % 24
                    d = base + datetime.timedelta(days=extra_days)
                    return f"{d.isoformat()} {h:02d}:{m:02d}:{s:02d}"
                except (ValueError, AttributeError):
                    return None

            start_t = format_gtfs_time(time_range[0])
            end_t = format_gtfs_time(time_range[1])

            def get_period(t_str):
                try:
                    h = int(t_str.split(':')[0])
                    if 6 <= h < 9:
                        return "Morning Peak"
                    if 9 <= h < 16:
                        return "Midday"
                    if 16 <= h < 19:
                        return "Evening Peak"
                    return "Night"
                except Exception:
                    return "Unknown"

            period = get_period(time_range[0])

            feat.setAttributes([
                str(sid), str(route_id), str(route_name), str(route_long_name), str(route_desc),
                str(agency_name), str(trip_name), str(trip.get('direction', '')), str(transit_type),
                str(route_to_price.get(route_id, '')), str(color),
                int(shape_frequencies.get(sid, 0)),
                int(length_int),
                str(start_t), str(end_t), str(period)
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
                # Base width 0.4, grows with frequency up to 2.5
                sl.setDataDefinedProperty(QgsSymbolLayer.PropertyStrokeWidth,
                                          QgsProperty.fromExpression('scale_linear("frequency", 1, 100, 0.4, 2.5)'))

        # Rendering Order: Thicker lines (higher frequency) at the bottom
        # QGIS renders from first to last, so we want high frequency first.
        # Set feature rendering order (high frequency/thicker lines at the bottom)
        renderer = layer.renderer()
        clause = QgsFeatureRequest.OrderByClause("frequency", False)  # Descending = drawn first = at bottom
        renderer.setOrderBy(QgsFeatureRequest.OrderBy([clause]))
        renderer.setOrderByEnabled(True)

        # Labeling
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = "line"
        label_settings.placement = QgsPalLayerSettings.Line

        text_format = QgsTextFormat()
        text_format.setSize(8)
        text_format.setColor(QtGui.QColor(0, 0, 0))

        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QtGui.QColor(255, 255, 255))
        text_format.setBuffer(buffer_settings)

        label_settings.setFormat(text_format)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        layer.setDisplayExpression("line")

        QgsProject.instance().addMapLayer(layer)
        return layer

    @staticmethod
    def create_frequency_heatmap_layer(source_layer: QgsVectorLayer):
        """Creates a new layer 'lines - heatmap' and applies a graduated renderer."""
        if not source_layer:
            return

        # Clone the layer
        heatmap_layer = QgsVectorLayer(
            source_layer.source(),
            "lines - heatmap",
            source_layer.providerType()
        )

        # Copy features
        pr = heatmap_layer.dataProvider()
        pr.addAttributes(source_layer.fields())
        heatmap_layer.updateFields()
        pr.addFeatures([f for f in source_layer.getFeatures()])

        my_range = []
        styles = [
            (1, 10, "#ffffb2", 0.6, "Low (1-10)"),
            (11, 40, "#fecc5c", 1.0, "Moderate (11-40)"),
            (41, 80, "#fd8d3c", 1.6, "High (41-80)"),
            (81, 150, "#f03b20", 2.2, "Very High (81-150)"),
            (151, 9999, "#bd0026", 3.0, "Major Corridor (150+)")
        ]

        for low, high, color, width, label in styles:
            symbol = QgsLineSymbol.createSimple({
                'color': color,
                'width': str(width),
                'line_style': 'solid'
            })
            my_range.append(QgsRendererRange(low, high, symbol, label))

        renderer = QgsGraduatedSymbolRenderer('frequency', my_range)
        heatmap_layer.setRenderer(renderer)
        QgsProject.instance().addMapLayer(heatmap_layer)
        return heatmap_layer

    @staticmethod
    def create_network_isochrones(
            road_layer: QgsVectorLayer,
            stops_layer: QgsVectorLayer,
            distance: float):
        """Generates a network-based reach layer using QGIS processing."""
        import processing

        # We'll use 'native:serviceareafrompoints'
        # It calculates the part of the network reachable within a certain cost
        params = {
            'INPUT': road_layer,
            'START_POINTS': stops_layer,
            'STRATEGY': 0,  # Shortest
            'DIRECTION_FIELD': '',
            'VALUE_BACKWARD': '',
            'VALUE_FORWARD': '',
            'VALUE_BOTH': '',
            'DEFAULT_DIRECTION': 2,
            'DEFAULT_SPEED': 5,
            'TOLERANCE': 10,
            'TRAVEL_COST': distance,
            'OUTPUT': 'memory:ServiceArea'
        }
        # Try to find the correct algorithm ID dynamically
        all_algs = [alg.id() for alg in QgsApplication.processingRegistry().algorithms()]
        target_alg = next((a for a in all_algs if "servicearea" in a.lower() and "layer" in a.lower()), None)

        if not target_alg:
            # Last ditch effort: fallback search
            possible_ids = ["native:servicearea_fromlayer", "qgis:servicearea_fromlayer", "native:serviceareafrompoints"]
            target_alg = next((a for a in possible_ids if a in all_algs), None)

        if not target_alg:
            raise Exception("No service area algorithm found in QGIS. Please check your Network Analysis provider.")

        try:
            result = processing.run(target_alg, params)
        except Exception as e:
            QgsMessageLog.logMessage(f"Service Area Failed with {target_alg}. Error: {str(e)}", "GTFS Plugin", Qgis.Critical)
            raise e

        output_layer = result['OUTPUT']

        # Add to project
        output_layer.setName(f"Network Reach ({int(distance)}m)")
        QgsProject.instance().addMapLayer(output_layer)
        # Uncheck visibility by default
        node = QgsProject.instance().layerTreeRoot().findLayer(output_layer.id())
        if node:
            node.setItemVisibilityChecked(False)

        # Simple styling: Red lines
        symbol = QgsLineSymbol.createSimple({'color': '#e31a1c', 'width': '0.4'})
        output_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        output_layer.triggerRepaint()

    @staticmethod
    def create_stop_layer(
            stops: Dict[str, Dict[str, Any]],
            stop_to_routes: Dict[str, Set[str]],
            stop_to_pf_routes: Dict[str, Set[str]],
            stop_route_counts: Dict[str, int],
            routes: Dict[str, Dict[str, Any]],
            stop_route_types: Dict[str, Set[str]],
            period: str = "All Periods") -> None:
        if not stops:
            return

        layer = QgsVectorLayer("Point?crs=epsg:4326", "Stops", "memory")
        pr = layer.dataProvider()

        pr.addAttributes([
            _build_field("stop_id", QVariant.String),
            _build_field("name", QVariant.String),
            _build_field("location_type", QVariant.String),
            _build_field("parent_station", QVariant.String),
            _build_field("stop_code", QVariant.String),
            _build_field("platform", QVariant.String),
            _build_field("routes", QVariant.String),
            _build_field("is_terminal", QVariant.String),
            _build_field("terminal_routes", QVariant.String),
            _build_field("stop_desc", QVariant.String),
            _build_field("lat", QVariant.Double),
            _build_field("lon", QVariant.Double),
            _build_field("lines_count", QVariant.Int),
            _build_field("all_transit_types", QVariant.String),
            _build_field("most_frequent_type", QVariant.Int)
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

            # Transit Types
            r_types = stop_route_types.get(stop_id, set())
            r_types_list = sorted(list(r_types))
            r_types_str = ", ".join(r_types_list)

            # Primary transit type for icon (priority: Subway > Rail > Tram > Ferry > Bus)
            primary_type = 3  # Default Bus
            if r_types:
                # Basic GTFS types priority
                priority = {'1': 1, '2': 2, '0': 10, '4': 20, '3': 30}
                sorted_by_pri = sorted(list(r_types), key=lambda x: priority.get(x, 100))
                primary_type = int(sorted_by_pri[0])

            feat.setAttributes([
                stop_id,
                s['name'],
                s.get('location_type', ''),
                s.get('parent_station', ''),
                s.get('stop_code', ''),
                s.get('platform_code', ''),
                route_names_str,
                is_pf,
                pf_route_names_str,
                s.get('stop_desc', ''),
                s['lat'],
                s['lon'],
                stop_route_counts.get(stop_id, 0),
                r_types_str,
                primary_type
            ])
            features.append(feat)

        pr.addFeatures(features)
        layer.updateExtents()

        # Styling - Rule Based Symbology with Layered Markers (Circle + Emoji)
        def create_layered_symbol(color, char):
            symbol = QgsMarkerSymbol()
            # 1. Background Circle
            bg_layer = QgsSimpleMarkerSymbolLayer()
            bg_layer.setShape(QgsSimpleMarkerSymbolLayer.Circle)
            bg_layer.setColor(QtGui.QColor(color))
            no_pen = getattr(QtCore.Qt, "NoPen", QtCore.Qt.PenStyle.NoPen)
            bg_layer.setStrokeStyle(no_pen)
            bg_layer.setSize(3)
            symbol.changeSymbolLayer(0, bg_layer)
            # 2. Foreground Emoji
            fg_layer = QgsFontMarkerSymbolLayer()
            fg_layer.setFontFamily('Arial')  # Avoid system-specific font mapping issues
            fg_layer.setCharacter(char)
            fg_layer.setColor(QtGui.QColor(255, 255, 255))
            fg_layer.setSize(2.2)
            symbol.appendSymbolLayer(fg_layer)
            return symbol

        # Categories based on GTFS Extended Route Types
        # Priority: Subway > Rail > Tram > Ferry > Bus
        present_types = set()
        for stop_id, s_types in stop_route_types.items():
            if not s_types:
                continue
            priority = {'1': 1, '2': 2, '0': 10, '4': 20, '3': 30, '200': 30}  # Note: 200 grouped with Bus priority
            sorted_by_pri = sorted(list(s_types), key=lambda x: priority.get(x, 100))
            p_type = sorted_by_pri[0]
            # Convert extended to base types for rule matching if needed
            if 100 <= int(p_type) < 200:
                p_type = '100'  # Rail
            elif 200 <= int(p_type) < 300:
                p_type = '3'  # Coach as Bus
            elif 900 <= int(p_type) < 1000:
                p_type = '0'  # Tram
            elif 700 <= int(p_type) < 900:
                p_type = '3'  # Bus
            elif 1000 <= int(p_type) < 1100:
                p_type = '4'  # Ferry
            present_types.add(p_type)

        rules = [
            # (Label, Expression, Color, Emoji, TypeID)
            # (Label, Expression, Color, Emoji, TypeID)
            ('Subway', '"most_frequent_type" = 1', '#FF0000', '🚇', '1'),
            ('Rail', '("most_frequent_type" = 2 OR ("most_frequent_type" >= 100 AND "most_frequent_type" < 200))', '#FF8C00', '🚄', '100'),
            ('Tram', '("most_frequent_type" = 0 OR ("most_frequent_type" >= 900 AND "most_frequent_type" < 1000))', '#32CD32', '🚃', '0'),
            ('Bus', '("most_frequent_type" = 3 OR ("most_frequent_type" >= 200 AND "most_frequent_type" < 300) OR ("most_frequent_type" >= 700 AND "most_frequent_type" < 900))', '#1E90FF', '🚌', '3'),
            ('Ferry', '("most_frequent_type" = 4 OR ("most_frequent_type" >= 1000 AND "most_frequent_type" < 1100))', '#00CED1', '⛴️', '4')
        ]

        root_rule = QgsRuleBasedRenderer.Rule(None)

        # Only add rules that are present in the data
        for label, exp, color, char, tid in rules:
            if tid in present_types:
                rule = QgsRuleBasedRenderer.Rule(create_layered_symbol(color, char), label=label, filterExp=exp)
                root_rule.appendChild(rule)

        # Default rule if nothing matches or others exist
        default_rule = QgsRuleBasedRenderer.Rule(create_layered_symbol('#808080', '🚏'), label='Other', filterExp='ELSE')
        root_rule.appendChild(default_rule)

        layer.setRenderer(QgsRuleBasedRenderer(root_rule))

        # Labeling
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = "name"
        text_format = QgsTextFormat()
        text_format.setSize(8)
        label_settings.setFormat(text_format)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        layer.setDisplayExpression("name")

        QgsProject.instance().addMapLayer(layer)
        return layer

    @staticmethod
    def create_walking_reach(stop_layer: QgsVectorLayer) -> Optional[QgsVectorLayer]:
        """Creates a 400m buffer using native:buffer for maximum reliability."""
        if not stop_layer or stop_layer.featureCount() == 0:
            return None

        import processing
        params = {
            'INPUT': stop_layer,
            'DISTANCE': 0.0036,  # ~400m in degrees for 4326
            'SEGMENTS': 25,
            'END_CAP_STYLE': 0,  # Round
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'DISSOLVE': False,
            'OUTPUT': 'memory:Walking Reach'
        }

        try:
            result = processing.run("native:buffer", params)
            reach_layer = result['OUTPUT']

            # Styling: Semi-transparent blue
            symbol = QgsFillSymbol.createSimple({'color': '0,0,255,40', 'outline_color': 'blue'})
            reach_layer.renderer().setSymbol(symbol)
            reach_layer.setOpacity(0.5)

            QgsProject.instance().addMapLayer(reach_layer)
            # Uncheck visibility by default
            node = QgsProject.instance().layerTreeRoot().findLayer(reach_layer.id())
            if node:
                node.setItemVisibilityChecked(False)
            QgsMessageLog.logMessage("Walking Reach created via native:buffer.", "GTFS Plugin", Qgis.Info)
            return reach_layer
        except Exception as e:
            QgsMessageLog.logMessage(f"Walking Reach Failed: {str(e)}", "GTFS Plugin", Qgis.Critical)
            return None

    @staticmethod
    def calculate_population_coverage(
            walking_layer: QgsVectorLayer,
            pop_layer: QgsVectorLayer,
            pop_field: str) -> float:
        """Calculates total population covered by walking reach and generates a % coverage map."""
        if not walking_layer or not pop_layer:
            return 0.0

        # Unified walking geometry
        walking_geoms = [f.geometry() for f in walking_layer.getFeatures()]
        unified_walking = QgsGeometry.unaryUnion(walking_geoms)

        # Ensure CRS compatibility
        if walking_layer.crs() != pop_layer.crs():
            transform = QgsCoordinateTransform(walking_layer.crs(), pop_layer.crs(), QgsProject.instance())
            unified_walking.transform(transform)

        if unified_walking.isEmpty():
            return 0.0

        # Create results layer
        result_layer = QgsVectorLayer(
            f"Polygon?crs={pop_layer.crs().authid()}",
            "Population Coverage Map",
            "memory"
        )
        pr = result_layer.dataProvider()
        fields = pop_layer.fields()
        fields.append(_build_field("pct_covered", QVariant.Double))
        pr.addAttributes(fields)
        result_layer.updateFields()

        total_pop = 0.0
        features_to_add = []

        # Map fields (case-insensitive)
        actual_pop_field = next((f.name() for f in pop_layer.fields() if f.name().lower() == pop_field.lower()), pop_field)

        for pop_feat in pop_layer.getFeatures():
            geom = pop_feat.geometry()
            new_feat = QgsFeature(pop_feat)
            new_feat.setFields(result_layer.fields())

            if not geom or geom.isEmpty() or not geom.intersects(unified_walking):
                new_feat.setAttribute("pct_covered", 0.0)
                features_to_add.append(new_feat)
                continue

            intersection = geom.intersection(unified_walking)
            if intersection.isEmpty():
                new_feat.setAttribute("pct_covered", 0.0)
                features_to_add.append(new_feat)
                continue

            # Area-based ratio
            ratio = intersection.area() / geom.area() if geom.area() > 0 else 0.0
            pct = ratio * 100.0

            try:
                val_attr = pop_feat.attribute(actual_pop_field)
                pop_val = float(val_attr) if val_attr is not None else 0.0
                total_pop += pop_val * ratio
            except (ValueError, TypeError):
                pass

            new_feat.setAttribute("pct_covered", min(100.0, pct))
            features_to_add.append(new_feat)

        pr.addFeatures(features_to_add)
        result_layer.updateExtents()

        # Styling: Light to Dark Purple
        my_range = []
        symbol = QgsFillSymbol.createSimple({'color': '#f2f0f7', 'outline_color': 'gray'})
        my_range.append(QgsRendererRange(0.0, 0.0, symbol, '0%'))

        symbol = QgsFillSymbol.createSimple({'color': '#cbc9e2', 'outline_color': 'gray'})
        my_range.append(QgsRendererRange(0.1, 25.0, symbol, '1-25%'))

        symbol = QgsFillSymbol.createSimple({'color': '#9e9ac8', 'outline_color': 'gray'})
        my_range.append(QgsRendererRange(25.1, 50.0, symbol, '25-50%'))

        symbol = QgsFillSymbol.createSimple({'color': '#756bb1', 'outline_color': 'gray'})
        my_range.append(QgsRendererRange(50.1, 75.0, symbol, '50-75%'))

        symbol = QgsFillSymbol.createSimple({'color': '#54278f', 'outline_color': 'gray'})
        my_range.append(QgsRendererRange(75.1, 100.0, symbol, '75-100%'))

        renderer = QgsGraduatedSymbolRenderer('pct_covered', my_range)
        result_layer.setRenderer(renderer)

        QgsProject.instance().addMapLayer(result_layer)
        return total_pop

    @staticmethod
    def create_transit_deserts_layer(
            walking_layer: QgsVectorLayer,
            pop_layer: QgsVectorLayer,
            pop_field: str) -> Optional[QgsVectorLayer]:
        """Creates a layer highlighting areas with population but no walking reach coverage."""
        if not walking_layer or not pop_layer:
            return None

        # Create memory layer
        desert_layer = QgsVectorLayer(
            f"Polygon?crs={pop_layer.crs().authid()}",
            "Transit Deserts",
            "memory"
        )
        pr = desert_layer.dataProvider()

        # Copy fields from pop_layer
        pr.addAttributes(pop_layer.fields())
        desert_layer.updateFields()

        # Get unified walking geometry
        walking_geoms = [f.geometry() for f in walking_layer.getFeatures()]
        unified_walking = QgsGeometry.unaryUnion(walking_geoms)

        # Ensure CRS compatibility
        if walking_layer.crs() != pop_layer.crs():
            transform = QgsCoordinateTransform(walking_layer.crs(), pop_layer.crs(), QgsProject.instance())
            unified_walking.transform(transform)

        features_to_add = []
        for pop_feat in pop_layer.getFeatures():
            geom = pop_feat.geometry()
            # If the census tract is NOT covered by walking reach
            # and has population > 0
            if not geom.intersects(unified_walking):
                pop_val = 0
                try:
                    pop_val = float(pop_feat.attribute(pop_field))
                except (ValueError, TypeError):
                    pass

                if pop_val > 0:
                    features_to_add.append(pop_feat)
            else:
                # Partial coverage check: if intersection area < 10% of total area
                intersection = geom.intersection(unified_walking)
                if intersection.area() < geom.area() * 0.1:
                    pop_val = 0
                    try:
                        pop_val = float(pop_feat.attribute(pop_field))
                    except (ValueError, TypeError):
                        pass
                    if pop_val > 0:
                        features_to_add.append(pop_feat)

        pr.addFeatures(features_to_add)
        desert_layer.updateExtents()

        # Style: Semi-transparent Red
        symbol = QgsFillSymbol.createSimple({'color': '255,0,0,100', 'outline_color': 'red'})
        desert_layer.renderer().setSymbol(symbol)

        QgsProject.instance().addMapLayer(desert_layer)
        return desert_layer
