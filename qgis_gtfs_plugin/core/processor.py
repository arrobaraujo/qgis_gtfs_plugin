# -*- coding: utf-8 -*-

import io
import csv
import zipfile
from typing import Dict, List, Tuple, Set, Any, Optional

try:
    from qgis.core import QgsDistanceArea, QgsPointXY, QgsRectangle, QgsGeometry
except ImportError:
    pass


class GTFSProcessor:
    """Handles the parsing and processing of GTFS files from a ZIP archive."""

    def __init__(self, zip_path: str):
        self.zip_path = zip_path
        self.agencies: Dict[str, Dict[str, str]] = {}
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.fares: Dict[str, str] = {}
        self.route_to_price: Dict[str, str] = {}
        self.trips: List[Dict[str, Any]] = []
        self.shapes: Dict[str, List[Dict[str, Any]]] = {}
        self.stops: Dict[str, Dict[str, Any]] = {}
        self.stop_to_routes: Dict[str, Set[str]] = {}
        self.stop_to_pf_routes: Dict[str, Set[str]] = {}
        self.shape_frequencies: Dict[str, int] = {}
        self.shape_time_ranges: Dict[str, Tuple[str, str]] = {}
        self.stop_route_counts: Dict[str, int] = {}
        self.stop_route_types: Dict[str, Set[str]] = {}
        self.service_to_days: Dict[str, List[int]] = {}
        self.shape_lengths: Dict[str, float] = {}

    def process(self, service_day='All'):
        with zipfile.ZipFile(self.zip_path, 'r') as z:
            files = z.namelist()
            self._parse_agency(z, files)
            self._parse_calendar(z, files)
            self._parse_routes(z, files)
            self._parse_fares(z, files)
            self._parse_trips(z, files, service_day)
            self._parse_shapes(z, files)
            self._parse_stops(z, files)
            self._parse_stop_times(z, files)

    def _parse_agency(self, z, files):
        if 'agency.txt' in files:
            with z.open('agency.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    aid = row.get('agency_id', 'default')
                    name = row.get('agency_name') or row.get('agency_id') or aid
                    self.agencies[aid] = {'name': name}

    def _parse_calendar(self, z, files):
        if 'calendar.txt' in files:
            with z.open('calendar.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    sid = row['service_id']
                    days = []
                    if row.get('monday') == '1':
                        days.append(0)
                    if row.get('tuesday') == '1':
                        days.append(1)
                    if row.get('wednesday') == '1':
                        days.append(2)
                    if row.get('thursday') == '1':
                        days.append(3)
                    if row.get('friday') == '1':
                        days.append(4)
                    if row.get('saturday') == '1':
                        days.append(5)
                    if row.get('sunday') == '1':
                        days.append(6)
                    self.service_to_days[sid] = days

    def _parse_routes(self, z, files):
        if 'routes.txt' in files:
            with z.open('routes.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    rid = row.get('route_id')
                    if not rid:
                        continue
                    self.routes[rid] = {
                        'short_name': row.get('route_short_name', ''),
                        'long_name': row.get('route_long_name', ''),
                        'desc': row.get('route_desc', ''),
                        'agency_id': row.get('agency_id', 'default'),
                        'type': row.get('route_type', '3'),
                        'color': row.get('route_color', '000000')
                    }

    def _parse_fares(self, z, files):
        if 'fare_attributes.txt' in files:
            with z.open('fare_attributes.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    self.fares[row['fare_id']] = row.get('price', '0.00')
        if 'fare_rules.txt' in files:
            with z.open('fare_rules.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    rid = row['route_id']
                    fid = row['fare_id']
                    if fid in self.fares and rid not in self.route_to_price:
                        self.route_to_price[rid] = self.fares[fid]

    def _parse_trips(self, z, files, service_day='All'):
        if 'trips.txt' in files:
            with z.open('trips.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    sid = row['service_id']
                    if service_day != 'All':
                        days = self.service_to_days.get(sid, [])
                        if service_day == 'Weekday' and not any(d < 5 for d in days):
                            continue
                        if service_day == 'Saturday' and 5 not in days:
                            continue
                        if service_day == 'Sunday' and 6 not in days:
                            continue
                    self.trips.append({
                        'trip_id': row['trip_id'],
                        'route_id': row['route_id'],
                        'shape_id': row.get('shape_id', ''),
                        'direction': row.get('direction_id', ''),
                        'headsign': row.get('trip_headsign', ''),
                        'short_name': row.get('trip_short_name', '')
                    })
                    shape_id = row.get('shape_id', '')
                    if shape_id:
                        self.shape_frequencies[shape_id] = self.shape_frequencies.get(shape_id, 0) + 1

    def _parse_shapes(self, z, files):
        if 'shapes.txt' in files:
            with z.open('shapes.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    sid = row['shape_id']
                    if sid not in self.shapes:
                        self.shapes[sid] = []
                    self.shapes[sid].append({
                        'lat': float(row['shape_pt_lat']),
                        'lon': float(row['shape_pt_lon']),
                        'seq': int(row['shape_pt_sequence'])
                    })
            da = QgsDistanceArea()
            da.setEllipsoid('WGS84')
            for sid, points in self.shapes.items():
                sorted_pts = sorted(points, key=lambda x: x['seq'])
                dist = 0
                for i in range(len(sorted_pts)-1):
                    p1 = QgsPointXY(sorted_pts[i]['lon'], sorted_pts[i]['lat'])
                    p2 = QgsPointXY(sorted_pts[i+1]['lon'], sorted_pts[i+1]['lat'])
                    dist += da.measureLine(p1, p2)
                self.shape_lengths[sid] = dist / 1000.0

    def _parse_stops(self, z, files):
        if 'stops.txt' in files:
            with z.open('stops.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    sid = row.get('stop_id')
                    if not sid:
                        continue
                    try:
                        self.stops[sid] = {
                            'name': row.get('stop_name', sid),
                            'lat': float(row['stop_lat']),
                            'lon': float(row['stop_lon']),
                            'location_type': row.get('location_type', '0'),
                            'parent_station': row.get('parent_station', ''),
                            'stop_code': row.get('stop_code', ''),
                            'platform_code': row.get('platform_code', ''),
                            'stop_desc': row.get('stop_desc', '')
                        }
                    except (KeyError, ValueError):
                        continue

    def _parse_stop_times(self, z, files):
        trip_last_stop = {}
        trip_times = {}
        trip_to_route = {t['trip_id']: t['route_id'] for t in self.trips}
        trip_to_shape = {t['trip_id']: t['shape_id'] for t in self.trips}
        if 'stop_times.txt' in files:
            with z.open('stop_times.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    tid, sid, seq = row['trip_id'], row['stop_id'], int(row['stop_sequence'])
                    arr, dep = row.get('arrival_time', ''), row.get('departure_time', '')
                    if tid not in trip_times:
                        trip_times[tid] = []
                    if arr:
                        trip_times[tid].append(arr)
                    if dep:
                        trip_times[tid].append(dep)
                    rid = trip_to_route.get(tid)
                    if rid:
                        if sid not in self.stop_to_routes:
                            self.stop_to_routes[sid] = set()
                        self.stop_to_routes[sid].add(rid)
                        rtype = self.routes.get(rid, {}).get('type', '3')
                        if sid not in self.stop_route_types:
                            self.stop_route_types[sid] = set()
                        self.stop_route_types[sid].add(rtype)
                        if tid not in trip_last_stop or seq > trip_last_stop[tid][1]:
                            trip_last_stop[tid] = (sid, seq)
            for tid, times in trip_times.items():
                if not times:
                    continue
                sid = trip_to_shape.get(tid)
                if sid:
                    if sid not in self.shape_time_ranges:
                        self.shape_time_ranges[sid] = (min(times), max(times))
                    else:
                        cmin, cmax = self.shape_time_ranges[sid]
                        self.shape_time_ranges[sid] = (min(cmin, min(times)), max(cmax, max(times)))
            for sid, rids in self.stop_to_routes.items():
                self.stop_route_counts[sid] = len(rids)
            for tid, (sid, _) in trip_last_stop.items():
                rid = trip_to_route.get(tid)
                if rid:
                    if sid not in self.stop_to_pf_routes:
                        self.stop_to_pf_routes[sid] = set()
                    self.stop_to_pf_routes[sid].add(rid)

    def get_stats(self) -> Dict[str, Any]:
        total_km = sum(self.shape_lengths.get(sid, 0) * freq for sid, freq in self.shape_frequencies.items())
        agency_trips = {}
        agencies_found = set()
        for trip in self.trips:
            rid = trip['route_id']
            aid = self.routes.get(rid, {}).get('agency_id') or 'default'
            aname = self.agencies.get(aid, {}).get('name', aid)
            agency_trips[aname] = agency_trips.get(aname, 0) + 1
            agencies_found.add(aid)
        avg_len = sum(self.shape_lengths.values()) / len(self.shape_lengths) if self.shape_lengths else 0
        area_km2 = 0
        if self.stops:
            lats, lons = [s['lat'] for s in self.stops.values()], [s['lon'] for s in self.stops.values()]
            rect = QgsRectangle(min(lons), min(lats), max(lons), max(lats))
            da = QgsDistanceArea()
            da.setEllipsoid('WGS84')
            area_km2 = da.measureArea(QgsGeometry.fromRect(rect)) / 1e6
        return {
            'total_km': total_km,
            'stop_density': len(self.stops) / area_km2 if area_km2 > 0 else 0,
            'routes_count': len(self.routes),
            'trips_count': len(self.trips),
            'avg_shape_len': avg_len,
            'agencies_count': len(agencies_found),
            'stops_count': len(self.stops),
            'area_km2': area_km2,
            'agency_trips': agency_trips
        }
