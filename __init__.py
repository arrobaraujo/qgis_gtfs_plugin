# -*- coding: utf-8 -*-

def classFactory(iface):
    from .gtfs_loader import GTFSLoader
    return GTFSLoader(iface)
