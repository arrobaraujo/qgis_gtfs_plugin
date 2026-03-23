# -*- coding: utf-8 -*-

import csv
import io
import zipfile
from typing import Dict, List, Set, Tuple, Optional, Any

class GTFSProcessor:
    """Handles the parsing and processing of GTFS files from a ZIP archive."""

    def __init__(self, zip_path: str):
        self.zip_path = zip_path
        self.agencies: Dict[str, str] = {}
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.fares: Dict[str, str] = {}
        self.route_to_price: Dict[str, str] = {}
        self.trips: List[Dict[str, Any]] = []
        self.shapes: Dict[str, List[Dict[str, Any]]] = {}
        self.stops: Dict[str, Dict[str, Any]] = {}
        self.stop_to_routes: Dict[str, Set[str]] = {}
        self.stop_to_pf_routes: Dict[str, Set[str]] = {}

    def process(self):
        """Main method to parse all relevant GTFS files."""
        with zipfile.ZipFile(self.zip_path, 'r') as z:
            files = z.namelist()
            
            self._parse_agency(z, files)
            self._parse_routes(z, files)
            self._parse_fares(z, files)
            self._parse_trips(z, files)
            self._parse_shapes(z, files)
            self._parse_stops(z, files)
            self._parse_stop_times(z, files)

    def _parse_agency(self, z, files):
        if 'agency.txt' in files:
            with z.open('agency.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    aid = row.get('agency_id', '')
                    self.agencies[aid] = row['agency_name']
                    if not aid:
                        self.agencies['DEFAULT'] = row['agency_name']

    def _parse_routes(self, z, files):
        if 'routes.txt' in files:
            with z.open('routes.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    self.routes[row['route_id']] = {
                        'short_name': row.get('route_short_name', ''),
                        'long_name': row.get('route_long_name', ''),
                        'desc': row.get('route_desc', ''),
                        'agency_id': row.get('agency_id', ''),
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

    def _parse_trips(self, z, files):
        if 'trips.txt' in files:
            with z.open('trips.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    self.trips.append({
                        'trip_id': row['trip_id'],
                        'route_id': row['route_id'],
                        'shape_id': row.get('shape_id', ''),
                        'headsign': row.get('trip_headsign', ''),
                        'short_name': row.get('trip_short_name', ''),
                        'direction': row.get('direction_id', '')
                    })

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

    def _parse_stops(self, z, files):
        if 'stops.txt' in files:
            with z.open('stops.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    stop_id = row['stop_id']
                    self.stops[stop_id] = {
                        'name': row.get('stop_name', stop_id),
                        'lat': float(row['stop_lat']),
                        'lon': float(row['stop_lon']),
                        'location_type': row.get('location_type', '0'),
                        'parent_station': row.get('parent_station', ''),
                        'stop_code': row.get('stop_code', ''),
                        'platform_code': row.get('platform_code', ''),
                        'stop_desc': row.get('stop_desc', '')
                    }

    def _parse_stop_times(self, z, files):
        trip_last_stop: Dict[str, Tuple[str, int]] = {}
        trip_to_route = {t['trip_id']: t['route_id'] for t in self.trips}
        
        if 'stop_times.txt' in files:
            with z.open('stop_times.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for row in reader:
                    tid = row['trip_id']
                    sid = row['stop_id']
                    seq = int(row.get('stop_sequence', '0'))
                    
                    rid = trip_to_route.get(tid)
                    if rid:
                        if sid not in self.stop_to_routes:
                            self.stop_to_routes[sid] = set()
                        self.stop_to_routes[sid].add(rid)
                        
                        if tid not in trip_last_stop or seq > trip_last_stop[tid][1]:
                            trip_last_stop[tid] = (sid, seq)

            for tid, (sid, seq) in trip_last_stop.items():
                rid = trip_to_route.get(tid)
                if rid:
                    if sid not in self.stop_to_pf_routes:
                        self.stop_to_pf_routes[sid] = set()
                    self.stop_to_pf_routes[sid].add(rid)
