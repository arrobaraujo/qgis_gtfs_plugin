# -*- coding: utf-8 -*-

import os
# Force pure-Python implementation to avoid "Descriptors cannot be created directly" error in newer protobuf versions
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import urllib.request
from typing import List, Dict, Any
try:
    from .vendor.gtfs_realtime_pb2 import FeedMessage
    HAS_PROTOBUF = True
except (ImportError, ModuleNotFoundError):
    HAS_PROTOBUF = False

class GTFSRTProcessor:
    """Handles fetching and parsing of GTFS Realtime feeds."""

    def __init__(self, url: str):
        self.url = url

    def fetch_vehicle_positions(self) -> List[Dict[str, Any]]:
        """
        Fetches the GTFS-RT feed and extracts vehicle positions.
        Returns a list of dictionaries with vehicle data.
        """
        if not HAS_PROTOBUF:
            raise Exception("O pacote 'protobuf' não está instalado no QGIS. Por favor, instale-o para usar o tempo real.")

        vehicles = []
        try:
            # 1. Fetch the raw binary data
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(self.url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                binary_data = response.read()

            # 2. Parse using Protobuf
            feed = FeedMessage()
            feed.ParseFromString(binary_data)

            # 3. Extract entities
            for entity in feed.entity:
                if entity.HasField('vehicle'):
                    v = entity.vehicle
                    pos = v.position
                    
                    vehicle_data = {
                        'vehicle_id': v.vehicle.id if v.HasField('vehicle') else entity.id,
                        'trip_id': v.trip.trip_id if v.HasField('trip') else '',
                        'route_id': v.trip.route_id if v.HasField('trip') else '',
                        'lat': pos.latitude,
                        'lon': pos.longitude,
                        'bearing': pos.bearing if pos.HasField('bearing') else 0.0,
                        'speed': pos.speed if pos.HasField('speed') else 0.0,
                        'timestamp': v.timestamp if v.HasField('timestamp') else 0
                    }
                    vehicles.append(vehicle_data)
                    
        except Exception as e:
            # Re-raise to be caught by the manager
            raise Exception(f"Failed to fetch GTFS-RT: {str(e)}")

        return vehicles
